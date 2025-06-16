# Smash Club - Tennis Court Booking & Match Management System

A Django-based web application for managing tennis court bookings and live match tracking with real-time WebSocket support.

## Features

### 🎾 Court Management
- Multiple court types (Indoor Hard, Clay, Grass, Outdoor Hard ...)
- Court availability tracking
- Image support for courts

### 📅 Booking System
- Create individual bookings
- Recurring bookings for teachers
- Player invitation system
- Cancellation with 24-hour policy
- Real-time booking status updates

### 👥 User Management
- Role-based access (Players, Teachers, Admins)
- Player selection interface
- Teacher permission assignment
- Group-based permissions

### 🏆 Live Match Tracking
- Real-time score updates via WebSockets
- Tennis scoring system (sets, games, points)
- Best of 3 or 5 match formats
- Live match status
- Winner determination

## Technology Stack

- **Backend**: Django 4.x
- **Frontend**: Bootstrap 4, jQuery
- **Real-time**: Django Channels (WebSockets)
- **Database**: SQLite (development)
- **Forms**: Django Crispy Forms
- **Authentication**: Django built-in auth system

## Installation

1. **Clone the repository**
git clone <repository-url>
cd smash_club2/smashclub

2. **Create virtual environment with Pipenv**
pip install pipenv
pipenv shell

3. **Install dependencies with Pipenv**
pipenv install django
pipenv install django-crispy-forms
pipenv install channels
pipenv install pillow  # for image handling

5. **Run migrations**
python manage.py makemigrations
python manage.py migrate

6. **Create superuser**
python manage.py createsuperuser

7. **Create user groups**
python manage.py shell

from django.contrib.auth.models import Group
Group.objects.create(name='players')
Group.objects.create(name='teachers')

8. **Run the server**
python manage.py runserver

## Project Structure

<pre>
smashclub/
├── booking/                 # Booking management app
│   ├── models.py           # Court, Booking, InvitedPlayer models
│   ├── views.py            # Booking CRUD, player selection
│   ├── forms.py            # Booking forms with crispy forms
│   ├── urls.py             # Booking URL patterns
│   └── templates/          # Booking templates
├── matches/                # Match management app
│   ├── models.py           # Match model with scoring
│   ├── views.py            # Match CRUD and live updates
│   ├── consumers.py        # WebSocket consumers
│   └── templates/          # Match templates
├── static/                 # Static files (CSS, images)
├── templates/              # Base templates
├── media/                  # User uploaded files
└── smashclub/              # Main project settings
    ├── settings.py
    ├── urls.py
    ├── routing.py          # WebSocket routing
    └── consumers.py        # WebSocket consumers
</pre>

## Usage

### For Players
1. **Dashboard**: Access booking and match features
2. **Create Booking**: Book courts for specific times
3. **Invite Players**: Use the player selection interface to invite others
4. **View Matches**: Watch live matches and scores

### For Teachers
- All player features plus:
- **Recurring Bookings**: Create weekly recurring bookings
- **Extended Cancellation**: Cancel bookings closer to start time

### For Admins
- All features plus:
- **Court Management**: Add courts
- **User Management**: Assign teacher permissions
- **Match Management**: Create and manage matches

## Key Models

### Booking
- Court assignment
- Time slot management
- User associations
- Cancellation policies

### Match
- Player tracking
- Live scoring (sets, games, points)
- Best of 3/5 formats
- WebSocket integration

### Court
- Multiple surface types
- Image support
- Availability tracking

## WebSocket Features

Real-time match updates including:
- Score changes
- Match start/end events
- Live status updates
- Automatic UI updates

## URL Patterns

### Booking URLs
- `/bookings/` - My bookings
- `/bookings/create/` - Create booking
- `/bookings/recurring/` - Recurring booking (teachers)
- `/bookings/select-player/` - Player selection interface

### Match URLs
- `/matches/` - Match list
- `/matches/create/` - Create match (admin)
- `/matches/<id>/` - Live match view


## License

This project is for educational/demonstration purposes.

---
