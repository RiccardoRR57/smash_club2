from django.db import models

# Create your models here.
class Match(models.Model):
    BEST_OF_CHOICES = [
        (3, 'Best of 3'),
        (5, 'Best of 5'),
    ]

    player1 = models.CharField(max_length=100)
    player2 = models.CharField(max_length=100)
    best_of = models.PositiveIntegerField(choices=BEST_OF_CHOICES, default=3)

    set_player1 = models.IntegerField(default=0)
    set_player2 = models.IntegerField(default=0)
    game_player1 = models.IntegerField(default=0)
    game_player2 = models.IntegerField(default=0)
    point_player1 = models.IntegerField(default=0)
    point_player2 = models.IntegerField(default=0)

    winner = models.IntegerField(null=True, blank=True)  # 1 for player1, 2 for player2
    is_live = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def add_point(self, player):
        if not self.is_live:
            return

        if player == 1:
            self.point_player1 += 1
        elif player == 2:
            self.point_player2 += 1
        else:
            raise ValueError("Player must be 1 or 2")

        # Tennis point progression: 0, 15, 30, 40, Advantage, Game
        def has_won_game(p1, p2):
            return (p1 >= 4 and p1 - p2 >= 2)

        if has_won_game(self.point_player1, self.point_player2):
            self.game_player1 += 1
            self.point_player1 = 0
            self.point_player2 = 0
        elif has_won_game(self.point_player2, self.point_player1):
            self.game_player2 += 1
            self.point_player1 = 0
            self.point_player2 = 0

        # Set is usually first to 6 games, win by 2
        def has_won_set(g1, g2):
            return (g1 >= 6 and g1 - g2 >= 2) or (g1 == 7 and g2 == 5) or (g1 == 7 and g2 == 6)

        if has_won_set(self.game_player1, self.game_player2):
            self.set_player1 += 1
            self.game_player1 = 0
            self.game_player2 = 0
        elif has_won_set(self.game_player2, self.game_player1):
            self.set_player2 += 1
            self.game_player1 = 0
            self.game_player2 = 0

        # Determine if match is finished and set winner
        if self.set_player1 > self.best_of // 2:
            self.is_live = False
            self.winner = 1
        elif self.set_player2 > self.best_of // 2:
            self.is_live = False
            self.winner = 2

        self.save()

    def start(self):
        if not self.is_live:
            self.is_live = True
            self.set_player1 = 0
            self.set_player2 = 0
            self.game_player1 = 0
            self.game_player2 = 0
            self.point_player1 = 0
            self.point_player2 = 0
            self.winner = None
            self.save()
        
    def stop(self):
        if self.is_live:
            self.is_live = False
            self.save()

    def get_winner(self):
        if self.winner == 1:
            return self.player1
        elif self.winner == 2:
            return self.player2
        else:
            return "--"

    def get_score(self):
        return f"{self.set_player1}-{self.set_player2} ({self.game_player1}-{self.game_player2}) ({self.point_player1}-{self.point_player2})"

    def __str__(self):
        return f"{self.player1} vs {self.player2} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}"