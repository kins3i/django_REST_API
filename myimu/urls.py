from django.urls import include, path

from rest_framework import routers
from . import views

router = routers.SimpleRouter()

router.register(r'post', views.PostViewSet, basename="post")

urlpatterns = [
    path('', include(router.urls)),
    # path(r'data/', views.SensorList.as_view() ),
    path(r'start/', views.start, name="start"),
    path(r'results/', views.results, name="results"),
    path(r'graph/', views.draw_graph, name="graph"),
    path(r'del_items/', views.delete_items, name="del_items"),
    path(r'del_file/', views.delete_file, name="del_file"),
    path(r'get_file/', views.get_file, name="get_file"),
    path(r'clear_session/', views.clear_session, name='clear_session'),
]