from django.urls import include, path

from .views import estudiante, tutoria

urlpatterns = [
    path('tutoria/<str:hash>', tutoria.registro, name='registro'),
]
