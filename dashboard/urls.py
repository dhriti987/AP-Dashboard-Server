from django.urls import path
from .views import (PlantListCreateAPIView, PlantUpdateDeleteAPIView, PlantListAPIView,
                    UnitListCreateAPIView, UnitUpdatedeleteAPIView, UnitListAPIView, UnitTimeSeriesDataAPIView, UpdateClientCredentialsAPIView)

urlpatterns = [
    path("plant/add_plant/", PlantListCreateAPIView.as_view()),
    path("plant/", PlantListAPIView.as_view()),
    path("plant/<int:pk>", PlantUpdateDeleteAPIView.as_view()),
    path("unit/add_unit/", UnitListCreateAPIView.as_view()),
    path("unit/<str:plant>", UnitListAPIView.as_view()),
    path("units/<int:pk>", UnitUpdatedeleteAPIView.as_view()),
    path("unit-time-series/", UnitTimeSeriesDataAPIView.as_view()),
    path("update-client-cred/", UpdateClientCredentialsAPIView.as_view()),
]
