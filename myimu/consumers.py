import time
import datetime

from djangochannelsrestframework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    PatchModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DeleteModelMixin,
)
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer

model_list = []
filename = ''


class PostConsumer(
    ListModelMixin,
    RetrieveModelMixin,
    PatchModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DeleteModelMixin,
    GenericAsyncAPIConsumer):
    authentication_classes = []  # disables authentication
    permission_classes = []

    async def connect(self, **kwargs):
        await super().connect()
        # await self.model_change.subscribe()
        global model_list
        global filename
        model_list = []
        today = datetime.date.today()
        now = datetime.datetime.now()
        current_time = datetime.time(now.hour, now.minute)
        name = datetime.datetime.combine(today, current_time)
        print(name)
        date_str = name.strftime("%d-%m-%Y_%H_%M")
        filename = date_str + ".txt"
        print(filename)
        print("Connected")
        await self.send_json('message')

    async def receive(self, text_data=None, bytes_data=None):
        start = time.time()
        global model_list
        global filename
        separator = '\n'
        model_list.append(text_data)
        if len(model_list) >= 500:
            await self.send_json('save')
            long_str = separator.join(model_list)
            long_str += '\n'
            # file = open(filename, 'a')
            with open(filename, 'a') as file:
                file.write(long_str)
            print("add to file time {}.".format((time.time() - start) * 1000))
            model_list = []
        if ((time.time() - start) * 1000) > 0.9:
            print("time {}.".format((time.time() - start) * 1000))
            # print("Message received")

    async def disconnect(self, message):
        print("Disconnected")
        global model_list
        model_list = []
        global filename
        filename = ''
        await super().disconnect(message)
