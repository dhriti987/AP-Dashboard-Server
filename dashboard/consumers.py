from channels.generic.websocket import AsyncJsonWebsocketConsumer
import asyncio
from .models import UnitData, Unit, FrequencyData
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


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
        await asyncio.sleep(1)
        recent_data = await self.get_recent_unit_datas()

        await self.channel_layer.group_send(
            self.plant,
            {
                "type": "unit_data_for_plant",
                "data": recent_data,
            }
        )

    async def disconnect(self, code):
        if hasattr(self, "chat_room"):
            await self.channel_layer.group_discard(
                self.plant,
                self.channel_name
            )
        return await super().disconnect(code)

    async def unit_data_for_plant(self, event):
        data = event['data']
        print(data)
        await self.send_json({"frequency": await self.get_frequency_data(), "data": data})

    @database_sync_to_async
    def get_recent_unit_datas(self):
        units = Unit.objects.filter(plant__name=self.plant)
        data = []
        for unit in units:
            unit_data = unit.unit_data.last()
            data.append({
                "pointId": unit.point_id,
                "pointValues": float(unit_data.point_value) if unit_data else 0
            })
        return data

    @database_sync_to_async
    def get_frequency_data(self):
        try:
            return float(FrequencyData.objects.last().point_value)
        except:
            return 0
