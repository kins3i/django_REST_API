from rest_framework import generics, viewsets
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from braces.views import CsrfExemptMixin
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny


from . import models, serializers


# class SensorsValueView(generics.RetrieveUpdateAPIView):
#     queryset = models.SensorsValue.objects.all()
#     if not models.SensorsValue.objects.count():
#         models.SensorsValue.objects.create()
#     # serializer_class = serializers.SensorsValueSerializer(queryset, many=True)
#     serializer_class = serializers.SensorsValueSerializer


# @csrf_exempt
# def data_list(request):
#     if request.method == 'POST':
#         queryset = models.SensorsValue.objects.all()
#         if not models.SensorsValue.objects.count():
#             models.SensorsValue.objects.create()
#         serializer = serializers.SensorsValueSerializer(queryset, many=True)
#         return JsonResponse(serializer.data, safe=False)
#
#     elif request.method == 'GET':
#         data = JSONParser().parse(request)
#         serializer = serializers.SensorsValueSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)
#
#     elif request.method == 'PUT':
#         queryset = models.SensorsValue.objects.all()
#         serializer = serializers.SensorsValueSerializer(queryset, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors)

@method_decorator(csrf_exempt, name='dispatch')
class SensorList(APIView):
    """
    List all snippets, or create a new snippet.
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        snippets = models.SensorsValue.objects.all()
        serializer = serializers.SensorsValueSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = serializers.SensorsValueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def put(self, request, pk, format=None):
    #     snippet = self.get_object(pk)
    #     serializer = serializers.SensorsValueSerializer(snippet, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)