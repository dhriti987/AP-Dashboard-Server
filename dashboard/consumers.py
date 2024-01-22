from channels.generic.websocket import AsyncJsonWebsocketConsumer


class UnitDataConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if self.scope['plant'] == None:
            return
        self.plant = self.scope['plant'][0]

        await self.channel_layer.group_add(
            self.plant,
            self.channel_name
        )
        await self.accept()

        # await self.channel_layer.group_send(
        #     self.plant,
        #     {
        #         "type": "unit_data_for_plant",
        #         "data": f"connected to {self.plant}",
        #     }
        # )

    async def disconnect(self, code):
        if hasattr(self, "chat_room"):
            await self.channel_layer.group_discard(
                self.plant,
                self.channel_name
            )
        return await super().disconnect(code)

    async def unit_data_for_plant(self, event):
        data = event['data']
        await self.send_json(data)
