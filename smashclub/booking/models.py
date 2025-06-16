from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import localtime
from django.conf import settings

class Court(models.Model):
    name = models.CharField(max_length=100)

    SURFACE_CHOICES = (
        ('clay', 'Clay'),
        ('grass', 'Grass'),
        ('indoor_hard', 'Indoor Hard'),
        ('outdoor_hard', 'Outdoor Hard'),
        ('carpet', 'Carpet'),
        ('artificial_grass', 'Artificial Grass'),
    )
    surface = models.CharField(max_length=20, choices=SURFACE_CHOICES, default='indoor_hard')

    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    image = models.ImageField(upload_to='courts/', blank=False, null=False)

    def __str__(self):
        return f'{self.name} ({self.get_surface_display()})'



class Booking(models.Model):
    # Foreign key to the court being booked
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='bookings')
    # Foreign key to the user who made the booking
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')

    # Booking time details
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Field for cancellation logic (will be calculated automatically)
    cancellable_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        # Ensure no overlapping bookings for the same court
        constraints = [
            models.UniqueConstraint(fields=['court', 'start_time'], name='unique_booking_slot')
        ]
        # Order bookings by start time by default
        ordering = ['start_time']

    def invite_player(self, user):
        """Invite a player to this booking."""
        if self.invited_players.filter(user=user).exists():
            raise ValueError(f"{user.username} is already invited.")
        InvitedPlayer.objects.create(booking=self, user=user)

    def cancel_invitation(self, player):
        """Cancel an invitation for a player."""
        invitation = self.invited_players.filter(player=player).first()
        if invitation:
            invitation.delete()


    def save(self, *args, **kwargs):
        today = timezone.now()
        if( self.start_time < today):
            raise ValueError("Booking start time cannot be in the past.")
        if self.start_time.minute != 0 or self.start_time.second != 0:
            raise ValueError("Booking start time must be on the hour (e.g., 14:00, not 14:15).")
        if self.start_time.hour < 8 or self.start_time.hour > 21:
            raise ValueError("Bookings can only be made between 08:00 and 21:00.")
        if not (self.user.groups.filter(name='teachers').exists() or self.user.is_staff) and self.start_time > today + timedelta(days=7):
            raise ValueError("Bookings can only be made up to 7 days in advance for regular users.")

        self.start_time = self.start_time.replace(minute=0, second=0, microsecond=0)
        self.end_time = self.start_time + timedelta(hours=1)
        self.cancellable_until = self.start_time - timedelta(days=1)
        print(f"Booking created by {self.user.username} for court {self.court.name} from {self.start_time} to {self.end_time}. Cancellable until {self.cancellable_until}.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        now = timezone.now()
        if self.cancellable_until and now > self.cancellable_until and not (self.user.groups.filter(name='teachers').exists() or self.user.is_staff):
            raise ValueError("Cannot delete booking after the cancellable period has passed.")

        super().delete(*args, **kwargs)

    def __str__(self):
        local_start_time = localtime(self.start_time)
        local_end_time = localtime(self.end_time)
        return f"{self.court.name} by {self.user.username} on {local_start_time.strftime('%Y-%m-%d')} from {local_start_time.strftime('%H:%M')} to {local_end_time.strftime('%H:%M')}"

class InvitedPlayer(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='invited_players')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invited_players')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('declined', 'Declined'),
        ],
        default='pending'
    )
    invited_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only check on creation
            if self.booking.user == self.user:
                raise ValueError("You cannot invite yourself to your own booking.")
            if InvitedPlayer.objects.filter(booking=self.booking, user=self.user).exists():
                raise ValueError(f"{self.user.username} is already invited to this booking.")
        return super().save(*args, **kwargs)

    def __str__(self):
        local_start_time = localtime(self.booking.start_time)
        return f"{self.user.username} invited to {self.booking.court.name} on {local_start_time.strftime('%Y-%m-%d %H:%M')} by {self.booking.user.username}"