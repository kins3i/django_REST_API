from rest_framework import serializers

from . import models


class SensorsValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SensorsValue
        # fields = 'timer', 'accX', 'accY', 'accZ', 'gyrX', 'gyrY', 'gyrZ'
        fields = '__all__'
        read_only_fields = ['__all__']