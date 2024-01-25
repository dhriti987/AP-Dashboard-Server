from django.db import models

# Create your models here.


class Plant(models.Model):
    """
    Model representing a plant entity with a unique name.
    """
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        """
        Returns a string representation of the plant object using its name.
        """
        return self.name


class Unit(models.Model):
    """
    Model representing a unit with unique identifiers (point_id, unit, code)
    and a foreign key relationship with a plant.
    """
    point_id = models.CharField(max_length=50, unique=True)
    system_guid = models.CharField(max_length=80)
    plant = models.ForeignKey(
        Plant, on_delete=models.CASCADE, related_name="units")
    unit = models.CharField(max_length=10)
    code = models.CharField(max_length=30, unique=True)
    max_voltage = models.IntegerField(default=330)

    class Meta:
        unique_together = ('plant', 'unit')

    def __str__(self):
        """
        Returns a string representation of the unit object using its code.
        """
        return self.code


class UnitData(models.Model):
    """
    Model representing unit-specific data with fields for point value, quality,
    derived quality, and sample time.
    """
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, related_name="unit_data")
    point_value = models.DecimalField(max_digits=5, decimal_places=2)
    quality = models.CharField(max_length=20)
    derived_quality = models.CharField(max_length=20)
    sample_time = models.DateTimeField()
