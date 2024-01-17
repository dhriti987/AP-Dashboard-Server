from django.urls import path
from .views import PlantListCreateAPIView, PlantUpdateDeleteAPIView, UnitListCreateAPIView, UnitUpdatedeleteAPIView

urlpatterns = [
    path("plant/", PlantListCreateAPIView.as_view()),
    path("plant/<int:pk>", PlantUpdateDeleteAPIView.as_view()),
    path("unit/", UnitListCreateAPIView.as_view()),
    path("unit/<int:pk>", UnitUpdatedeleteAPIView.as_view()),
]
