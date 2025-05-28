import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class AIStreamConsumer(WebsocketConsumer):
    def connect(self):
        # Get session key or generate unique identifier
        self.session_key = self.scope.get('session', {}).get('session_key', 'default')
        self.stream_group_name = f'ai_stream_{self.session_key}'

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.stream_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.stream_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (from client)
    def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', '')

            # Handle client messages if needed
            # For now, we're just using WebSocket for server->client communication
            pass

        except json.JSONDecodeError:
            self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))

    # Receive message from group
    def send_word(self, event):
        # Send word to WebSocket
        self.send(text_data=json.dumps(event['data']))