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

cols_tps_parcours = ['Mouvement', 'Duree', 'TypeMouvement']

cols_EB_by_time = ['Date_Time', 'EB_COUNT']

cols_EB_by_KP = ['Start_track_id', 'Start_abscissa']

def trace_precision_station(data, cols=cols_precision_station,
                                    color=None, figsize=(8,10),
                                    xlim=(1,-1), trace_moy=True,
                                    category=cols_precision_station[2],
                                    sort=True, **kwargs):
    """plots a horizontal barplot graph showing the mean stopping accuracy by
    station

    Parameters
    ----------
    data : pd.Dataframe

    cols : list of strings, optional
        list of labels used to plot on x, y axis and by category.
        (Default value = cols_precision_station)
    color : string, optional
        color to be used to plot. Overriden to False if category is defined
        (Default value = None)
    figsize : tuple of int or float, optional
        defines the size of plot
        (Default value = (8,10))
    xlim : tuple of int or float
        defines the limits for x axis
        (Default value = (1,-1))
    trace_moy : bool, optional
        defines whether or not to plot a vertical red dotted line showing the
        overall stopping accuracy.
        (Default value = True)
    category : string, optional
        label to be used for visualizing category of plotted data
        (Default value = cols_precision_station[2])
    sort : bool, optional
        if True, stations on y axis are sorted alphabetically
        (Default value = True)
    **kwargs :


    Returns
    -------
    plots a barplot graph
        

    
    """

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


#    if 'orient' in kwargs:
#        orientation = kwargs['orient']
#    else:
    orientation = kwargs.pop('orient', 'h')

#    if 'ci' in kwargs:
#        ci = kwargs['ci']
#    else:
    ci = kwargs.pop('ci', False)

#    if 'dodge' in kwargs:
#        dodge = kwargs['dodge']
#    else:
    dodge = kwargs.pop('dodge', False)
        
    # ci"""" parameter set to None disables the plotting of confidence intervals
    # dodge parameter set to False prevents having a bar for each 'y' value
    # and for each 'hue' category: here the 'hue' parameter is just used to
    # color code each bar depending on category of hue.
    sns.barplot(data=data, y=cols[0], x=cols[1],
                color=color, orient=orientation, hue=category, ci=ci,
                dodge=dodge, order=ordre, **kwargs)
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
    """

    Parameters
    ----------
    data :

    cols :
         (Default value = cols_precision_station)
    color :
         (Default value = None)
    figsize :
         (Default value = (8,10))
    xlim :
         (Default value = (0.5,0))
    trace_moy :
         (Default value = True)
    category :
         (Default value = cols_precision_station[2])
    sort :
         (Default value = True)

    Returns
    -------

    """

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
    """

    Parameters
    ----------
    data :

    cols :
        (Default value = cols_precision_train)
    color :
        (Default value = None)
    figsize :
        (Default value = (8,10))
    xlim :
         (Default value = (1,-1))
    trace_moy :
        (Default value = True)
    category :
        (Default value = None)
    sort :
        (Default value = True)

    Returns
    -------

    
    """

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
    """

    Parameters
    ----------
    data :

    cols :
        (Default value = cols_precision_train)
    xlim :
        (Default value = (0.5,0))
    0) (unused?) :

    trace_moy :
        (Default value = True)
    category :
        (Default value = None)
    sort :
        (Default value = True)
    color :
         (Default value = None)
    figsize :
         (Default value = (8,10))

    Returns
    -------

    
    """

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

def trace_EB_by_KP(data, cols=cols_EB_by_KP, bins=100,
                   color='tab:blue', figsize=(20,8), ylim=None):
    """

    Parameters
    ----------
    data :

    cols :
        (Default value = cols_EB_by_KP)
    bins :
        (Default value = 100)
    color :
         (Default value = 'tab:blue')
    figsize :
         (Default value = (20,8))
    ylim :
         (Default value = None)

    Returns
    -------

    
    """

    fig = plt.figure(figsize=figsize)

    plt.subplot(2,1,1)
    plt.hist(data.loc[data[cols[0]] == 3, cols[1]], bins=bins, color=color)
    plt.xticks()
    plt.title("Nombre d'EB par KP", size = 16)
    plt.gca().invert_xaxis()
    plt.ylim(ylim)
    plt.ylabel("Nombre d'EB")
    plt.subplot(2,1,2)
    plt.hist(data.loc[data[cols[0]] == 2, cols[1]], bins=bins, color=color)
    plt.xticks()
    plt.ylim(ylim)
    plt.gca().invert_xaxis()
    plt.ylabel("Nombre d'EB")
    plt.xlabel("KP")
    plt.tight_layout()
    return plt.show()

def trace_EB_by_time(data, cols=cols_EB_by_time, bins='10T',
                      color='tab:blue', figsize=(20,4), ylim=None):
    """

    Parameters
    ----------
    data :

    cols :
        (Default value = cols_EB_by_time)
    bins :
        (Default value = '10T')
    color :
        (Default value = 'tab:blue')
    figsize :
        (Default value = (20,4))
    4) (unused?) :

    ylim :
        (Default value = None)

    Returns
    -------

    
    """

    data['Time'] = pd.to_datetime(data[cols[0]])
    data_by_time = data.set_index('Time').sort_index()
    data_by_time = data_by_time.resample(bins)[cols[1]].count()

    fig = plt.figure(figsize=figsize)
    sns.barplot(x=data_by_time.index, y=data_by_time.values, color=color)
    plt.xticks(rotation=90)
    plt.title("Nombre d'EB par période de temps", size = 16)
    plt.ylim(ylim)
    plt.ylabel("Nombre d'EB")
    plt.xlabel("Temps")
    return plt.show()

def trace_tps_parcours(data, cols=cols_tps_parcours,
                       category=cols_tps_parcours[2], color=None,
                       figsize=(16,5), ylim=None, sort=True):
    """

    Parameters
    ----------
    data :

    cols :
        (Default value = cols_tps_parcours)
    category :
        (Default value = cols_tps_parcours[2])
    color :
        (Default value = None)
    figsize :
        (Default value = (16,5))
    ylim :
        (Default value = None)
    sort :
        (Default value = True)

    Returns
    -------

    
    """
    
    fig = plt.figure(figsize=figsize)
    
    if sort:
        ordre = data[cols[0]].sort_values().unique()
    else:
        ordre = None
    
    if category:
        color= None
    
    sns.barplot(data=data, x=cols[0], y=cols[1], hue=category, color=color,
                order=ordre, dodge=False, ci=False)
    plt.title("Temps de parcours moyen par mouvement", size=16)
    plt.xticks(rotation=90)
    return plt.show()
    
def trace_disp_tps_parcours(data, cols=cols_tps_parcours,
                            category=cols_tps_parcours[2],
                      color=None, figsize=(16,5), ylim=None, sort=True):
    """

    Parameters
    ----------
    data :

    cols :
        (Default value = cols_tps_parcours)
    category :
        (Default value = cols_tps_parcours[2])
    color :
        (Default value = None)
    figsize :
         (Default value = (16,5))
    ylim :
        (Default value = None)
    sort :
        (Default value = True)

    Returns
    -------

    
    """
    
    fig = plt.figure(figsize=figsize)
    
    if sort:
        ordre = data[cols[0]].sort_values().unique()
    else:
        ordre = None
    
    sns.boxplot(data=data, x=cols[0], y=cols[1], hue=category, color=color,
                order=ordre, dodge=False)
    plt.title("Dispersion des temps de parcours par mouvement", size=16)
    plt.ylim(ylim)
    plt.xticks(rotation=90)
    return plt.show()

"""
initial code developped by Tiphaine GRAILLAT for ALSTOM
"""
