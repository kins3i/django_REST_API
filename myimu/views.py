from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.http.response import HttpResponse
from rest_framework import viewsets


from . import models, serializers

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SensorsValueSerializer
    queryset = models.SensorsValue.objects.all()
    # authentication_classes = []  # disables authentication
    # permission_classes = []


# class SensorList(APIView):
#     """
#     List all snippets, or create a new snippet.
#     """
#     authentication_classes = []  # disables authentication
#     permission_classes = []
#
#     def get(self, request, format=None):
#         snippets = models.SensorsValue.objects.all()
#         serializer = serializers.SensorsValueSerializer(snippets, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format="json"):
#         serializer = serializers.SensorsValueSerializer(data=request.data, many = True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, pk, format=None):
    #     snippet = self.get_object(pk)
    #     serializer = serializers.SensorsValueSerializer(snippet, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def start(request):
    if (request.GET.get('start')):
        return HttpResponse("start")
    if (request.GET.get('stop')):
        return HttpResponse("stop")
    return render(request, "start.html")