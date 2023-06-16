from rest_framework import serializers

from . import models


class SensorsValueSerializer(serializers.ModelSerializer):
    # localtime = serializers.DateTimeField(source='localtime')
    class Meta:
        model = models.SensorsValue
        # optional_fields = ['id', 'localtime']
        # fields = 'timer', 'accX', 'accY', 'accZ', 'gyrX', 'gyrY', 'gyrZ'
        fields = '__all__'
        read_only_fields = ['__all__']