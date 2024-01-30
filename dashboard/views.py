from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import Plant, PlantSerializer, Unit, UnitSerializer, UnitTimeSeriesDataSerializer, UnitData
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Prefetch
from datetime import datetime

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


class UnitUpdatedeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific Unit object.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


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
        # print(self.request.query_params)
        if self.request.query_params.get("plant"):
            data = self.get_queryset().filter(
                plant__name=self.request.query_params.get("plant")).prefetch_related(Prefetch(
                    "unit_data", UnitData.objects.filter(sample_time__lt=datetime.today())))
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
                    "unit_data", UnitData.objects.filter(sample_time__lt=datetime.today()))).get(pk=self.request.query_params.get("unit"))
                serializer_obj = self.get_serializer_class()(data)
                distinct_data_points = []
                for data_point in (serializer_obj.data["unit_data"]):
                    if not len(distinct_data_points):
                        distinct_data_points.append(data_point)
                    elif data_point["sample_time"] != distinct_data_points[-1]["sample_time"]:
                        print(data_point["sample_time"],
                              distinct_data_points[-1]["sample_time"])
                        distinct_data_points.append(data_point)
                # print(len(distinct_data_points))
                # serializer_obj.data["unit_data"] = distinct_data_points
                # print(len(serializer_obj.data["unit_data"]))
                return Response({"id": serializer_obj.data["id"], "unit_data": distinct_data_points})
            except Exception as e:
                print(e)
                raise ValidationError("Mentioned Unit id doesn't exist")
        else:
            raise ValidationError("provide plant or unit parameter")
        return Response(serializer_obj.data)
