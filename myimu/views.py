import matplotlib

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg

from django.shortcuts import render, redirect
from django.http.response import HttpResponse
from rest_framework import viewsets
from django.db import connection
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import numpy as np
import math
import statistics as stat
from scipy import arange
from scipy.fft import fft

import os
import json

from . import models, serializers
matplotlib.use('Agg')


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SensorsValueSerializer
    queryset = models.SensorsValue.objects.all()
    # authentication_classes = []  # disables authentication
    # permission_classes = []


def start(request):
    channel_layer = get_channel_layer()
    if request.POST.get('start'):
        async_to_sync(channel_layer.group_send)(
            "echo_group",
            {
                'type': 'invoke_start_stop',
                'message': "start"
            }
        )
        print("Start")
    if request.POST.get('stop'):
        async_to_sync(channel_layer.group_send)(
            "echo_group",
            {
                'type': 'invoke_start_stop',
                'message': "stop"
            }
        )
    return render(request, "start.html")


def get_file(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        filename = myfile.name
        request.session['myfilename'] = filename
        return redirect('results')
    return render(request, 'get_file.html')


def results(request):
    filename = request.session.get('myfilename')
    freq_max = request.session.get('freq_max')
    amp_mm = request.session.get('amp_mm')
    context = {
        'freq_max': freq_max,
        'amp_mm': amp_mm,
        'filename': filename,
    }
    if filename:
        return render(request, 'results.html', context)
    return redirect('post-list')


def calc_results(myfilename):
    filename = myfilename
    path = os.path.join(os.getcwd(), filename)

    print(filename)

    time = []
    vecA = []
    vecG = []

    if os.path.isfile(path):
        file = open(filename, 'r')
        str_list = file.readlines()
        json_list = []
        for row in str_list:
            json_row = json.loads(row)
            json_list.append(json_row)
        for j_row in json_list:
            time.append(j_row['timer'])
            if (len(time) > 2) and (time[-1] - time[-2] != time[1] - time[0]):
                time.pop()
                break
            accX = j_row['accX']
            accY = j_row['accY']
            accZ = j_row['accZ']
            gyrX = j_row['gyrX']
            gyrY = j_row['gyrY']
            gyrZ = j_row['gyrZ']
            tempA = [accX / 1000, accY / 1000, accZ / 1000]
            num = math.sqrt(tempA[0] ** 2 + tempA[1] ** 2 + tempA[2] ** 2)
            vecA.append(num)
            tempG = [gyrX / 1000, gyrY / 1000, gyrZ / 1000]
            num = math.sqrt(tempG[0] ** 2 + tempG[1] ** 2 + tempG[2] ** 2)
            vecG.append(num)

        if len(vecA) % 2 != 0:
            time.pop()
            vecA.pop()
            vecG.pop()

        n = len(vecA)
        print(n)
        dt = stat.mean(np.diff(time))
        fs = 1 / (dt / 1000)
        fs = fs.item()

        k = arange(n)
        T = n / fs
        freq = k / T  # two sides frequency range
        freq = freq[range(math.floor(n / 2))]  # one side frequency range

        Y_A = fft(vecA) / n  # fft computing and normalization
        Y_A = Y_A[range(math.floor(n / 2))]
        powAcc = abs(Y_A)

        Y_G = fft(vecG) / n  # fft computing and normalization
        Y_G = Y_G[range(math.floor(n / 2))]
        powGyr = abs(Y_G)

        idx = min(range(len(freq)), key=lambda i: abs(freq[i] - 50))
        max_powAcc = max(powAcc[1:idx])
        idx_f = np.where(powAcc == max_powAcc)
        f_max = freq[idx_f]
        f_max = f_max.item()
        f_max = round(f_max, 3)
        raw = []
        milig = []

        przelicznik_txt = "przelicznik.txt"
        path = os.path.join(os.getcwd(), przelicznik_txt)
        if os.path.isfile(path):
            file = open(przelicznik_txt, 'r')
            all_lines = file.readlines()
            for row in all_lines[1:]:
                milig.append(float(row.split(',')[0]))
                raw.append(float(row.split(',')[1]))

        przelicznik = stat.mean(raw) / stat.mean(milig)
        maxA = max(vecA)
        minA = min(vecA)
        maxAmp = max(maxA, -minA)
        meanVecA = stat.mean(vecA)
        ampVecA = maxAmp - meanVecA
        amp_mms2 = ampVecA * przelicznik / 1000
        omega = 2 * math.pi * f_max

        amp_mm = amp_mms2 / (omega ** 2)
        print(amp_mm)
        amp_mm = round(amp_mm, 4)

        context = {
            'time': time,
            'vecACC': vecA,
            'vecGYR': vecG,
            'frequency': freq,
            'powerAcc': powAcc,
            'powerGyr': powGyr,
            'freq_max': f_max,
            'amp_mm': amp_mm,
        }

        return context


def draw_graph(request):
    filename = request.session.get('myfilename')
    context = calc_results(filename)

    if context:
        freq = context["frequency"]
        powAcc = context["powerAcc"]
        powGyr = context["powerGyr"]

        fig, ax = plt.subplots(1, 2, figsize=(15, 10))
        plt.subplots_adjust(wspace=0.8)

        idx = min(range(len(freq)), key=lambda i: abs(freq[i]-50))

        markerline0, stemline0, baseline0 = ax[0].stem(freq[:idx], powAcc[:idx])
        plt.setp(markerline0, markersize=2)
        ax[0].grid()
        ax[0].set_title("Frequency spectrum of linear acceleration")
        ax[0].set_xlabel("Frequency [Hz]")
        ax[0].set_ylabel("Amplitude [mg]")
        ax[0].set_yscale("log")

        markerline1, stemline1, baseline1 = ax[1].stem(freq[:idx], powGyr[:idx])
        plt.setp(markerline1, markersize=2)
        ax[1].grid()
        ax[1].set_title("Frequency spectrum of angular velocity")
        ax[1].set_xlabel("Frequency [Hz]")
        ax[1].set_ylabel("Amplitude [deg/s]")
        ax[1].set_yscale("log")

        response = HttpResponse(
            content_type='image/png',
        )

        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)

        plt.close()

        freq_max = context['freq_max']
        request.session['freq_max'] = freq_max
        amp_mm = context['amp_mm']
        request.session['amp_mm'] = amp_mm

        return response


def delete_items(request):
    queryset = models.SensorsValue.objects.all()
    if queryset.exists():
        queryset.delete()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'myimu_sensorsvalue'")
    return redirect('post-list')


def delete_file(request):
    filename = request.session.get('myfilename')
    path = os.path.join(os.getcwd(), filename)
    if os.path.isfile(path):
        os.remove(filename)
        print('File removed')
    else:
        print("The file does not exist")
    return redirect('post-list')


def clear_session(request):
    del request.session['myfilename']
    del request.session['freq_max']
    del request.session['amp_mm']
    return redirect('results')
