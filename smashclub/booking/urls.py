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
    path('invite_user/<int:booking_id>/', views.InvitationCreateView.as_view(), name='invite_user'),

    path('teacher_dashboard/', views.TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
