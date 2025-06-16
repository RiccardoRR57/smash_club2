from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from . import views 

app_name = 'matches'

urlpatterns = [
    path("<int:match_id>/",views.match_details,name="details"),
    path("list/", views.MatchListView.as_view(), name="list"),
    path("create/", views.MatchCreateView.as_view(), name="create"),
]
