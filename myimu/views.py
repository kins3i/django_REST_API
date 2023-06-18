from . import models, serializers

from django.views.generic import DetailView, TemplateView
from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from rest_framework import viewsets
from django.db import connection

import numpy as np
import math
import statistics as stat
from scipy.fftpack import fft
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SensorsValueSerializer
    queryset = models.SensorsValue.objects.all()
    # authentication_classes = []  # disables authentication
    # permission_classes = []


def start(request):
    if request.GET.get('start'):
        return HttpResponse("start")
    if request.GET.get('stop'):
        return HttpResponse("stop")
    return render(request, "start.html")


def calc_results():
    time = []
    vecA = []
    vecG = []

    if models.SensorsValue.objects.all().exists():
        for x in models.SensorsValue.objects.all():
            time.append(x.timer)
            temp = [x.accX, x.accY, x.accZ]
            num = math.sqrt(temp[0] ** 2 + temp[1] ** 2 + temp[2] ** 2)
            vecA.append(num)
            temp = [x.gyrX, x.gyrY, x.gyrZ]
            num = math.sqrt(temp[0] ** 2 + temp[1] ** 2 + temp[2] ** 2)
            vecG.append(num)
            temp = []

        n = len(vecA)
        dt = stat.mean(np.diff(time))
        fs = 1 / (dt / 1000)
        fs = fs.item()
        freq = np.arange(0, fs / 2 + fs / len(vecA), fs / len(vecA))
        yfAcc = fft(vecA)
        yfAcc = yfAcc.tolist()
        yfGyr = fft(vecG)
        yfGyr = yfGyr.tolist()

        absAcc = [abs(x) for x in yfAcc]
        absGyr = [abs(x) for x in yfGyr]
        powAcc = [(i ** 2) / n for i in absAcc]
        powGyr = [(i ** 2) / n for i in absGyr]

        context = {
            'time': time,
            'vecACC': vecA,
            'vecGYR': vecG,
            'frequency': freq,
            'powerAcc': powAcc,
            'powerGyr': powGyr,
        }

        # print(time)

        return context

    # return render(request, 'graph.html', context)
    # return response


def draw_graph(request):
    context = calc_results()

    if context:
        freq = context["frequency"]
        powAcc = context["powerAcc"]
        powGyr = context["powerGyr"]

        # print(powAcc)
        # print(freq)

        fig, ax = plt.subplots(1, 2, figsize=(15, 10))
        plt.subplots_adjust(wspace=0.8)

        ax[0].plot(freq, powAcc)
        ax[0].grid()
        ax[0].set_title("Frequency spectrum of linear acceleration")
        ax[0].set_xlabel("Frequency [Hz]")
        ax[0].set_ylabel("Amplitude [mg]")
        ax[0].set_yscale("log")

        ax[1].plot(freq, powGyr)
        ax[1].grid()
        ax[1].set_title("Frequency spectrum of angular velocity")
        ax[1].set_xlabel("Frequency [Hz]")
        ax[1].set_ylabel("Amplitude [deg/s]")
        ax[1].set_yscale("log")

        # input()

        response = HttpResponse(
            content_type='image/png',
        )

        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)

        plt.close()

        return response

def results(request):
    context = calc_results()
    if context:
        return render(request, 'results.html')
    return redirect('post-list')


def delete_items(request):
    queryset = models.SensorsValue.objects.all()
    if queryset.exists():
        queryset.delete()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE sqlite_sequence SET seq = 1 WHERE name = 'myimu_sensorsvalue'")
    return redirect('post-list')
