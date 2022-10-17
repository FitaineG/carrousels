# -*- coding: utf-8 -*-
"""

Ceci est un package python qui contient les classes Track et Carrousel

"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from xlrd import XLRDError
from carrouselsAnalysis.dataFormat import carrouselFormat


cols_precision_station = ['StopStation', 'DistanceSSP', 'TypeMovement']

cols_precision_train = ['Train', 'DistanceSSP']

cols_tps_parcours = ['Movement', 'Duree', 'TypeMovement']

cols_EB_by_time = ['Date', 'EBCause']

cols_EB_by_KP = ['EB_trackID', 'EB_KP']


class Track:
    
    def __init__(self, trackdef, tracklist=None, pexMovements=None,
                 turnbacks=None, intersectors=None, terminus=None):
        if trackdef:
            self.tracklist = trackdef['tracklist']
            self.pexMovements = trackdef['pexMovements']
            self.turnbacks = trackdef['turnbacks']
            self.intersectors = trackdef['intersectors']
            self.terminus = trackdef['terminus']
        else:
            if tracklist:
                self.tracklist = tracklist
            if pexMovements:
                self.pexMovements = pexMovements
            if turnbacks:
                self.turnbacks = turnbacks
            if intersectors:
                self.intersectors = intersectors
            if terminus:
                self.terminus = terminus

        return print('Track créée')


class Carrousel:

    def __init__(self, source, context, track=None, build=None, dataPath=None):
        self.track = track
        self.dataPath = dataPath
        self.source = source
        self.context = context
        self.build = build
        return print('Carrousel créé')

    def get_movement(self, path=None, fileFormat='xls', sheet=0,
                     dropna=True, dataFormat='MG', rename_cols=None,
                     drop_cols=None):
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

        if dataFormat:
            drop_cols = carrouselFormat[dataFormat]['movement_cols_drop']
            rename_cols  = carrouselFormat[dataFormat]['movement_cols_name']

        if drop_cols:
        # suppression des colonnes
            data = data.drop(columns=drop_cols)

        if rename_cols:
        # renaming des colonnes
            data = data.rename(columns=rename_cols)

        if dropna:
        # Suppression des valeurs manquantes (NaN)
            data = data.dropna()
        
        # Define new column for mvt from mvt start to mvt stop
        data['Movement'] = (data['StartStation'].str[:-2] + '-' +
                             data['StopStation'].str[:-2])
        # Define new columns for source, and context
        data['Source'] = self.source
        data['Context'] = self.context
        if self.build:
        # use concatenation of 'build', 'source' and 'context' to uniquely
        # identify the data
            data['Version'] = (self.build + '_' + self.source + '_'
                              + self.context)
        else:
        # use the 'Control_software' of data concatenated with 'source'
        # and 'context' to uniquely identify the data
            data['Version'] = 'v' + data['SoftwareVersion'].str.replace(
                " ","").str.replace("_1_", "b").str[1:] + (
                    '_' + self.source + '_' + self.context)
        # determine type of movement
        if self.track:
            data['TypeMovement'] = data['Movement'].apply(
            lambda x: self.__determine_type_movement(x))



        data['CorrectDocking'] = data['TrainCorrectlyDocked'] != 0

        print(f"{data.shape[0]} mouvements importés")
        self.movements = data.reset_index()


    def update_track(self, track):
        self.track = track

    def define_type_movement(self):
        self.movements['TypeMovement'] = self.movements['Movement'].apply(
            lambda x: self.__determine_type_movement(x))
        
    def __determine_type_movement(self, mouvement):
        # force mouvement sous forme de string
        mouvement = str(mouvement)
        if mouvement in self.track.intersectors:
            return 'intersecteur'
        elif (mouvement[-4:] in self.track.terminus) or (
              mouvement[-3:] in self.track.terminus):
            return 'terminus'
        elif (mouvement in self.track.turnbacks):
            return 'retournement'
        else:
            return 'standard'



    def get_EB(self, path=None, fileFormat='xls', sheet=2, dropna=True,
               moving=True, dataFormat='MG', drop_cols=None, filter_col=None,
               rename_cols=None):
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

        if dataFormat:
            drop_cols = carrouselFormat[dataFormat]['EB_cols_drop']
            rename_cols  = carrouselFormat[dataFormat]['EB_cols_name']
            filter_col = carrouselFormat[dataFormat]['EB_filter']

        if drop_cols:
            data = data.drop(columns=drop_cols)

        if filter_col:
            data = data[data[filter_col].isnull() == False]
            data = data.drop(columns=filter_col)

        if rename_cols:
        # renaming des colonnes
            data = data.rename(columns=rename_cols)

        if dropna:
            # Suppression des valeurs manquantes (NaN)
            data = data.dropna()

        if moving:
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
        else:
        # use the 'Control_software' of data concatenated with 'source'
        # and 'context' to uniquely identify the data
            data['Version'] = 'v' + data['SoftwareVersion'].str.replace(
                " ","").str.replace("_1_", "b").str[1:] + (
                    '_' + self.source + '_' + self.context)
        if moving:
            print(f"{data.shape[0]} EB en mouvement importés")
        else:
            print(f"{data.shape[0]} EB importés, dont certains peuvent être ",
                  end='')
            print("à l'arrêt")
        self.emergencyBrakings = data.reset_index()


    def trace_precision_station(self, cols=cols_precision_station,
                                color='tab:blue', figsize=(8,10), xlim=(1,-1),
                                trace_moy=True,
                                category=cols_precision_station[2],
                                sort=True, **kwargs):
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

        fig = plt.figure(figsize=figsize)

        # if category is used to plot against categorical data, color parameter
        # is omitted to let seaborn choos the color palette
        if category:
            color=None

        # If sort is True, the order used is alphabetical order of stop stations
        if sort:
            ordre=self.movements[cols[0]].sort_values().unique()
        else:
            ordre=None


        orientation = kwargs.pop('orient', 'h')

        ci = kwargs.pop('ci', False)

        dodge = kwargs.pop('dodge', False)

        # ci parameter set to None disables the plotting of confidence intervals
        # dodge parameter set to False prevents having a bar for each 'y' value
        # and for each 'hue' category: here the 'hue' parameter is just used to
        # color code each bar depending on category of hue.
        sns.barplot(data=self.movements, y=cols[0], x=cols[1],
                    color=color, orient=orientation, hue=category, ci=ci,
                    dodge=dodge, order=ordre, **kwargs)
        plt.title(f"Précision moyenne d'arrêt par station", size=16)
        plt.xlim(xlim[0],xlim[1])
        if trace_moy:
        # let plot the mean for distance to SSP across all data set
            plt.axvline(self.movements[cols[1]].mean(), color='r', ls='--',
                label=f"Moyenne = {self.movements[cols[1]].mean():.2f}")
        plt.legend()
        plt.xlabel('Distance au SSP')
        plt.ylabel("Station d'arrivée")
        return plt.show()

    def trace_dispersion_station(self, cols=cols_precision_station,
                                 color='tab:blue', figsize=(8,10), xlim=(1,-1),
                                 trace_moy=True,
                                 category=cols_precision_station[2],
                                 sort=True, **kwargs):
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
            ordre=self.movements[cols[0]].sort_values().unique()
        else:
            ordre=None

        orientation = kwargs.pop('orient', 'h')

        dodge = kwargs.pop('dodge', False)

        # dodge parameter set to False prevents having a bar for each 'y' value
        # and for each 'hue' category: here the 'hue' parameter is just used to
        # color code each bar depending on category of hue.
        sns.boxplot(data=self.movements, x=cols[1], y=cols[0], color=color,
                    hue=category, orient=orientation, order=ordre, dodge=dodge,
                    **kwargs)
        plt.title("Répartition statistique des arrêts par station", size=16)
        plt.xlabel('Distance au SSP')
        plt.ylabel("Station d'arrivée")
        plt.xlim(xlim[0],xlim[1])    
        if trace_moy:
            plt.axvline(self.movements[cols[1]].mean(), color='r', ls='--',
                label=f"Moyenne = {self.movements[cols[1]].mean():.2f}")
        plt.legend()
        return plt.show()


    def trace_precision_train(self, cols=cols_precision_train, color='tab:blue',
                              figsize=(8,10), xlim=(1,-1), trace_moy=True,
                              category=None, sort=True, **kwargs):
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
            ordre=self.movements[cols[0]].sort_values().unique()
        else:
            ordre=None

        orientation = kwargs.pop('orient', 'h')

        ci = kwargs.pop('ci', False)

        dodge = kwargs.pop('dodge', False)
        

        # ci parameter set to None disables the plotting of confidence intervals
        # dodge parameter set to False prevents having a bar for each 'y' value
        # and for each 'hue' category: here the 'hue' parameter is just used to
        # color code each bar depending on category of hue.
        sns.barplot(data=self.movements, y=cols[0], x=cols[1],
                    color=color, orient=orientation, hue=category, ci=ci,
                    dodge=dodge, order=ordre, **kwargs)
        
        plt.title(f"Précision moyenne d'arrêt par train", size=16)
        plt.xlim(xlim[0],xlim[1])
        if trace_moy:
        # let plot the mean for distance to SSP across all data set
            plt.axvline(self.movements[cols[1]].mean(), color='r', ls='--',
                label=f"Moyenne = {self.movements[cols[1]].mean():.2f}")
        plt.legend()
        plt.xlabel('Distance au SSP')
        plt.ylabel("Numéro du train")
        return plt.show()

    def trace_dispersion_train(self, cols=cols_precision_train,
                               color='tab:blue', figsize=(8,10), xlim=(1,-1),
                               trace_moy=True, category=None, sort=True,
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

        fig = plt.figure(figsize=figsize)

        # if category is used to plot against categorical data, color parameter
        # is omitted to let seaborn choos the color palette
        if category:
            color=None

        # If sort=True, the order used is the increasing order of train number
        if sort:
            ordre=self.movements[cols[0]].sort_values().unique()
        else:
            ordre=None

        orientation = kwargs.pop('orient', 'h')

        dodge = kwargs.pop('dodge', False)

        # dodge parameter set to False prevents having a bar for each 'y' value
        # and for each 'hue' category: here the 'hue' parameter is just used to
        # color code each bar depending on category of hue.
        sns.boxplot(data=self.movements, x=cols[1], y=cols[0], color=color,
                    hue=category, orient=orientation, order=ordre, dodge=dodge,
                    **kwargs)
        plt.title("Répartition statistique des arrêts par train", size=16)
        plt.xlabel('Distance au SSP')
        plt.ylabel("Numéro du train")
        plt.xlim(xlim[0],xlim[1])    
        if trace_moy:
            plt.axvline(self.movements[cols[1]].mean(), color='r', ls='--',
                label=f"Moyenne = {self.movements[cols[1]].mean():.2f}")
        plt.legend()
        return plt.show()

    def trace_EB_by_KP(self, cols=cols_EB_by_KP, bins=100,
                       color='tab:blue', figsize=(20,8), ymax=5, **kwargs):
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
        plt.title("Nombre d'EB par KP", size = 16)
        if not self.track.tracklist:
            message = """Pour tracer ce graphe, le carrousel doit être associé à
            une track contenant une liste de voies"""
            return message

        nb_graphs = len(self.track.tracklist)
        for i, t in enumerate(self.track.tracklist):
            # creating as many subplots as the number of tracks declared
            plt.subplot(nb_graphs,1,i+1)
            plt.hist(self.emergencyBrakings.loc[
                self.emergencyBrakings[cols[0]] == t[1], cols[1]],
                     bins=bins, color=color, **kwargs)
            plt.xticks()
            plt.gca().invert_xaxis()
            plt.ylim(0,ymax)
            plt.ylabel(f"{t[0]}")
        plt.xlabel("Points kilométriques")
        plt.tight_layout()
        return plt.show()

    def trace_EB_by_time(self, cols=cols_EB_by_time, bins='10T',
                         color='tab:blue', figsize=(20,4),
                         ymax=10, **kwargs):
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

        self.emergencyBrakings['Time'] = pd.to_datetime(
            self.emergencyBrakings[cols[0]])
        # previous line shall be moved to import function for EBs
        data_by_time = self.emergencyBrakings.set_index('Time').sort_index()
        data_by_time = data_by_time.resample(bins)[cols[1]].count()

        fig = plt.figure(figsize=figsize)
        sns.barplot(x=data_by_time.index, y=data_by_time.values, color=color)
        plt.xticks(rotation=90)
        plt.title("Nombre d'EB par période", size = 16)
        plt.ylim(0,ymax)
        plt.ylabel("Nombre d'EB")
        plt.xlabel("Temps")
        return plt.show()

    def trace_tps_parcours(self, cols=cols_tps_parcours,
                           category=cols_tps_parcours[2], color='tab:blue',
                           figsize=(16,5), ylim=None, sort=True, **kwargs):
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
            ordre = self.movements[cols[0]].sort_values().unique()
        else:
            ordre = None

        if category:
            color= None

        ci = kwargs.pop('ci', False)

        dodge = kwargs.pop('dodge', False)

            
        sns.barplot(data=self.movements, x=cols[0], y=cols[1], hue=category,
                    color=color, order=ordre, dodge=dodge, ci=ci, **kwargs)
        plt.title("Temps de parcours moyen par mouvement", size=16)
        plt.xticks(rotation=90)
        return plt.show()

    def trace_disp_tps_parcours(self, cols=cols_tps_parcours,
                                category=cols_tps_parcours[2], color='tab:blue',
                                figsize=(16,5), ylim=None, sort=True, **kwargs):
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
            ordre = self.movements[cols[0]].sort_values().unique()
        else:
            ordre = None

        if category:
            color= None

        dodge = kwargs.pop('dodge', False)
            
        sns.boxplot(data=self.movements, x=cols[0], y=cols[1], hue=category,
                    color=color, order=ordre, dodge=dodge, **kwargs)
        plt.title("Dispersion des temps de parcours par mouvement", size=16)
        plt.ylim(ylim)
        plt.xticks(rotation=90)
        return plt.show()
