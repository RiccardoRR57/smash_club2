from django.views.generic import ListView, CreateView, DetailView, DeleteView, TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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

## bookings management views

class BookingCreateView(LoginRequiredMixin, CreateView):
    title = 'Create Booking'
    template_name = 'booking_form.html'
    success_url = reverse_lazy('booking:my_bookings')
    form_class = CreateBookingForm

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
                initial['start_time'] = f"{date} {hour}:00"
            except Court.DoesNotExist:
                print(f"Invalid court ID: {court_id}")  # Handle invalid court_id gracefully
        return initial

    def form_valid(self, form):
        # Save the booking instance
        form.instance.user = self.request.user
        booking = form.save()

        # Save invited players
        invited_players = form.cleaned_data.get('invited_players', [])
        for player in invited_players:
            booking.invite_player(player)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Booking'
        return context

class BookingDeleteView(LoginRequiredMixin, DeleteView):
    model = Booking
    template_name = 'booking_delete.html'
    context_object_name = 'booking'
    success_url = reverse_lazy('booking:my_bookings')

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

class InvitationCreateView(LoginRequiredMixin, CreateView):
    title = 'Invite User'
    template_name = 'invite_user_form.html'
    success_url = reverse_lazy('booking:my_bookings')
    form_class = CreateInvitationForm

    def get_form_kwargs(self):
        """Pass the logged-in user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['exclude_users'] = [self.request.user]  # Pass the logged-in user
        return kwargs

    def form_valid(self, form):
        booking_id = self.kwargs.get('booking_id')
        booking = Booking.objects.get(id=booking_id)
        form.instance.booking = booking
        form.instance.inviter = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Invite User'
        return context
    
## teacher exclusive views



class TeacherDashboardView(LoginRequiredMixin, CreateView):
    title = 'Create Recurring Booking'
    template_name = 'teacher_dashboard.html'
    success_url = reverse_lazy('booking:my_bookings')
    form_class = RecurringBookingForm

    def form_valid(self, form):
        # Save the booking instance
        form.instance.user = self.request.user
        form.instance.until = form.cleaned_data.get('until')
        start_time = form.instance.start_time
        invited_players = form.cleaned_data.get('invited_players', [])

        with transaction.atomic():
            while start_time.date() <= form.instance.until:
                # Create a new Booking instance for each week
                booking = Booking()
                booking.court = form.instance.court
                booking.start_time = start_time
                booking.user = self.request.user

                booking.save()


                # Save invited players for this booking
                for player in invited_players:
                    booking.invite_player(player)

                # Move to the next week
                start_time += timedelta(weeks=1)

        return HttpResponseRedirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Teacher Dashboard'
        return context

## admin exclusive views
def admin_dashboard(request):
    context = {
        'title': 'Admin Dashboard', 
    }
    return render(request, 'admin_dashboard.html', context)