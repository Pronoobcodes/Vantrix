from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ChatConsumer(
    AsyncJsonWebsocketConsumer
):

    async def connect(self):

        self.room_name = self.scope[
            "url_route"
        ]["kwargs"]["conversation_id"]

        self.group_name = (
            f"chat_{self.room_name}"
        )

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(
        self,
        close_code
    ):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive_json(
        self,
        content
    ):

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "message": content,
            }
        )

    async def chat_message(
        self,
        event
    ):
        await self.send_json(
            event["message"]
        )