from django.urls import include, path

from rest_framework import routers
from . import views

router = routers.SimpleRouter()

router.register("post", views.PostViewSet, basename="post")

urlpatterns = [
    path('', include(router.urls)),
    # path(r'data/', views.SensorList.as_view() ),
    path(r'start/', views.start, name="start"),
]