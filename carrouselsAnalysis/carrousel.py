# -*- coding: utf-8 -*-
"""

Ceci est un package python qui contient les classes Track et Carrousel

"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
from xlrd import XLRDError
from itertools import chain
from carrouselsAnalysis.dataFormat import carrouselFormat
from carrouselsAnalysis import (titleFontSize, xaxisFontSize,
                                        yaxisFontSize)        


decoratorsList = ['legend', 'legendTitle', 'locLegend', 'legendLabels',
                  'supTitle', 'supTitleSize', 'supTitleY',
                  'title', 'titleSize',
                  'xLabel', 'xLabelSize',
                  'xticks', 'xticksRotation', 'xlim', 'invertXaxis',
                  'yLabel', 'yLabelSize',
                  'yticks', 'yticksRotation', 'ylim', 'invertYaxis']

cols_arrets_rates = ['CorrectDocking']

cols_precision_station = ['StopStation', 'DistanceSSP']

cols_precision_train = ['Train', 'DistanceSSP']

cols_tps_parcours = ['Movement', 'Duree', 'TypeMovement']

cols_EB_by_time = ['DateEB', 'EBCause']

cols_EB_by_KP = ['EBTrackId', 'EB_KP']


class Track:
    
    def __init__(self, trackdef, maintracklist=None, nominalMovements=None,
                 turnbacks=None, intersectors=None, terminus=None,
                 platforms=None):
        if trackdef:
            self.maintracklist = trackdef['maintracklist']
            self.nominalMovements = trackdef['nominalMovements']
            self.turnbacks = trackdef['turnbacks']
            self.intersectors = trackdef['intersectors']
            self.terminus = trackdef['terminus']
            self.platforms = trackdef['platforms']
        else:
            self.maintracklist = maintracklist
            self.nominalMovements = nominalMovements
            self.turnbacks = turnbacks
            self.intersectors = intersectors
            self.terminus = terminus
            self.platforms = platforms

        return print('Track créée')


class Carrousel:

    def __init__(self, source, context, track=None, build=None, dataPath=None,
                dataFormat=None):
        self.track = track
        self.dataPath = dataPath
        self.source = source
        self.context = context
        self.build = build
        self.dataFormat = dataFormat
        return print('Carrousel créé')

    def get_movement(self, path=None, fileFormat='xls', sheet=None,
                     dropna=False, dataFormat=None, rename_cols=None,
                     drop_cols=None, stationRegex=None):
        """import movement data from path into a pandas.DataFrame adding source,
        context and version as new columns to uniquely identify imported data
        and label graphs.
        Data file can be in two formats, xls (default) or csv.
        Rows with missing data are dropped if specified (True by default)
        'build' can be specified to name specific build instead of using
        control_software column

        Parameters
        ----------
        path : string
            path to the data file to get.
        format : string, optional
            format of data file. The default is 'xls'.
            Other option is 'csv'
        sheet : string, optional
            sheet name to import. The default is 0 (first sheet)
        source : string
            source of data as string. Will be added to the data as new col.
            Typically 'FIVP', 'Site'.
        context : string
            context of data as a string. Will be added to the data as new col.
            Typically 'mono-train', 'multi-trains'.
        build : string, optional
            name of specific build. The default is None.
        dropna : bool, optional
            whether or not to drop rows with missing data.
            The default is True.
        mapping_interstations : dict, optional
            dict providing list of strings corresponding to each one of the
            following movement types: 'interstation', 'retournement' or
            'terminus'.
            To disable mapping, use {}.
            The default value is 'interstations' defined in this module.
        rename_cols : dict, optional
            provides mapping to rename columns.
            To disable renaming, use {}.
            The default value is 'movement_cols_name' defined in this module.
        drop_cols : list, optional
            list of columns to drop.
            To disable, use [].
            The default value is 'cols_movement_drop' defined in this module.

        Returns
        -------
        pandas.DataFrame
            the data as a pandas.DataFrame with additional columns describing
            the source and context of the data

        Raises
        ------
        XLRDError
            For error in case the 'sheet' input does not match with an actual
            sheet in the excel file from path.


        """
        # if path not defined as input for this method, use the dataPath
        # inherited from class Carrousel
        if not path:
            path = self.dataPath
        
        if (not dataFormat) and self.dataFormat:
            dataFormat = self.dataFormat
            
        # si le format de data est défini, alors on utilise les données
        # drop_cols et rename_cols du format choisi
        if dataFormat:
            drop_cols = carrouselFormat[dataFormat]['movement_cols_drop']
            rename_cols  = carrouselFormat[dataFormat]['movement_cols_name']
            stationRegex = carrouselFormat[dataFormat]['stationRegex']
            if not sheet:
                sheet=0

        if fileFormat == 'xls':
            try:
                data = pd.read_excel(path, sheet_name=sheet)
            except XLRDError:
                message = (f"!! ERREUR !! Le classeur '{sheet}' " +
                           "n'existe pas dans le fichier excel")
                print(message)
                raise XLRDError(message)
        elif fileFormat == 'csv':
            if sheet != 0:
                print(f"'{sheet}' sheet not taken into account for 'csv' file")
            data = pd.read_csv(path)
        else:
            print(f"'{fileFormat}' files are not a valid data format")
            return

        if drop_cols:
        # suppression des colonnes
            for col in drop_cols:
                if col in data.columns:
                    data = data.drop(columns=[col])

        if rename_cols:
        # renaming des colonnes
            data = data.rename(columns=rename_cols)

        if 'EBCause' in data.columns:
            data['EBCause'] = data['EBCause'].fillna('')
        
        if dropna:
        # Suppression des valeurs manquantes (NaN)
            data = data.dropna()
        
        # Define new columns for source, and context
        data['Source'] = self.source
        data['Context'] = self.context
        if self.build:
        # use concatenation of 'build', 'source' and 'context' to uniquely
        # identify the data
            data['Version'] = (self.build + '_' + self.source + '_'
                              + self.context)
        elif 'SoftwareVersion' in data.columns:
        # use the 'Control_software' of data concatenated with 'source'
        # and 'context' to uniquely identify the data
            data['Version'] = 'v' + data['SoftwareVersion'].str.replace(
                " ","").str.replace("_1_", "b").str[1:] + (
                    '_' + self.source + '_' + self.context)
        else:
            print('No `version` attribute could be computed')
        
        if ('StartStation' in data.columns) and ('StopStation' in
                                                 data.columns):
            data['StartPosition'] = data['StartStation'].apply(
                lambda x: self.__determine_upstream_downstream(x,
                                                               stationRegex))
            data['StartStation'] = data['StartStation'].str.extract(
                                        stationRegex)['station']
            data['StopPosition'] = data['StopStation'].apply(
                lambda x: self.__determine_upstream_downstream(x,
                                                               stationRegex))
            data['StopStation'] = data['StopStation'].str.extract(
                                        stationRegex)['station']
        # Define new column for mvt from mvt start to mvt stop
            data['Movement'] = (data['StartStation'] + '-' +
                                data['StopStation'])
            # determine type of movement
            if self.track:
                data['TypeMovement'] = data['Movement'].apply(
                        lambda x: self.__determine_type_movement(x))
                
            data['DestType'] = data['StopStation'].apply(
                lambda x: self.__determine_dest_type(x))
                
        if 'TrainCorrectlyDocked' in data.columns:
        # define Correct Docking status
            data['CorrectDocking'] = data['TrainCorrectlyDocked'] != 0
            
        if 'DistanceSSP' in data.columns:
            # define new column with abs value of `DistanceSSP`
            data['absoluteDistanceSSP'] = data['DistanceSSP'].abs()
            
        if ('NVCommandSup40p' in data.columns) and (
            'NVCommandSup50p' in data.columns):
            # define new column for line resistivity state
            data['resistivityStateDetailed'] = data.apply(
                lambda row: self.__determine_resistivity_state(row,
                                                            detailed=True),
                axis=1)
            data['resistivityStateDual'] = data.apply(
                lambda row: self.__determine_resistivity_state(row,
                                                            detailed=False),
                axis=1)
        
        if 'StopTrackId' in data.columns:        
            data['StopTrackId'] = data['StopTrackId'].apply(
                    lambda x: self.__transform_track_id(x))
            
            data['StopTrackName'] = data['StopTrackId'].apply(
                lambda x: self.__get_track_name_from_id(x))
        
        # define movements attribute based on data pd.DataFrame with reset index
        self.movements = data.reset_index()
        
        # if track is defined for this carrousel, define nominal movements
        # based on pexMovements attribute of track
        if self.track and ('Movement' in data.columns):
            self.nominalMovements = data[data['Movement'].isin(
                list(chain(*self.track.nominalMovements.values())))]
            
            # print number of movements imported
            return print(f"{self.movements.shape[0]} mouvements importés" +
                        f" dont {self.nominalMovements.shape[0]} mouvements" +
                        f" du service nominal")
        else:
            return print(f"{self.movements.shape[0]} mouvements importés")


    def update_track(self, track):
        self.track = track

    def define_type_movement(self):
        self.movements['TypeMovement'] = self.movements['Movement'].apply(
            lambda x: self.__determine_type_movement(x))
        
    def create_nominalMovements(self):
        if self.track:
            self.nominalMovements = self.movements[
                self.movements['Movement'].isin(
                    list(chain(*self.track.nominalMovements.values())))]
            return print(f"{self.nominalMovements.shape[0]} mouvements" +
                        f" du service nominal importés")
        else:
            return print('No track defined for this carrousel')
    
    def __determine_resistivity_state(self, row, detailed):
        if row['NVCommandSup40p'] == 0:
            return 'receptive'
        elif (row['NVCommandSup50p'] == 0) and detailed:
            return 'partiellement'
        else:
            return 'non-receptive'
    
    def __determine_type_movement(self, mouvement):
        # force mouvement sous forme de string
        mouvement = str(mouvement)
        if mouvement in self.track.intersectors:
            return 'intersecteur'
        elif (mouvement[-4:] in self.track.terminus) or (
              mouvement[-3:] in self.track.terminus):
            return 'terminus'
        elif (mouvement in list(chain(*self.track.turnbacks.values()))):
            return 'retournement'
        else:
            return 'standard'

    def __determine_upstream_downstream(self, station, regexStation):
        station = str(station)
        match = re.search(regexStation, station)
        if match and match.group('pos') == '_0':
            return 'amont'
        elif match and match.group('pos') == '_1':
            return 'aval'
        else:
            return
        
    def __determine_dest_type(self, StopStation):
        StopStation = str(StopStation)
        if StopStation in self.track.platforms:
            return 'plateforme'
        else:
            return 'stabling'
        
    def __transform_track_id(self, trackId):
        trackId = str(trackId)
        for id in [self.track.maintracklist[i]['trackId']
                   for i in range(len(self.track.maintracklist))]:
            if trackId == str(id - 3000):
                return str(id)
            elif (trackId.find(str(id)) != -1):
                return str(id)
        return trackId
              
    def __get_track_name_from_id(self, trackId):
        trackId = str(trackId)
        for i, id in enumerate([self.track.maintracklist[i]['trackId']
                        for i in range(len(self.track.maintracklist))]):
            if trackId == str(id):
                return self.track.maintracklist[i]['trackName']
        
        return 'unknown'
        
        
    def get_EB(self, path=None, fileFormat='xls', sheet=None, dropna=False,
               moving=True, dataFormat=None, drop_cols=None,
               filter_col='TrainEB', rename_cols=None):
        """import EB data from path into a pandas.DataFrame adding source,
        context and version as new columns to uniquely identify imported data
        and label graphs.
        Data file can be in two formats, xls (default) or csv.
        Rows with missing data are dropped if specified (True by default)
        'build' can be specified to name specific build instead of using
        control_software column

        Parameters
        ----------
        path : string
            path to the data file to get.
        source : string
            source of data as string. Will be added to the data as new col.
            Typically 'FIVP', 'Site'.
        context : string
            context of data as a string. Will be added to the data as new col.
            Typically 'mono-train', 'multi-trains'.
        format : string, optional
            format of data file. The default is 'xls'.
            Other option is 'csv'
        sheet : string, optional
            sheet name to import. The default is 0 (first sheet)
        build : string, optional
            name of specific build. The default is None.
        dropna : bool, optional
            whether or not to drop rows with missing data.
            The default is True.
        en_mouvement : bool, optional
            whether or not import only EBs which occured at non null speed.
            The default is True.
        drop_cols : list of strings, optional
            List of column names to drop.
            To disable, use [].
            The default is cols_EB_drop.

        Returns
        -------
        pandas.DataFrame
            the EB data as a pandas.DataFrame with additional columns describing
            the source and context of the EB data

        Raises
        ------
        XLRDError
            For error in case the 'sheet' input does not match with an actual
            sheet in the excel file from path.


        """
        # if path not defined as input for this method, use the dataPath
        # inherited from class Carrousel
        if not path:
            path = self.dataPath
            
        if (not dataFormat) and self.dataFormat:
            dataFormat = self.dataFormat

        # si le format de data est défini, alors on utilise les données
        # drop_cols, rename_cols et filter_cols du format choisi
        if dataFormat:
            drop_cols = carrouselFormat[dataFormat]['EB_cols_drop']
            rename_cols  = carrouselFormat[dataFormat]['EB_cols_name']
            if not sheet:
                if dataFormat == 'MG':
                    sheet=2
                elif dataFormat == 'Fabisis':
                    if moving:
                        sheet=1
                    else:
                        sheet=2
        
        if dataFormat != 'MG':
            filter_col = None
            
        if fileFormat == 'xls':
            try:
                data = pd.read_excel(path, sheet_name=sheet)
            except XLRDError:
                message = (f"!! ERREUR !! Le classeur '{sheet}' " +
                           "n'existe pas dans le fichier excel")
                print(message)
                raise XLRDError(message)
        elif fileFormat == 'csv':
            if sheet != 0:
                print(f"'{sheet}' sheet not taken into account for 'csv' file")
            data = pd.read_csv(path)
        else:
            print(f"'{fileFormat}' files are not a valid data format")
            return

        # suppression des colonnes
        if drop_cols:
            for col in drop_cols:
                if col in data.columns:
                    data = data.drop(columns=[col])

        if rename_cols:
        # renaming des colonnes
            data = data.rename(columns=rename_cols)            

        # on filtre sur les valeurs non nulles de la colonne filtre
        # puis on supprime la colonne filtre dont on n'aura plus besoin
        if filter_col:
            data = data[data[filter_col].isnull() == False]
        
        if dataFormat == 'MG':
            data = data.drop(columns=['TrainEB', 'TrainImmo'])
        elif dataFormat == 'Fabisis':
            data['addEBCause'] = data['addEBCause'].fillna(0)
            
        if dropna:
        # Suppression des valeurs manquantes (NaN)
            data = data.dropna()

        if moving and ('Speed' in data.columns):
        # suppression des EB à vitesse nulle
            data = data[data['Speed'] != 0]
        # Define new columns for source, and context
        data['Source'] = self.source
        data['Context'] = self.context
        
        if self.build:
        # use concatenation of 'build', 'source' and 'context' to uniquely
        # identify the data
            data['Version'] = (self.build + '_' + self.source + '_'
                              + self.context)
        elif 'SoftwareVersion' in data.columns:
        # use the 'Control_software' of data concatenated with 'source'
        # and 'context' to uniquely identify the data
            data['Version'] = 'v' + data['SoftwareVersion'].str.replace(
                " ","").str.replace("_1_", "b").str[1:] + (
                    '_' + self.source + '_' + self.context)
        else:
            print('No `version` attribute could be computed')
        
        if 'DateEB' in data.columns:
            data['Time'] = pd.to_datetime(
                data['DateEB'])
              
        if 'EBTrackId' in data.columns:        
            data['EBTrackId'] = data['EBTrackId'].apply(
                    lambda x: self.__transform_track_id(x))
              
            data['EBTrackName'] = data['EBTrackId'].apply(
                lambda x: self.__get_track_name_from_id(x))
            
        self.emergencyBrakings = data.reset_index()
        
        if moving and ('Speed' in data.columns):
            return print(f"{data.shape[0]} EB en mouvement importés")
        else:
            return print(f"{data.shape[0]} EB importés, dont certains" +
                         f" peuvent être à l'arrêt")
        
    def __extract_decorators(self, decoratorsList=decoratorsList, **kwargs):
        
        decorators = {}
        for d in decoratorsList:
            decorators[d] = kwargs.pop(d, None)

        return decorators, kwargs
    

    def __set_decorators(self, decorators):

        from carrouselsAnalysis import (titleFontSize, xaxisFontSize,
                                        yaxisFontSize)        

        d = decorators

        # legend
        if d['legendLabels'] and d['legend']:
            plt.legend(title=d['legendTitle'], loc=d['locLegend'],
                      labels=d['legendLabels'])
        elif d['legend']:
            plt.legend(title=d['legendTitle'], loc=d['locLegend'])
        # supTitle
        if d['supTitleSize'] and d['supTitle']:
            plt.suptitle(d['supTitle'], size=d['supTitleSize'],
                         y=d['supTitleY'])
        elif d['supTitle']:
            plt.suptitle(d['supTitle'], size=titleFontSize,
                        y=d['supTitleY'])
        # title
        if d['titleSize']:
            plt.title(d['title'], size=d['titleSize'])
        else:
            plt.title(d['title'], size=titleFontSize)
        # xLabel
        if d['xLabelSize']:
            plt.xlabel(d['xLabel'], size=d['xLabelSize'])
        elif d['xLabel']:
            plt.xlabel(d['xLabel'], size=xaxisFontSize)
        # yLabel
        if d['yLabelSize']:
            plt.ylabel(d['yLabel'], size=d['yLabelSize'])
        elif d['yLabel']:
            plt.ylabel(d['yLabel'], size=yaxisFontSize)
        # xlim
        if d['xlim']:
            plt.xlim(d['xlim'][0], d['xlim'][1])
        elif d['invertXaxis']:
            plt.gca().invert_xaxis()
        # xticks
        if d['xticks']:
            plt.xticks(d['xticks'], rotation=d['xticksRotation'])
        elif d['xticksRotation'] != None:
            plt.xticks(rotation=d['xticksRotation'])
        # ylim
        if d['ylim']:
            plt.ylim(d['ylim'][0], d['ylim'][1])
        elif d['invertYaxis']:
            plt.gca().invert_yaxis()
        # yticks
        if d['yticks']:
            plt.yticks(d['yticks'], rotation=d['yticksRotation'])
        elif d['yticksRotation']:
            plt.yticks(rotation=d['yticksRotation'])
        
        return
    
    def trace_precision_station(self, x='DistanceSSP', y='StopStation',
                                platformsOnly=True,
                                color='tab:blue', figsize=(8,10),
                                category=None,
                                sort=True, trace_moy=True,
                                **kwargs):
        """plots a horizontal barplot graph showing the mean stopping accuracy
        by station

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
        
        defaultDecorators={
            'legend': True,
            'locLegend': 'best',
            'title': "Précision moyenne des arrêts par station",
            'xLabel': "Distance au SSP",
            'yLabel': "Station d'arrivée",
            'xlim': (1,-1)}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        

        fig = plt.figure(figsize=figsize)

        # if category is used to plot against categorical data, color parameter
        # is omitted to let seaborn choos the color palette
        if category:
            color=None

        data = self.movements
        
        if platformsOnly:
            data = data[data['DestType'] == 'plateforme']    
        
        # If sort is True, the order used is alphabetical order of stop stations
        if sort:
            ordre = ([stat for stat in self.track.platforms
                     if stat in data['StopStation'].unique()] +
                     [stat for stat in data[y].sort_values().unique()
                      if stat not in self.track.platforms])
        else:
            ordre=None

        orientation = kwargs.pop('orient', 'h')

        ci = kwargs.pop('ci', False)

        dodge = kwargs.pop('dodge', True)

        # ci parameter set to None disables the plotting of confidence intervals
        # dodge parameter set to False prevents having a bar for each 'y' value
        # and for each 'hue' category: here the 'hue' parameter is just used to
        # color code each bar depending on category of hue.
        sns.barplot(data=data, y=y, x=x,
                    color=color, orient=orientation, hue=category, ci=ci,
                    dodge=dodge, order=ordre, **kwargs)
        
        if trace_moy:
        # let plot the mean for distance to SSP across all data set
            plt.axvline(data[x].mean(), color='r', ls='--',
                label=f"Moyenne = {data[x].mean():.2f}")
        
        self.__set_decorators(decorators)

        return plt.show()

    def trace_dispersion_station(self, x='DistanceSSP', y='StopStation',
                        platformsOnly=True,
                        color='tab:blue', figsize=(8,10),
                        category=None,
                        sort=True, trace_moy=True,
                        **kwargs):
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
        
        defaultDecorators={
            'legend': True,
            'locLegend': 'best',
            'title': "Répartition statistique des arrêts par station",
            'xLabel': "Distance au SSP",
            'yLabel': "Station d'arrivée",
            'xlim': (1.3,-1.3)}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        
        fig = plt.figure(figsize=figsize)

        # if category is used to plot against categorical data, color parameter
        # is omitted to let seaborn choos the color palette
        if category:
            color=None
            
        data = self.movements
        
        if platformsOnly:
            data = data[data['DestType'] == 'plateforme']

        # If sort is True, the order used is alphabetical order of stop stations
        if sort:
            ordre = ([stat for stat in self.track.platforms
                     if stat in data['StopStation'].unique()] +
                     [stat for stat in data[y].sort_values().unique()
                      if stat not in self.track.platforms])
        else:
            ordre=None

        orientation = kwargs.pop('orient', 'h')

        dodge = kwargs.pop('dodge', True)

        # dodge parameter set to False prevents having a bar for each 'y' value
        # and for each 'hue' category: here the 'hue' parameter is just used to
        # color code each bar depending on category of hue.
        sns.boxplot(data=data, x=x, y=y, color=color,
                    hue=category, orient=orientation, order=ordre, dodge=dodge,
                    **kwargs)
 
        if trace_moy:
            plt.axvline(data[x].mean(), color='r', ls='--',
                label=f"Moyenne = {data[x].mean():.2f}")

        self.__set_decorators(decorators)

        return plt.show()


    def trace_precision_train(self, x='DistanceSSP', y='Train',
                              platformsOnly=True,
                              color='tab:blue', figsize=(8,10),
                              category=None,
                              sort=True, trace_moy=True,
                              **kwargs):
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
        
        if platformsOnly:
            defaultTitle = "Précision moyenne des arrêts en station par train"
        else:
            defaultTitle = "Précision moyenne des arrêts par train"
        
        defaultDecorators={
            'legend': True,
            'locLegend': 'best',
            'title': defaultTitle,
            'xLabel': "Distance au SSP",
            'yLabel': "Numéro du train",
            'xlim': (1,-1)}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]

        fig = plt.figure(figsize=figsize)

        # if category is used to plot against categorical data, color parameter
        # is omitted to let seaborn choos the color palette
        if category:
            color=None
            
        data = self.movements
        
        if platformsOnly:
            data = data[data['DestType'] == 'plateforme']

        # If sort is True, the order used is increasing order of train number
        if sort:
            ordre=data[y].sort_values().unique()
        else:
            ordre=None

        orientation = kwargs.pop('orient', 'h')

        ci = kwargs.pop('ci', False)

        dodge = kwargs.pop('dodge', True)

        # ci parameter set to None disables the plotting of confidence intervals
        # dodge parameter set to False prevents having a bar for each 'y' value
        # and for each 'hue' category: here the 'hue' parameter is just used to
        # color code each bar depending on category of hue.
        sns.barplot(data=data, y=y, x=x,
                    color=color, orient=orientation, hue=category, ci=ci,
                    dodge=dodge, order=ordre, **kwargs)
        
        if trace_moy:
        # let plot the mean for distance to SSP across all data set
            plt.axvline(data[x].mean(), color='r', ls='--',
                label=f"Moyenne = {data[x].mean():.2f}")

        self.__set_decorators(decorators)
        
        return plt.show()

    def trace_dispersion_train(self, x='DistanceSSP', y='Train',
                               platformsOnly=True,
                               color='tab:blue', figsize=(8,10),
                               category=None,
                               sort=True, trace_moy=True,
                               **kwargs):
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
        
        if platformsOnly:
            defaultTitle = "Répartition des arrêts en station par train"
        else:
            defaultTitle = "Répartition des arrêts par train"
        
        defaultDecorators={
            'legend': True,
            'locLegend': 'best',
            'title': defaultTitle,
            'xLabel': "Distance au SSP",
            'yLabel': "Numéro du train",
            'xlim': (1.3,-1.3)}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]

        fig = plt.figure(figsize=figsize)

        # if category is used to plot against categorical data, color parameter
        # is omitted to let seaborn choos the color palette
        if category:
            color=None
            
        data = self.movements
        
        if platformsOnly:
            data = data[data['DestType'] == 'plateforme']

        # If sort=True, the order used is the increasing order of train number
        if sort:
            ordre=data[y].sort_values().unique()
        else:
            ordre=None

        orientation = kwargs.pop('orient', 'h')

        dodge = kwargs.pop('dodge', True)

        # dodge parameter set to False prevents having a bar for each 'y' value
        # and for each 'hue' category: here the 'hue' parameter is just used to
        # color code each bar depending on category of hue.
        sns.boxplot(data=data, x=x, y=y, color=color,
                    hue=category, orient=orientation, order=ordre, dodge=dodge,
                    **kwargs)

        if trace_moy:
            plt.axvline(data[x].mean(), color='r', ls='--',
                label=f"Moyenne = {data[x].mean():.2f}")

        self.__set_decorators(decorators)
        
        return plt.show()

    def trace_EB_by_KP(self, x='EB_KP', y='EBTrackName', bins=100,
                    color='tab:blue', figsize=(20, 8),
                    **kwargs):
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
        
        defaultDecorators={
            'legend': False,
            'supTitle': "Répartition des FUs par KP",
            'supTitleSize': 20,
            'supTitleY': 1.02,
            'xLabel': "Points kilométriques",
            'invertXaxis': True,
            'xticksRotation': 30,
            'ylim': (0, 5)}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        
        fig = plt.figure(figsize=figsize)

        if not self.track.maintracklist:
            message = """Pour tracer ce graphe, le carrousel doit être associé à
            une track contenant une liste de voies"""
            return message

        nb_graphs = len(self.track.maintracklist)
        
        xlim=decorators['xlim']
        
        if xlim:
            kpRange=(min(xlim), max(xlim))
        
        for i, t in enumerate(self.track.maintracklist):
            # creating as many subplots as the number of tracks declared
            plt.subplot(nb_graphs,1,i+1)
            if not xlim:
                kpRange = (0, t['trackKPmax'])
            plt.hist(self.emergencyBrakings.loc[
                self.emergencyBrakings[y] == t['trackName'], x],
                     bins=bins, color=color, range=kpRange, **kwargs)

            d = {'yLabel': f"{t['trackName']}",
                 'yLabelSize': decorators['yLabelSize'],
                 'ylim': decorators['ylim'],
                 'invertYaxis': decorators['invertYaxis'],
                 'yticks': decorators['yticks'],
                 'yticksRotation': decorators['yticksRotation'],
                 'xlim': decorators['xlim'],
                 'invertXaxis': decorators['invertXaxis'],
                 'xticks': decorators['xticks'],
                 'xticksRotation': decorators['xticksRotation']}
    
            deco, _ = self.__extract_decorators(**d)
            
            self.__set_decorators(deco)

        plt.tight_layout()

        d = {'supTitle': decorators['supTitle'],
             'supTitleSize': decorators['supTitleSize'],
             'supTitleY': decorators['supTitleY'],
             'xLabel': decorators['xLabel'],
             'xLabelSize': decorators['xLabelSize'],
             'legend': decorators['legend'],
             'legendTitle': decorators['legendTitle'],
             'locLegend': decorators['locLegend']}
    
        deco, _ = self.__extract_decorators(**d)
        
        self.__set_decorators(deco)
        
        return plt.show()

    def trace_EB_by_time(self, x='DateEB', bins='10T',
                    color='tab:blue', figsize=(20,4),
                    **kwargs):
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
        
        defaultDecorators={
            'legend': False,
            'title': "Répartition des FUs dans le temps",
            'xLabel': "Temps",
            'xticksRotation': 90,
            'yLabel': "Nombre de FUs",
            'ylim': (0, 10)}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]

        data_by_time = self.emergencyBrakings.set_index('Time').sort_index()
        data_by_time = data_by_time.resample(bins)[x].count()

        fig = plt.figure(figsize=figsize)
        
        sns.barplot(x=data_by_time.index, y=data_by_time.values, color=color,
                   **kwargs)

        self.__set_decorators(decorators)
        
        return plt.show()

    def trace_tps_parcours(self, x='Movement', y='Duree',
                        category='TypeMovement', nominalService=True,
                        deleteNegTimes=True, color='tab:blue',
                        figsize=(16,5), sort=True, function='mean',
                        trace_moy=True, **kwargs):
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

        defaultYLabel = 'Durée (s)'
        
        if function == 'mean':
            defaultTitle = "Temps de parcours moyen par mouvement"
            estimator= np.mean
        elif function == 'min':
            defaultTitle = "Temps de parcours mini par mouvement"
            estimator = np.min
        elif function == 'max':
            defaultTitle = "Temps de parcours maxi par mouvement"
            estimator = np.max
        elif function == 'std':
            defaultTitle = "Écart type des temps de parcours par mouvement"
            defaultYLabel = "Écart type de la distribution de durée"
            estimator = np.std
        elif function == 'mean-min':
            defaultTitle = "Différence entre temps de parcours moyen et mini par mouvement"
            defaultYLabel = "Différence de durée (s)"
            estimator = lambda x: np.mean(x) - np.min(x)
        elif function == 'median-min':
            defaultTitle = "Différence entre temps de parcours médian et mini par mouvement"
            defaultYLabel = "Différence de durée (s)"
            estimator = lambda x: np.median(x) - np.min(x)
        elif function == 'median':
            defaultTitle = "Temps de parcours median par mouvement"
            estimator = np.median
        else:
            defaultTitle = "Temps de parcours"
            estimator = function
            
        
        defaultDecorators={
            'legend': True,
            'title': defaultTitle,
            'xLabel': "Mouvement",
            'xticksRotation': 90,
            'yLabel': defaultYLabel}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]

        fig = plt.figure(figsize=figsize)

        if nominalService:
            data=self.nominalMovements
        else:
            data=self.movements[self.movements['Movement'].notnull()]
            
        if deleteNegTimes:
            data = data[data[y] > 0]
        
        if sort:
            nominalMovementsList = [pex for pexlist in 
                    self.track.nominalMovements.values() for pex in pexlist]
            ordre = ([move for move in nominalMovementsList
                      if move in data[x].unique()] +
                     [move for move in data[x].unique()
                      if move not in nominalMovementsList])
        else:
            ordre = None

        if category:
            color= None

        ci = kwargs.pop('ci', False)

        dodge = kwargs.pop('dodge', False)
        
        sns.barplot(data=data, x=x, y=y, hue=category,
                    color=color, order=ordre, dodge=dodge, ci=ci,
                    estimator=estimator, **kwargs)
        
        if trace_moy and (function == 'mean-min') or (function == 'median-min'):
            times = data.groupby(x)[y].agg(estimator).reset_index()
            lostTimeMean = times[y].mean()
            plt.axhline(lostTimeMean, color='r', ls='--',
                label=f"Temps moyen perdu par station {lostTimeMean:.1f}s")
                        
        self.__set_decorators(decorators)

        return plt.show()

    def trace_disp_tps_parcours(self, x='Movement', y='Duree',
                        category='TypeMovement', nominalService=True,
                        deleteNegTimes=True, color='tab:blue',
                        figsize=(16,5), sort=True,
                        **kwargs):
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
        
        defaultDecorators={
            'legend': False,
            'title': "Répartition statistique des temps de parcours",
            'xLabel': "Mouvement",
            'xticksRotation': 90,
            'yLabel': "Durée du mouvement",
            'ylim': (40, 110)}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]

        fig = plt.figure(figsize=figsize)

        if nominalService:
            data=self.nominalMovements
        else:
            data=self.movements[self.movements['Movement'].notnull()]
            
        if deleteNegTimes:
            data = data[data[y] > 0]
        
        if sort:
            nominalMovementsList = [pex for pexlist in 
                    self.track.nominalMovements.values() for pex in pexlist]
            ordre = ([move for move in nominalMovementsList
                      if move in data[x].unique()] +
                     [move for move in data[x].unique()
                      if move not in nominalMovementsList])
        else:
            ordre = None

        if category:
            color= None

        dodge = kwargs.pop('dodge', False)
            
        sns.boxplot(data=data, x=x, y=y, hue=category,
                    color=color, order=ordre, dodge=dodge, **kwargs)


        self.__set_decorators(decorators)
 
        return plt.show()

    def camembert_arrets_rates(self, cols=cols_arrets_rates, figsize=(5,5),
                            title="Proportion d'arrêts ratés ",
                            resistivityState='all', detailedState=True):
        
        fig = plt.figure(figsize=figsize)
        
        self.__plot_pie_missed_stops(cols, resistivityState,
                                     detailedState=detailedState,
                                     title=title)
        
        return plt.show()

    def __plot_pie_missed_stops(self, cols, resistivityState, detailedState,
                                title="Proportion d'arrêts ratés ",
                                labels=True):

        if detailedState:
            col='resistivityStateDetailed'
        else:
            col='resistivityStateDual'
        
        if resistivityState == 'all':
            addTitle = 'au global'
            data = self.movements
        elif resistivityState == 'receptive':
            addTitle = 'en ligne réceptive'
            data= self.movements[
                self.movements[col] == resistivityState]
        elif resistivityState == 'non-receptive':
            addTitle = 'en ligne non réceptive'
            data= self.movements[
                self.movements[col] == resistivityState]
        elif resistivityState == 'partiellement':
            addTitle = 'en ligne partiellement réceptive'
            data = self.movements[
                self.movements[col] == resistivityState]
        elif isinstance(resistivityState, list):
            addTitle = (f"en ligne {resistivityState[0]}" +
                        f" et {resistivityState[1]}")
            data = self.movements[
                self.movements[col].isin(resistivityState)]
            
        nbTrains = data['Train'].unique().shape[0]
        nbStops = data.shape[0]
        pieData = data[cols[0]].value_counts()
            
        if labels == False:
            labelList=None
        elif pieData.index[0] == True:
            labelList=['Docking: OK', 'Docking: KO']
        else:
            labelList=['Docking: KO', 'Docking: OK']
        
        explosion = [0.1]
        if len(pieData) == 2:
            explosion = [0.1]*2
        pieData.plot.pie(autopct='%.1f%%',
                    labels=labelList,
                    pctdistance=0.6, explode=explosion,
                    textprops={'fontsize': 14, 'weight': 'bold'})
        
        plt.title(title + addTitle, size = 16, weight='bold')
        plt.ylabel('')
        plt.xlabel(f"Total de {nbStops} arrêts pour " +
                f"{nbTrains}" + f" trains", size=16, weight='bold')
    
    def synthese_arrets_rates(self, cols=cols_arrets_rates, detailedState=True,
                              figsize=(20,5),
                              title="Synthèse des arrêts ratés",
                              locLegend='right'):
        
        fig = plt.figure(figsize=figsize)
        
        if detailedState:
            col = 'resistivityStateDetailed'
        else:
            col = 'resistivityStateDual'

        listStates = ['all']
        listStates = (listStates +
                      list(self.movements[col].unique()))
        nbplots =  len(listStates)
        
        for i, state in zip(range(nbplots), listStates): 
            plt.subplot(1, nbplots, i+1)
            self.__plot_pie_missed_stops(cols, resistivityState=state,
                                         detailedState=detailedState,
                                         labels=False, title='')
        
        plt.suptitle(title, size=20, weight='bold', y=1.02)
        fig.legend(['Arrêt OK', 'Arrêt raté'], loc=locLegend, fontsize=14)
        
        return plt.show()
    
    def histo_precision(self, x='DistanceSSP', platformsOnly=True,
                        xRange=(-1.3, 1.3),
                        bins=30, y='count', style='bar', alpha=1,
                        figsize=(8,5), color='tab:blue',
                        **kwargs):
        
        defaultDecorators={
            'legend': False,
            'title': "Répartition statistique des arrêts en station",
            'xLabel': "Distance au SSP (m)"}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        
        if isinstance(bins, list):
            decorators['xticks'] = bins
        
        if xRange:
            data=self.movements[
                self.movements[x].between(xRange[0], xRange[1])]
        else:
            data=self.movements
        
        if platformsOnly:
            data = data[data['DestType'] == 'plateforme']
        
        xlim = decorators['xlim']
        if not xlim:
            xlim=(xRange[1], xRange[0])
        
        if y == 'freq':
            if data.shape[0] != 0:
                weights = [100/data.shape[0]] * data.shape[0]
            else:
                weights = None
            decorators['yLabel'] = "Frequence d'occurence (%)"
        else:
            weights=None
            decorators['yLabel'] = "Nombre d'occurences"
        
        fig = plt.figure(figsize=figsize)
        
        plt.hist(x=x, range=xRange, bins=bins, color=color, weights=weights,
                 data=data, histtype=style, alpha=alpha, **kwargs)
                 
        self.__set_decorators(decorators)
        
        return plt.show()
    
    def histo_precision_compare(self, dataCompare,
                        x='DistanceSSP', platformsOnly=True,
                        xRange=(-1.3, 1.3),
                        bins=30, y='count', 
                        globalFreq = True,
                        style='bar', alpha=None,
                        figsize=(8,5),
                        colors=['tab:blue', 'tab:red', 'tab:green',
                                'tab:purple', 'tab:orange'],
                        **kwargs):
        
        defaultDecorators={
            'legend': True,
            'locLegend': 'best',
            'title': "Répartition statistique des arrêts en station",
            'xLabel': "Distance au SSP (m)"}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        
        if isinstance(bins, list):
            decorators['xticks'] = bins
        
        if xRange:
            data=self.movements[
                self.movements[x].between(xRange[0], xRange[1])]
        else:
            data=self.movements
            
        if platformsOnly:
            data = data[data['DestType'] == 'plateforme']

        listValues = list(data[dataCompare].unique())
        nbCat = len(listValues)
        if nbCat > 5:
            return print('Number of supported categories is 5')
        
        if decorators['legend']:
            decorators['legendTitle']=dataCompare
            decorators['legendlabels']=listValues
        
        alpha = 1/nbCat
        
        datas=[]
        for i in range(nbCat):
            datas.append(data.loc[data[dataCompare] == listValues[i]])
        
        xlim = decorators['xlim']
        if not xlim:
            xlim=(xRange[1], xRange[0])    
        
        if style == 'barstacked':
            globalFreq = True
        
        weights = []
        if y == 'freq':
            if globalFreq == True:
                decorators['yLabel'] = "Freq. occurence globale (%)"
                for i in range(nbCat):
                    if data.shape[0] != 0:
                        weights.append([100/data.shape[0]] *
                                       datas[i].shape[0])
                    else:
                        weights.append(None)
            else:
                decorators['yLabel'] = "Freq. occurence par cat. (%)"
                for i in range(nbCat):
                    if datas[i].shape[0] != 0:
                        weights.append([100/datas[i].shape[0]] *
                                       datas[i].shape[0])
                    else:
                        weights.append(None)
        else:
            if style == 'barstacked':
                weights = None
            else:
                weights=[None] * nbCat
            decorators['yLabel'] = "Nb occurences"
            
        if style == 'barstacked':
            
            fig = plt.figure(figsize=figsize)
            plt.hist(x=[data[x] for data in datas],
                 range=xRange, bins=bins, color=colors[:nbCat],
                 weights=weights, histtype=style, alpha=1,
                 label = listValues, **kwargs)
            
            self.__set_decorators(decorators)
                       
        else:
            fig = plt.figure(figsize=figsize)
            for i in range(nbCat):
                plt.hist(x=x, range=xRange, bins=bins, color=colors[i],
                     weights=weights[i], data=datas[i],
                     histtype=style, alpha=alpha,
                     label = listValues[i], **kwargs)
            
            self.__set_decorators(decorators)
        
#        if isinstance(bins, list):
#            plt.xticks(bins)
        
        return plt.show()
    
    
    def histo_precision_filter(self, dataFilter, filterValue,
                        x='DistanceSSP', platformsOnly=True,
                        xRange=(-1.3, 1.3),
                        bins=30, y='count', 
                        style='bar', alpha=1,
                        figsize=(8,5),
                        color='tab:blue',
                        **kwargs):
        
        defaultDecorators={
            'legend': True,
            'locLegend': 'best',
            'title': "Répartition statistique des arrêts en station",
            'xLabel': "Distance au SSP (m)"}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        
        if isinstance(bins, list):
            decorators['xticks'] = bins
            
        if decorators['legend']:
            decorators['legendTitle'] = dataFilter
        
        if xRange:
            data=self.movements[
                self.movements[x].between(xRange[0], xRange[1])]
        else:
            data=self.movements
            
        if platformsOnly:
            data = data[data['DestType'] == 'plateforme']
            
        if dataFilter and (filterValue != None):
            data = data[data[dataFilter] == filterValue]
            
        xlim = decorators['xlim']
        if not xlim:
            xlim=(xRange[1], xRange[0])
        
        if y == 'freq':
            if data.shape[0] != 0:
                weights = [100/data.shape[0]] * data.shape[0]
            else:
                weights = None
            decorators['yLabel'] = "Frequence d'occurence (%)"
        else:
            weights=None
            decorators['yLabel'] = "Nombre d'occurences"
        
        fig = plt.figure(figsize=figsize)
        
        plt.hist(x=x, range=xRange, bins=bins, color=color, weights=weights,
                 data=data, histtype=style, alpha=alpha, label = filterValue,
                 **kwargs)
                 
        self.__set_decorators(decorators)
        
#        if isinstance(bins, list):
#            plt.xticks(bins)
        
#        if legend:
#            plt.legend(title=dataFilter)
        
        return plt.show()
    
    def missed_stops_pct_by_station(self, x='CorrectDocking',
                            cat='StopStation',
                            platformsOnly=True,
                            color='tab:blue',
                            figsize=(20,8),
                            **kwargs):
        
        defaultDecorators={
            'legend': False,
            'title': "Pourcentage d'arrêts ratés par station",
            'xLabel': "Station d'arrivée",
            'xticksRotation': 90,
            'yLabel': "Arrêts ratés (%)"}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        
        fig = plt.figure(figsize=figsize)
        
        self.__missed_stops_pct_by_cat(x, cat, platformsOnly, color, **kwargs)
        
        self.__set_decorators(decorators)
        
        return plt.show()
    
    def missed_stops_pct_by_train(self, x='CorrectDocking',
                            cat='Train',
                            platformsOnly=False,
                            color='tab:blue',
                            figsize=(20,8),
                            **kwargs):
        
        if platformsOnly:
            defaultTitle = "Pourcentage d'arrêts ratés en station par train"
        else:
            defaultTitle = "Pourcentage d'arrêts ratés par train"
        
        defaultDecorators={
            'legend': False,
            'title': defaultTitle,
            'xLabel': "Numéro du train",
            'xticksRotation': 0,
            'yLabel': "Arrêts ratés (%)"}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        
        fig = plt.figure(figsize=figsize)
        
        self.__missed_stops_pct_by_cat(x, cat, platformsOnly, color, **kwargs)
        
        self.__set_decorators(decorators)
        
        return plt.show()
    
    def __missed_stops_pct_by_cat(self, x, cat, platformsOnly, color,
                                  **kwargs):
        
        data = self.movements
        
        if platformsOnly:
            data = data[data['DestType'] == 'plateforme']

        sort = kwargs.pop('sort', True)
        
        if sort and cat == 'StopStation':
            ordre = ([stat for stat in self.track.platforms
                     if stat in data[cat].unique()] +
                     [stat for stat in data[cat].unique()
                      if stat not in self.track.platforms])
        elif sort and cat == 'Train':
            ordre = data[cat].sort_values().unique()
        else:
            ordre=None
        
        missed_stops_pct_by_cat = data.groupby(cat)[x].value_counts(
            normalize=True).unstack()[False].fillna(0).round(3)*100

        sns.barplot(x=missed_stops_pct_by_cat.index,
                    y=missed_stops_pct_by_cat.values,
                    order=ordre,
                    color=color, **kwargs)

    
    def commercial_speed_by_track(self, trackname='StopTrackName',
                        groupby='Movement', times='Duree',
                        dwells=None, timeOffset=3,
                        deleteNegTimes=True,
                        colors=None,
                        figsize=(8,5), function=['min', 'median'],
                        **kwargs):
        
        if timeOffset != 0:
            defaultLegendTitle = f'Tps parcours + {timeOffset}s'
        else:
            defaultLegendTitle = 'Tps parcours'
        
        defaultDecorators={
            'legend': True,
            'locLegend': 'upper center',
            'legendTitle': defaultLegendTitle,
            'title': "Vitesse commerciale par voie",
            'xLabel': "Track",
            'xticksRotation': 0,
            'yLabel': "Vitesse commerciale (km/h)",
            'ylim': (28,35)}
        
        decorators, kwargs = self.__extract_decorators(**kwargs)
        
        for d in defaultDecorators:
            if decorators[d] == None:
                decorators[d] = defaultDecorators[d]
        
        if not self.nominalMovements.empty:
            data = self.nominalMovements
        else:
            print('Nominal movements shall be defined to compute commercial speed')
            return
        
        tracklist=self.track.maintracklist
        nbtrackslist=range(len(tracklist))
        
        if not isinstance(function, list):
            function = [function]
        
        if (colors != None) and len(function) > len(colors):
            colors=None
        
        if deleteNegTimes:
            data = data[data[times] > 0]
        
        running_times = data.groupby([groupby, trackname])[times].agg(function).reset_index()
        
        nbNominalMovements = 0
        for nominalMoves in self.track.nominalMovements.values():
            nbNominalMovements += len(nominalMoves)
        
        if running_times.shape[0] != nbNominalMovements:
            print(f'nb mouvements uniques: {running_times.shape[0]}')
            print(f'nb mouvements nominaux: {nbNominalMovements}')
            print('Il manque des mouvements dans les données' +
                  ' pour calculer la vitesse commerciale')
            return
        
        running_times[function] += timeOffset
        
        speeds = running_times.groupby(trackname)[function].sum()
       
        speeds['trackDistance'] = [tracklist[i]['trackNominalRunningDistance']
                                  for i in nbtrackslist]
        
        if not dwells:
            dwells = [tracklist[i]['trackNominalDwellTimes'] for i in nbtrackslist]
                                   
        speeds['dwells'] = dwells
        
        for col in function:
            speeds[col] = speeds['trackDistance'] / (
                           speeds[col] + speeds['dwells']) *3.6
        
        speeds = speeds.reset_index()
        
        speeds = speeds.drop(columns=(['trackDistance', 'dwells']))

        speeds.plot(x=trackname, kind='bar', figsize=figsize, color=colors,
                    **kwargs)
        
        functionNames=[]
        for f in function:
            if f == 'min':
                functionNames.append('Minis')
            elif f == 'mean':
                functionNames.append('Moyens')
            elif f == 'max':
                functionNames.append('Maxis')
            elif f == 'median':
                functionNames.append('Medians')
            else:
                functionNames.append(f)
        
        decorators['legendLabels'] = functionNames
        
        self.__set_decorators(decorators)
        
        return plt.show()