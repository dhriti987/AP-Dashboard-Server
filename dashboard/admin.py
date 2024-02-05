from django.contrib import admin
from .models import Plant, Unit, UnitData, FrequencyData

# Register your models here.
admin.site.register(Plant)
admin.site.register(Unit)
admin.site.register(UnitData)
admin.site.register(FrequencyData)
