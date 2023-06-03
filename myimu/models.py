from django.db import models

class SensorsValue(models.Model):
    timer = models.PositiveBigIntegerField(default=0)
    localtime = models.DateTimeField(auto_now = True)
    accX = models.FloatField(default=0)
    accY = models.FloatField(default=0)
    accZ = models.FloatField(default=0)
    gyrX = models.FloatField(default=0)
    gyrY = models.FloatField(default=0)
    gyrZ = models.FloatField(default=0)
