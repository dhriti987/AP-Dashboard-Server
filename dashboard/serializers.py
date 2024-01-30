from rest_framework import serializers
from .models import Plant, Unit, UnitData


class PlantSerializer(serializers.ModelSerializer):
    """
    Serializer for the 'Plant' model. Includes all fields.
    """
    class Meta:
        model = Plant
        fields = "__all__"


class UnitSerializer(serializers.ModelSerializer):
    """
    Serializer for the 'Unit' model. Includes all fields.
    """
    plant_name = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = "__all__"

    def get_plant_name(self, obj):
        return obj.plant.name


class UnitDataAPIRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for API requests related to the 'UnitData' model.
    Includes fields 'pointId' and 'systemGuid', with corresponding custom methods.
    """
    pointId = serializers.SerializerMethodField()
    systemGuid = serializers.SerializerMethodField()

    class Meta:
        model = Unit
        fields = ["pointId", "systemGuid"]

    def get_pointId(self, obj):
        """
        Custom method to retrieve the 'pointId' field from the 'Unit' model.
        """
        return obj.point_id

    def get_systemGuid(self, obj):
        """
        Custom method to retrieve the 'systemGuid' field from the 'Unit' model.
        """
        return obj.system_guid


class UnitDataSerializer(serializers.ModelSerializer):
    sample_time = serializers.DateTimeField(format="%H:%M")
    point_value = serializers.DecimalField(
        max_digits=5, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = UnitData
        fields = ["point_value", "sample_time"]


class UnitTimeSeriesDataSerializer(serializers.ModelSerializer):
    unit_data = UnitDataSerializer(many=True)

    class Meta:
        model = Unit
        fields = ["id", "unit_data"]
