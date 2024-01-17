from django.db import models

# Create your models here.
class Plant(models.Model):
    name = models.CharField(max_length=20, unique=True)

class Unit(models.Model):
    point_id = models.CharField(max_length=50, unique=True)
    system_guid = models.CharField(max_length=80, unique=True)
    plant = models.ForeignKey(Plant,on_delete=models.CASCADE,related_name= "units")
    unit = models.CharField(max_length=10, unique=True)
    code = models.CharField(max_length=30, unique=True)

class UnitData(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="unit_data")
    point_value = models.DecimalField(max_digits=5, decimal_places=2)
    quality = models.CharField(max_length=20)
    derived_quality = models.CharField(max_length=20)
    sample_time = models.DateTimeField()