from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import Plant, PlantSerializer, Unit, UnitSerializer, UnitTimeSeriesDataSerializer, UnitData, FrequencyData, FrequencyDataSerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch
from datetime import datetime, timedelta
from .utilities import fetch_unit_data, update_client_credentials

# Create your views here.


class PlantListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating Plant objects.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class PlantUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific Plant object.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class PlantListAPIView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer


class UnitListCreateAPIView(generics.ListCreateAPIView):
    """
    API view for listing and creating Unit objects.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

    def create(self, request, *args, **kwargs):
        point_id = request.data.get("point_id")
        system_guid = request.data.get("system_guid")
        response = fetch_unit_data(
            [{"pointId": point_id, "systemGuid": system_guid}])
        if response.status_code == 400:
            raise ValidationError("Invalid System Guid")
        return super().create(request, *args, **kwargs)


class UnitUpdatedeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific Unit object.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

    def update(self, request, *args, **kwargs):
        point_id = request.data.get("point_id")
        system_guid = request.data.get("system_guid")
        response = fetch_unit_data(
            [{"pointId": point_id, "systemGuid": system_guid}])
        if response.status_code == 400:
            raise ValidationError("Invalid System Guid")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        point_id = request.data.get("point_id")
        system_guid = request.data.get("system_guid")
        response = fetch_unit_data(
            [{"pointId": point_id, "systemGuid": system_guid}])
        if response.status_code == 400:
            raise ValidationError("Invalid System Guid")
        return super().partial_update(request, *args, **kwargs)


class UnitListAPIView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer

    def list(self, request, plant):
        queryset = self.get_queryset().filter(plant__name=plant).order_by("unit")
        serializer = UnitSerializer(queryset, many=True)
        return Response(serializer.data)


class UnitTimeSeriesDataAPIView(generics.GenericAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitTimeSeriesDataSerializer

    def get(self, request):
        print(datetime.today().replace(hour=0, minute=0, second=0))
        if self.request.query_params.get("plant"):
            data = self.get_queryset().filter(
                plant__name=self.request.query_params.get("plant")).prefetch_related(Prefetch(
                    "unit_data", UnitData.objects.filter(sample_time__gt=datetime.today().replace(hour=0, minute=0, second=0))))
            serializer_obj = self.get_serializer_class()(data, many=True)
            for unit in serializer_obj.data:
                distinct_data_points = []
                for data_point in (unit["unit_data"]):
                    if not len(distinct_data_points):
                        distinct_data_points.append(data_point)
                    elif data_point["sample_time"] != distinct_data_points[-1]["sample_time"]:
                        distinct_data_points.append(data_point)
                unit["unit_data"] = distinct_data_points
        elif self.request.query_params.get("unit"):
            try:
                data = self.get_queryset().prefetch_related(Prefetch(
                    "unit_data", UnitData.objects.filter(sample_time__gt=datetime.today().replace(hour=0, minute=0, second=0)-timedelta(hours=5, minutes=30)).order_by("sample_time"))).get(pk=self.request.query_params.get("unit"))
                serializer_obj = self.get_serializer_class()(data)
                frequency_data_obj = FrequencyDataSerializer(FrequencyData.objects.filter(
                    sample_time__gt=datetime.today().replace(hour=0, minute=0, second=0)-timedelta(hours=5, minutes=30)), many=True)
                distinct_data_points = []
                distinct_freq_points = []
                print(serializer_obj.data["unit_data"][0])
                for data_point in (serializer_obj.data["unit_data"]):
                    if not len(distinct_data_points):
                        distinct_data_points.append(data_point)
                    elif data_point["sample_time"] != distinct_data_points[-1]["sample_time"]:
                        distinct_data_points.append(data_point)
                for freq_point in frequency_data_obj.data:
                    if not len(distinct_freq_points):
                        distinct_freq_points.append(freq_point)
                    elif freq_point["sample_time"] != distinct_freq_points[-1]["sample_time"]:
                        distinct_freq_points.append(freq_point)
                # print(len(distinct_data_points))
                # serializer_obj.data["unit_data"] = distinct_data_points
                # print(len(serializer_obj.data["unit_data"]))
                return Response({"id": serializer_obj.data["id"], "unit_data": distinct_data_points, "frequency": distinct_freq_points})
            except Exception as e:
                print(e)
                raise ValidationError("Mentioned Unit id doesn't exist")
        else:
            raise ValidationError("provide plant or unit parameter")
        return Response(serializer_obj.data)


class UpdateClientCredentialsAPIView(generics.GenericAPIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        client_id = request.data.get("client_id")
        client_secret = request.data.get("client_secret")
        status_code = update_client_credentials(client_id, client_secret)
        if status_code >= 400:
            raise ValidationError("Invalid Client ID and Client Secret")
        return Response()
