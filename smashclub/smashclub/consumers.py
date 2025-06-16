from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from matches.models import Match

class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.room_group_name = f"match_{self.match_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')

        if action == 'add_point':
            player = text_data_json.get('player')

            # Update the match score using the add_point method
            match = await sync_to_async(Match.objects.get)(id=self.match_id)
            await sync_to_async(match.add_point)(1 if player == 'pl1' else 2)

            if match.winner:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'match_ended',
                        'winner': match.get_winner(),
                    }
                )
            
            # Broadcast the updated score
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'match_score_update',
                    'score': {
                        'set_pl1': match.set_player1,
                        'set_pl2': match.set_player2,
                        'game_pl1': match.game_player1,
                        'game_pl2': match.game_player2,
                        'point_pl1': match.point_player1,
                        'point_pl2': match.point_player2,
                    },
                }
            )
            
        elif action == 'start_match':
            # Start the match
            match = await sync_to_async(Match.objects.get)(id=self.match_id)
            await sync_to_async(match.start)()

            # Notify all clients that the match has started
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'match_started',
                    'message': 'Match has started.',
                }
            )

    async def match_score_update(self, event):
        score = event['score']

        await self.send(text_data=json.dumps({
            'type': 'match_score_update',
            'score': score,
        }))

    async def match_started(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'type': 'match_started',
            'message': message,
        }))

    async def match_ended(self, event):
        winner = event['winner']

        await self.send(text_data=json.dumps({
            'type': 'match_ended',
            'winner': winner,
        }))