# Register your models here.
from django.contrib import admin

from . import models
from .models import SensorsValue


@admin.register(models.SensorsValue)
class SensorsValueAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SensorsValue._meta.get_fields()]