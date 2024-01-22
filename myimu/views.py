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
import scipy.signal as signal
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
    return redirect('start')


def calc_results(myfilename):
    filename = myfilename
    path = os.path.join(os.getcwd(), r'IMU_Logi', filename)

    print(path)

    time = []
    vecA = []
    vecG = []
    missed_time = []
    dt_read = 0
    start_row = 20
    end_row = 10000+5

    # read data from file
    if os.path.isfile(path):
        with open(path, 'r') as file:
            str_list = file.readlines()
        for row in str_list[8+start_row:end_row+8+start_row]:
            row_str = row.replace(' ', '').replace(',', '.')
            check_str_NaN = row_str.find('NaN')
            if check_str_NaN != -1:
                print("Broken row: ", row_str)
                break
            time.append(int(row_str.split(';')[5]))
            if len(time) == 2:
                dt_read = time[1] - time[0]
                if dt_read == 0:
                    break
            if (len(time) > 2) and (time[-1] - time[-2] != dt_read):
                print("last correct time: ", time[-2])
                if time[-1] - time[-2] != 2*dt_read:
                    time.pop()
                    break
                else:
                    missed_time.append((time[-1] - time[-2]) / 2)
                    if len(missed_time) > 2 and (missed_time[-1] - missed_time[-2] == dt_read):
                        time.pop()
                        break
                    time.pop()

                    accX = float(row_str.split(';')[6])
                    accY = float(row_str.split(';')[7])
                    accZ = float(row_str.split(';')[8])
                    gyrX = float(row_str.split(';')[9])
                    gyrY = float(row_str.split(';')[10])
                    gyrZ = float(row_str.split(';')[11])

                    tempA = [accX, accY, accZ]
                    num = math.sqrt(tempA[0] ** 2 + tempA[1] ** 2 + tempA[2] ** 2)
                    meanA = stat.mean([num, vecA[-1]])
                    tempG = [gyrX, gyrY, gyrZ]
                    num = math.sqrt(tempG[0] ** 2 + tempG[1] ** 2 + tempG[2] ** 2)
                    meanG = stat.mean([num, vecG[-1]])

                    time.append(missed_time)
                    vecA.append(meanA)
                    vecG.append(meanG)

                    time.append(int(row_str.split(';')[5]))

            accX = float(row_str.split(';')[6])
            accY = float(row_str.split(';')[7])
            accZ = float(row_str.split(';')[8])
            gyrX = float(row_str.split(';')[9])
            gyrY = float(row_str.split(';')[10])
            gyrZ = float(row_str.split(';')[11])

            tempA = [accX, accY, accZ]
            num = math.sqrt(tempA[0] ** 2 + tempA[1] ** 2 + tempA[2] ** 2)          # calc vec of acc
            vecA.append(num)
            tempG = [gyrX, gyrY, gyrZ]
            num = math.sqrt(tempG[0] ** 2 + tempG[1] ** 2 + tempG[2] ** 2)          # calc vec of gyr
            vecG.append(num)

            if np.isnan(vecA[-1]) or np.isnan(vecG[-1]):
                time.pop()
                vecA.pop()
                vecG.pop()
                break



            # print(vecA)
            # print(vecG)
        print("Last saved time: ", time[-1])

        # if len(vecA) % 2 != 0:                                                      # check if number of samples is even
        #     # delete last uneven sample
        #     time.pop()
        #     vecA.pop()
        #     vecG.pop()

        n_time = len(time)
        print("n_time: ", n_time)

        # calculate moving average on acc and gyr
        avgVecA = []
        avgVecG = []
        window = 5

        k = 0
        while k < len(vecA) - window + 1:
            # Calculate the average of current window
            window_averageA = round(np.sum(vecA[k:k + window]) / window, 2)
            window_averageG = round(np.sum(vecG[k:k + window]) / window, 2)
            # Store the average of current
            # window in moving average list
            avgVecA.append(window_averageA)
            avgVecG.append(window_averageG)
            # Shift window to right by one position
            k += 1

        vecA = avgVecA
        vecG = avgVecG

        if len(vecA) % 2 != 0:                                                      # check if number of samples is even
            # delete last uneven sample
            time.pop()
            vecA.pop()
            vecG.pop()

        # read file for conversion of units (from mg to m/s2)
        raw = []
        milig = []

        przelicznik_txt = "przelicznik.txt"
        path_p = os.path.join(os.getcwd(), przelicznik_txt)
        if os.path.isfile(path_p):
            with open(przelicznik_txt, 'r') as file:
                all_lines = file.readlines()
            for row in all_lines[1:]:
                milig.append(float(row.split(',')[0]))
                raw.append(float(row.split(',')[1]))

        przelicznik = stat.mean(raw) / stat.mean(milig)

        mean_milig = stat.mean(milig)

        vecA = [x - mean_milig for x in vecA]                                       # delete value of standard gravity

        # count sample rate
        n = len(vecA)
        print("n: ", n)

        dt = stat.mean(np.diff(time))
        print("dt: ", dt)
        # print("t: ", time)
        fs = 1 / (dt / 1000)
        fs = fs.item()

    # this part of code comes from some internet example on designing IIR and FIR filters
        # prepare band-pass IIR filter (for removing 0 Hz part of signal)
        sampling_frequency = fs  # Sampling frequency in Hz
        passband_frequencies = (2.0, 30.0)  # Filter cutoff in Hz
        stopband_frequencies = (0.0, 60.0)
        max_loss_passband = 3  # The maximum loss allowed in the passband
        min_loss_stopband = 30  # The minimum loss allowed in the stopband

        # calculation of filter's order
        order, normal_cutoff = signal.buttord(passband_frequencies, stopband_frequencies, max_loss_passband,
                                              min_loss_stopband, fs=sampling_frequency)

        # calculation of Butterworth filter
        iir_b, iir_a = signal.butter(order, normal_cutoff, btype="bandpass", fs=sampling_frequency)

        # prepare and save graph of filter's response for thesis paper
        # w, h = signal.freqz(iir_b, iir_a, worN=np.logspace(0, 3, 100), fs=sampling_frequency)
        # plt.semilogx(w, 20 * np.log10(abs(h)))
        # plt.title('Butterworth IIR bandpass filter fit to constraints')
        # plt.xlabel('Frequency [Hz]')
        # plt.ylabel('Amplitude [dB]')
        # plt.grid(which='both', axis='both')
        # plt.savefig("filter.svg", format="svg")
        # plt.savefig("filter.png", format="png")

        # do signals filtration
        vecA = signal.lfilter(iir_b, iir_a, vecA)
        vecG = signal.lfilter(iir_b, iir_a, vecG)

        # create list of frequencies
        k = arange(n)
        T = n / fs
        freq1 = k / T  # two sides frequency range
        freq = freq1[range(math.floor(n / 2))]  # one side frequency range


        # FFT of acc
        Y_A = fft(vecA) / n  # fft computing and normalization
        Y_A = Y_A[range(math.floor(n / 2))]
        powAcc = abs(Y_A)
        # FFT of gyr
        Y_G = fft(vecG) / n  # fft computing and normalization
        Y_G = Y_G[range(math.floor(n / 2))]
        powGyr = abs(Y_G)

        # find which real index of frequency list is closest to one that gives 50 Hz
        idx_50 = min(range(len(freq)), key=lambda i: abs(freq[i] - 50))

        # find main frequency (with the largest value of spectrum)
        max_powAcc = max(powAcc[0:idx_50])
        idx_f = np.where(powAcc == max_powAcc)
        f_max = freq[idx_f]
        f_max = f_max.item()

        # find amplitude of acc signal
        absA = abs(vecA)
        sortAbsA = sorted(absA, reverse=True)
        max10A = sortAbsA[0:10]
        maxAmp = stat.mean(max10A)
        meanVecA = stat.mean(vecA)
        ampVecA = maxAmp - meanVecA

        # unit conversion
        amp_ms2 = ampVecA * przelicznik                                                     # from mg to m/s2
        omega = 2 * math.pi * f_max

        # estimate displacement
        amp_m = amp_ms2 / (omega ** 2)
        amp_mm = round(amp_m*1000, 3)

        # some printing for debugging calculations
        # print("meanVecA ", meanVecA)
        # print("ampVecA ", ampVecA)
        # print("amp_ms2 ", amp_ms2)
        # print("omega ", omega)
        # print("amp_m ", amp_m)
        print("amp_mm", amp_mm)

        f_max = round(f_max, 3)

        # create context for draw_graph(request)
        context = {
            'time': time,
            'vecACC': vecA,
            'vecGYR': vecG,
            'frequency': freq,
            'powerAcc': powAcc,
            'powerGyr': powGyr,
            'freq_max': f_max,
            'amp_mm': amp_mm,
            'idx_f': idx_f,
        }

        return context


def draw_graph(request):
    filename = request.session.get('myfilename')
    context = calc_results(filename)

    if context:
        freq = context["frequency"]
        powAcc = context["powerAcc"]
        powGyr = context["powerGyr"]

        # again find index of frequencies' list, where frequency is the closest to 50 Hz
        idx_50 = min(range(len(freq)), key=lambda i: abs(freq[i]-50))

        # creating dynamic graph with 2 subplots
        fig, ax = plt.subplots(1, 2, figsize=(30, 10))
        plt.subplots_adjust(wspace=0.3)
        # first subplot with red mark for f_max
        markerline0, stemline0, baseline0 = ax[0].stem(freq[:idx_50], powAcc[:idx_50])
        plt.setp(markerline0, markersize=2)
        ax[0].grid()
        ax[0].set_title("Frequency spectrum of linear acceleration")
        ax[0].set_xlabel("Frequency [Hz]")
        ax[0].set_ylabel("Amplitude [mg]")
        ax[0].set_yscale("log")
        # second subplot with red mark for f_max
        markerline1, stemline1, baseline1 = ax[1].stem(freq[:idx_50], powGyr[:idx_50])
        plt.setp(markerline1, markersize=2)
        ax[1].grid()
        ax[1].set_title("Frequency spectrum of angular velocity")
        ax[1].set_xlabel("Frequency [Hz]")
        ax[1].set_ylabel("Amplitude [deg/s]")
        ax[1].set_yscale("log")

        response = HttpResponse(
            content_type='image/png',
        )

        # create Canvas object for dynamic image
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(response)
        # it ensures everything refreshes properly
        plt.close()

        # set variables from context in session for another view
        request.session['freq_max'] = context['freq_max']
        request.session['amp_mm'] = context['amp_mm']

        # creating 2 single plots of earlier subplots to save images for thesis paper
        # name = filename.replace('.txt', '')
        # name_acc = name + "_widmo_acc.png"
        # name_gyr = name + "_widmo_gyr.png"
        # idx_f = context["idx_f"]
        #
        # plt.figure(figsize=(10, 10))
        # markerline00, stemline00, baseline00 = plt.stem(freq[:idx], powAcc[:idx])
        # markerline02, stemline02, baseline02 = plt.stem(freq[idx_f], powAcc[idx_f])
        # plt.setp(markerline00, markersize=2)
        # plt.setp(markerline02, markersize=5, markerfacecolor='r')
        # plt.grid()
        # plt.title("Frequency spectrum of linear acceleration")
        # plt.xlabel("Frequency [Hz]")
        # plt.ylabel("Amplitude [mg]")
        # plt.yscale("log")
        # plt.savefig("widma/" + name_acc)
        #
        # plt.figure(figsize=(10, 10))
        # markerline11, stemline11, baseline11 = plt.stem(freq[:idx], powGyr[:idx])
        # markerline12, stemline12, baseline12 = plt.stem(freq[idx_f], powGyr[idx_f])
        # plt.setp(markerline11, markersize=2)
        # plt.setp(markerline12, markersize=5, markerfacecolor='r')
        # plt.grid()
        # plt.title("Frequency spectrum of angular velocity")
        # plt.xlabel("Frequency [Hz]")
        # plt.ylabel("Amplitude [deg/s]")
        # plt.yscale("log")
        # plt.savefig("widma/" + name_gyr)

        return response


def delete_items(request):
    queryset = models.SensorsValue.objects.all()
    if queryset.exists():
        queryset.delete()
        with connection.cursor() as cursor:
            cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'myimu_sensorsvalue'")
    return redirect('post-list')


def delete_file(request):
    # this view works in theory but always show WinErr 32
    # TODO: fix constant WinErr32
    if request.method == 'POST' and request.FILES['delfile']:
        delfile = request.FILES['delfile']
        filename = delfile.name
        path = os.path.join(os.getcwd(), r'data_log', filename)
        print(path)
        try:
            os.remove(path)
        except OSError as e:
            print("Error deleting file: " + str(e))
        else:
            return redirect('start')
    return render(request, 'delete_file.html')


def clear_session(request):
    del request.session['myfilename']
    del request.session['freq_max']
    del request.session['amp_mm']
    return redirect('start')
