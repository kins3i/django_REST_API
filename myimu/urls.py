from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from rest_framework import routers
from . import views

router = routers.SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
    # path('data', views.SensorsValueView.as_view(), {"pk": 1}),
    path(r'data/', views.SensorList.as_view() ),
    # path('sensor', views.data_list),
]