from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import ListView, CreateView
from django.utils.decorators import method_decorator
from .models import Match

def match_details(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'start':
            match.start()
        elif action == 'stop':
            match.stop()
        elif action == 'player1_point':
            match.add_point(1)
        elif action == 'player2_point':
            match.add_point(2)
        match.save()
        return redirect('matches:match', match_id=match.id)

    context = {
        'match': match,
        'title': 'Match Details',
    }

    return render(request, 'match.html', context=context)

class MatchListView(ListView):
    model = Match
    template_name = "match_list.html"
    context_object_name = "matches"
    title = "Match List"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context
    
@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class MatchCreateView(CreateView):
    model = Match
    fields = ['player1', 'player2', 'best_of']
    template_name = 'match_form.html'
    success_url = '/matches/list/'

    def form_valid(self, form):
        form.instance.is_live = False  # Set match to not live initially
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Match'
        return context