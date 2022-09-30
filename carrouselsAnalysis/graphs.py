# -*- coding: utf-8 -*-
"""

Ceci est un package python qui contient les fonctions
pour tracer des graphs d'analyse des données d'un
carrousel.

Il contient les fonctions suivantes:
    trace_precision_moy_station:
        trace un bar graph présentant la precision moyenne d'arrêt par station
    trace_dispersion_station:
        trace un graphe boite à moustaches montrant la gaussienne de precision
        d'arrêt par station

"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

cols_precision_station = ['StopStation', 'DistanceSSP', 'TypeMouvement']

cols_precision_train = ['Train', 'DistanceSSP']


def trace_precision_station(data, cols=cols_precision_station,
                                    color=None, figsize=(8,10),
                                    xlim=(1,-1), trace_moy=True,
                                    category=cols_precision_station[2],
                                    sort=True):

    fig = plt.figure(figsize=figsize)

    # if category is used to plot against categorical data, color parameter
    # is omitted to let seaborn choos the color palette
    if category:
        color=None

    # If sort is True, the order used is alphabetical order of stop stations
    if sort:
        ordre=data[cols[0]].sort_values().unique()
    else:
        ordre=None

    # ci parameter set to None disables the plotting of confidence intervals
    # dodge parameter set to False prevents having a bar for each 'y' value
    # and for each 'hue' category: here the 'hue' parameter is just used to
    # color code each bar depending on category of hue.
    sns.barplot(data=data, y=cols[0], x=cols[1],
                color=color, orient='h', hue=category, ci=None, dodge=False,
                order=ordre)
    plt.title(f"Précision moyenne d'arrêt par station", size=16)
    plt.xlim(xlim[0],xlim[1])
    if trace_moy:
    # let plot the mean for distance to SSP across all data set
        plt.axvline(data[cols[1]].mean(), color='r', ls='--',
            label=f"Moyenne = {data[cols[1]].mean():.2f}")
    plt.legend()
    plt.xlabel('Distance au SSP')
    plt.ylabel("Station d'arrivée")
    return plt.show()

def trace_dispersion_station(data, cols=cols_precision_station,
                             color=None, figsize=(8,10), xlim=(0.5,0),
                             trace_moy=True, category=cols_precision_station[2],
                             sort=True):

    fig = plt.figure(figsize=figsize)

    # if category is used to plot against categorical data, color parameter
    # is omitted to let seaborn choos the color palette
    if category:
        color=None

    # If sort is True, the order used is alphabetical order of stop stations
    if sort:
        ordre=data[cols[0]].sort_values().unique()
    else:
        ordre=None

    # dodge parameter set to False prevents having a bar for each 'y' value
    # and for each 'hue' category: here the 'hue' parameter is just used to
    # color code each bar depending on category of hue.
    sns.boxplot(data=data, x=cols[1], y=cols[0], color=color,
                hue=category, orient='h', order=ordre, dodge=False)
    plt.title("Répartition statistique des arrêts par station", size=16)
    plt.xlabel('Distance au SSP')
    plt.ylabel("Station d'arrivée")
    plt.xlim(xlim[0],xlim[1])    
    if trace_moy:
        plt.axvline(data[cols[1]].mean(), color='r', ls='--',
            label=f"Moyenne = {data[cols[1]].mean():.2f}")
    plt.legend()
    return plt.show()


def trace_precision_train(data, cols=cols_precision_train,
                                    color=None, figsize=(8,10),
                                    xlim=(1,-1), trace_moy=True,
                                    category=None,
                                    sort=True):

    fig = plt.figure(figsize=figsize)

    # if category is used to plot against categorical data, color parameter
    # is omitted to let seaborn choos the color palette
    if category:
        color=None

    # If sort is True, the order used is increasing order of train number
    if sort:
        ordre=data[cols[0]].sort_values().unique()
    else:
        ordre=None

    # ci parameter set to None disables the plotting of confidence intervals
    # dodge parameter set to False prevents having a bar for each 'y' value
    # and for each 'hue' category: here the 'hue' parameter is just used to
    # color code each bar depending on category of hue.
    sns.barplot(data=data, y=cols[0], x=cols[1],
                color=color, orient='h', hue=category, ci=None, dodge=False,
                order=ordre)
    plt.title(f"Précision moyenne d'arrêt par train", size=16)
    plt.xlim(xlim[0],xlim[1])
    if trace_moy:
    # let plot the mean for distance to SSP across all data set
        plt.axvline(data[cols[1]].mean(), color='r', ls='--',
            label=f"Moyenne = {data[cols[1]].mean():.2f}")
    plt.legend()
    plt.xlabel('Distance au SSP')
    plt.ylabel("Numéro du train")
    return plt.show()

def trace_dispersion_train(data, cols=cols_precision_train,
                             color=None, figsize=(8,10), xlim=(0.5,0),
                             trace_moy=True, category=None,
                             sort=True):

    fig = plt.figure(figsize=figsize)

    # if category is used to plot against categorical data, color parameter
    # is omitted to let seaborn choos the color palette
    if category:
        color=None

    # If sort is True, the order used is the increasing order of train number
    if sort:
        ordre=data[cols[0]].sort_values().unique()
    else:
        ordre=None

    # dodge parameter set to False prevents having a bar for each 'y' value
    # and for each 'hue' category: here the 'hue' parameter is just used to
    # color code each bar depending on category of hue.
    sns.boxplot(data=data, x=cols[1], y=cols[0], color=color,
                hue=category, orient='h', order=ordre, dodge=False)
    plt.title("Répartition statistique des arrêts par train", size=16)
    plt.xlabel('Distance au SSP')
    plt.ylabel("Numéro du train")
    plt.xlim(xlim[0],xlim[1])    
    if trace_moy:
        plt.axvline(data[cols[1]].mean(), color='r', ls='--',
            label=f"Moyenne = {data[cols[1]].mean():.2f}")
    plt.legend()
    return plt.show()


"""
initial code developped by Tiphaine GRAILLAT for ALSTOM
"""
