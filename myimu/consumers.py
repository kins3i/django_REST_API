import json

from asgiref.sync import sync_to_async
from django.core import serializers


from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    PatchModelMixin,
    UpdateModelMixin,
    CreateModelMixin,
    DeleteModelMixin,
)

from djangochannelsrestframework.observer import model_observer

from . import models, serializers


class PostConsumer(
        ListModelMixin,
        RetrieveModelMixin,
        PatchModelMixin,
        UpdateModelMixin,
        CreateModelMixin,
        DeleteModelMixin,
        GenericAsyncAPIConsumer,):
    queryset = models.SensorsValue.objects.all()
    serializer_class = serializers.SensorsValueSerializer()
    # permissions = (permissions.AllowAny,)

    authentication_classes = []  # disables authentication
    permission_classes = []

    async def connect(self, **kwargs):
        await super().connect()
        await self.model_change.subscribe()
        print("Connected")

    async def receive(self, text_data=None, bytes_data=None):
        incoming = json.loads(text_data)
        try:
            incoming["action"]
        except:
            pass
        else:
            action = incoming["action"]

        try:
            incoming["request_id"]
        except:
            pass
        else:
            request_id = incoming["request_id"]

        try:
            incoming["data"]
        except NameError:
            print("Faulty data")
        else:
            data = incoming["data"]

        m = models.SensorsValue(**data)
        await sync_to_async(m.save)()
        print("Message received")

    @model_observer(models.SensorsValue)
    async def model_change(self, message, **kwargs):
        print(message)
        # await self.send_json(message) # send message back to sensor

    @model_change.serializer
    def model_serialize(self, instance, action, **kwargs):
        # print(dict(data=serializers.SensorsValueSerializer(instance=instance).data, action=action.value))
        return dict(data=serializers.SensorsValueSerializer(instance=instance).data, action=action.value)

    async def disconnect(self, message):
        print("Disconnected")
        await super().disconnect(message)

# class PostConsumer(GenericAsyncAPIConsumer):
#     queryset = models.SensorsValue.objects.all()
#     serializer_class = serializers.SensorsValueSerializer()
#     authentication_classes = []  # disables authentication
#     permission_classes = []
#
#     @model_observer(models.SensorsValue)
#     async def add_data(
#         self,
#         message: serializers.SensorsValueSerializer,
#         observer=None,
#         subscribing_request_ids=[],
#         **kwargs
#     ):
#         await self.send_json(dict(message.data))
#
#     @add_data.serializer
#     def add_data(self, instance: models.SensorsValue, action, **kwargs) -> serializers.SensorsValueSerializer:
#         """This will return the comment serializer"""
#         return serializers.SensorsValueSerializer(instance)
#
#     @action()
#     async def subscribe_data(self, request_id, **kwargs):
#         await self.add_data.subscribe(request_id=request_id)
