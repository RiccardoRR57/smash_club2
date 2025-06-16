from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from . import views 

app_name = 'booking'

urlpatterns = [
    path('courts/', views.CourtListView.as_view(), name='court_list'),
    path('courts/<int:pk>/', views.CourtDetailView.as_view(), name='court_detail'),

    #path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('', views.calendar_view, name='booking_calendar'),
    path('delete/<int:pk>/', views.BookingDeleteView.as_view(), name='booking_delete'),
    path('my-bookings/', views.MyBookingsView.as_view(), name='my_bookings'),

    path('invitation_accept/<int:pk>/', views.accept_invitation, name='invitation_accept'),
    path('invitation_decline/<int:pk>/', views.decline_invitation, name='invitation_decline'),
    path('invite_user/<int:booking_id>/', views.invite_user, name='invite_user'),

    path('recurring_booking/', views.CreateRecurringBookingView.as_view(), name='recurring_booking'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_court/', views.CreateCourtView.as_view(), name='add_court'),
    path('set_teachers/', views.assign_teacher, name='assign_teacher'),

    path('select-player/', views.select_player, name='select_player'),
]
