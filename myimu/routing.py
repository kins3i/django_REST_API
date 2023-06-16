from django.template.defaulttags import url
from django.urls import re_path, path
from djangochannelsrestframework.consumers import view_as_consumer

from . import views
from . import consumers

ws_urlpatterns = [
    re_path("", consumers.PostConsumer.as_asgi())
    # url(r"ws/$", view_as_consumer(views.PostViewSet))
]