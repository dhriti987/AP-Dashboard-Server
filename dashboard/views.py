from rest_framework import generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import Plant, PlantSerializer, Unit, UnitSerializer
from rest_framework.response import Response

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
