from django.shortcuts import render
from django.views.generic import CreateView
from .forms import *

def home(request):
    ctx = {}
    ctx['title'] = "Smash Club"
    return render(request, 'home.html', context=ctx)

class RegisterView(CreateView):
    template_name = 'registration/register.html'
    form_class = CreateBaseUser
    success_url = '/accounts/login/'

    def form_valid(self, form):
        user = form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Register'
        return context
    