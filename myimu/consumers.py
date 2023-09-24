import time
import datetime
import os

from channels.generic.websocket import AsyncWebsocketConsumer

model_list = []
filename = ''


class PostConsumer(AsyncWebsocketConsumer):

    authentication_classes = []  # disables authentication
    permission_classes = []

    groups = ["echo_group"]

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_group_name = 'echo_group'
        self.room_name = 'event'

    async def connect(self, **kwargs):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        global model_list
        global filename
        model_list = []
        today = datetime.date.today()
        now = datetime.datetime.now()
        current_time = datetime.time(now.hour, now.minute, now.second)
        name = datetime.datetime.combine(today, current_time)
        date_str = name.strftime("%d-%m-%Y_%H_%M_%S")
        filename = os.path.join(os.getcwd(), "data_log", date_str+".txt")
        print(filename)
        print("Connected")
        await self.send('Good connection')

    async def receive(self, text_data=None, bytes_data=None):
        start = time.time()
        global model_list
        global filename
        separator = '\n'
        model_list.append(text_data)
        if len(model_list) >= 500:
            long_str = separator.join(model_list)
            long_str += '\n'
            with open(filename, 'a') as file:
                file.write(long_str)
            print("add to file time {}.".format((time.time() - start) * 1000))
            model_list = []
        if ((time.time() - start) * 1000) > 0.9:
            print("time {}.".format((time.time() - start) * 1000))
            # print("Message received")

    async def invoke_start_stop(self, event):
        # Receive message from room group (exactly from button view)
        message = event['message']
        print("EVENT TRIGGERED: ", message)
        await self.send(message)

    async def disconnect(self, message):
        print("Disconnected")
        await self.send('Server disconnected')
        global model_list
        model_list = []
        global filename
        filename = ''
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await super().disconnect(message)
