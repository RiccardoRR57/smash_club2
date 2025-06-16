from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin 
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from django.urls import reverse_lazy
from django.db import transaction
from datetime import timedelta, datetime
from .models import *
from .forms import *
from django.utils import timezone


## courts management views

class CourtListView(ListView):
    model = Court
    template_name = 'court_list.html'
    context_object_name = 'courts'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Courts'
        return context

class CourtDetailView(DetailView):
    model = Court
    template_name = 'court_detail.html'
    context_object_name = 'court'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Court Details'

        bookings = Booking.objects.filter(court=self.object).filter(start_time__gte=now()).order_by('start_time')
        context['bookings'] = bookings
        return context

class CreateCourtView(SuperuserRequiredMixin, CreateView):
    model = Court
    template_name = 'court_form.html'
    success_url = reverse_lazy('booking:court_list')
    form_class = CreateCourtForm

    def get_success_url(self):
        return super().get_success_url() + '?court_added=true'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Court'
        return context

## bookings management views

class BookingCreateView(LoginRequiredMixin, CreateView):
    title = 'Create Booking'
    template_name = 'booking_form.html'
    success_url = reverse_lazy('booking:my_bookings')
    form_class = CreateBookingForm

    def get_success_url(self):
        url = super().get_success_url()
        return f"{url}?b_added=true"

    def get_initial(self):
        """Pre-fill the form fields based on GET parameters."""
        initial = super().get_initial()
        court_id = self.request.GET.get('court_id')
        date = self.request.GET.get('date')
        hour = self.request.GET.get('hour')

        if court_id and date and hour:
            try:
                court = Court.objects.get(id=court_id)
                initial['court'] = court
                initial['date'] = datetime.strptime(date, '%Y-%m-%d').date()  # Convert string to date
                initial['hour'] = int(hour)  # Convert string to integer
            except Court.DoesNotExist:
                print(f"Invalid court ID: {court_id}")  # Handle invalid court_id gracefully
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        date = form.cleaned_data.get('date')  # Get the selected date
        hour = int(form.cleaned_data.get('hour'))  # Get the selected hour

        # Construct the start_time dynamically using the selected date and hour
        naive_start_time = datetime.combine(date, datetime.min.time()).replace(hour=hour)
        start_time = timezone.make_aware(naive_start_time)

        form.instance.start_time = start_time
        form.instance.end_time = start_time + timedelta(hours=1)
        form.instance.cancellable_until = start_time - timedelta(days=1)

        # Save the booking
        booking = form.save()

        # Save invited players for this booking
        invited_players = form.cleaned_data.get('invited_players', [])
        for player in invited_players:
            booking.invite_player(player)

        return HttpResponseRedirect(self.success_url+ '?b_added=true')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Booking'
        return context

class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'booking_delete.html'
    context_object_name = 'booking'
    success_url = reverse_lazy('booking:my_bookings')

    def get_success_url(self):
        url = super().get_success_url()
        return f"{url}?b_deleted=true"
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Booking'
        return context

def calendar_view(request):
    courts = Court.objects.all()
    today = now().date()
    current_hour = now().hour
    day_list = [today + timedelta(days=i) for i in range(7)]
    hours_list = range(8, 22)  # Hours from 8:00 to 21:00
    booked_data = {}
    past_hours = {}

    for court in courts:
        for day in day_list:
            day_str = day.isoformat()
            for hour in hours_list:
                hour_str = f"{hour:02d}"  # Format hour as two digits
                booking = Booking.objects.filter(
                    court=court,
                    start_time__date=day,
                    start_time__hour=hour
                ).first()
                key = f"{court.id}-{day_str}-{hour_str}"

                # Mark past hours using local time
                local_now = timezone.localtime(now())

                # Convert the day and hour to local datetime
                local_dt = timezone.make_aware(
                    datetime.combine(day, datetime.min.time()) + timedelta(hours=hour),
                    timezone.get_current_timezone()
                )

                if local_dt < local_now:
                    past_hours[key] = True
                else:
                    past_hours[key] = False

                booked_data[key] = booking

    context = {
        'title': 'Booking Calendar',
        'courts': courts,
        'day_list': day_list,
        'hours_list': hours_list,
        'booked_data': booked_data,
        'past_hours': past_hours,
        'now': now(),
    }
    return render(request, 'calendar_view.html', context)

class MyBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Bookings'

        past_bookings = self.get_queryset().filter(start_time__lt=now()).order_by('-start_time')
        context['past_bookings'] = past_bookings
        future_bookings = self.get_queryset().filter(start_time__gte=now()).order_by('start_time')
        context['future_bookings'] = future_bookings
        invitations = InvitedPlayer.objects.filter(user=self.request.user)

        context['invitations'] = invitations
        context['now'] = now()
        return context
    
## Invitations management views

@login_required
def accept_invitation(request, pk):
    invitation = InvitedPlayer.objects.get(pk=pk, user=request.user)
    invitation.status = 'accepted'
    invitation.save()
    return redirect('booking:my_bookings')

@login_required
def decline_invitation(request, pk):
    invitation = InvitedPlayer.objects.get(pk=pk, user=request.user)
    invitation.status = 'declined'
    invitation.save()
    return redirect('booking:my_bookings')


@login_required
def invite_user(request, booking_id):
    player_id = request.GET.get('player_id')  # Get the player ID from the URL

    if not player_id:
        # Redirect to the select_player page with the next parameter set to invite_user
        return redirect(f"{reverse_lazy('booking:select_player')}?next={reverse_lazy('booking:invite_user', kwargs={'booking_id': booking_id})}")

    booking = Booking.objects.get(id=booking_id)  # Get the booking by ID
    user = User.objects.get(id=player_id)  # Get the user by ID

    # Create an invitation for the selected user
    invitation = InvitedPlayer.objects.create(
        booking=booking,
        user=user,
        status='pending',
    )
    return redirect('booking:my_bookings')  # Redirect to the user's bookings page

## teacher exclusive views
class CreateRecurringBookingView(GroupRequiredMixin, CreateView):
    group_required = "teachers"
    title = 'Create Recurring Booking'
    template_name = 'create_recurring_booking.html'
    success_url = reverse_lazy('booking:my_bookings')
    form_class = RecurringBookingForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.until = form.cleaned_data.get('until')
        date = form.cleaned_data.get('date')  # Get the selected date
        hour = int(form.cleaned_data.get('hour'))  # Get the selected hour
        invited_players = form.cleaned_data.get('invited_players', [])

        # Use transaction.atomic to ensure all bookings are saved together
        with transaction.atomic():
            start_date = date
            until_date = form.instance.until

            while start_date <= until_date:
                # Construct the start_time dynamically using the selected date and hour
                naive_start_time = datetime.combine(start_date, datetime.min.time()).replace(hour=hour)
                start_time = timezone.make_aware(naive_start_time)

                # Create a new Booking instance for each week
                booking = Booking()
                booking.court = form.instance.court
                booking.user = form.instance.user
                booking.start_time = start_time
                booking.end_time = start_time + timedelta(hours=1)
                booking.cancellable_until = start_time - timedelta(days=1)

                print(f"Creating booking for {booking.court.name} by {booking.user.username} on {start_date} at {hour}:00")

                booking.save()

                # Save invited players for this booking
                for player in invited_players:
                    booking.invite_player(player)

                # Move to the next week
                start_date += timedelta(weeks=1)

        return HttpResponseRedirect(self.success_url + '?b_added=true')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Recurring Booking'
        return context

## admin exclusive views
@login_required
def dashboard(request):
    context = {
        'title': 'Dashboard', 
    }
    return render(request, 'dashboard.html', context)

@staff_member_required
def assign_teacher(request):
    player_id = request.GET.get('player_id')  # Get the player ID from the URL

    if not player_id:
        # Redirect to the select_player page with the next parameter set to assign_teacher
        return redirect(f"{reverse_lazy('booking:select_player')}?next={reverse_lazy('booking:assign_teacher')}")   

    user = User.objects.get(id=player_id)  # Get the user by ID
    teacher_group, created = Group.objects.get_or_create(name='teachers')  # Ensure the "teachers" group exists
    user.groups.add(teacher_group)  # Add the user to the "teachers" group
    return redirect(f"{reverse_lazy('booking:dashboard')}?teacher_added=true")  # Redirect to the dashboard or another page

@login_required
def select_player(request):
    query = request.GET.get('q', '')  # Get the search query from the request
    next_url = request.GET.get('next', reverse_lazy('booking:dashboard'))  # Get the next URL to redirect to after selection
    booking_id = request.GET.get('booking_id')
    players = User.objects.filter(groups__name='players')  # Filter users in the "Players" group

    if query:
        players = players.filter(username__icontains=query)  # Filter players by username

    context = {
        'title': 'Select Player',
        'players': players,
        'query': query,
        'next': next_url,  # Pass the next URL to the template
        'booking_id': booking_id,  # Pass the booking ID to the template if available
    }
    return render(request, 'select_player.html', context)