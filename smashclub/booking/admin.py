from django.contrib import admin
from .models import Court, Booking, InvitedPlayer


admin.site.register(Court)
admin.site.register(Booking)
admin.site.register(InvitedPlayer)