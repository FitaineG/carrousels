# -*- coding: utf-8 -*-
"""

Ceci est un package python qui contient les classes Track et Carrousel

"""

__version__ = 0.1
__author__ = "Tiphaine GRAILLAT for ALSTOM"

import pandas as pd
import tracks
from xlrd import XLRDError

cols_EB_drop = ['id', 'EB_TRAIN_ARRET', 'Abscisse_Temps', 'EB_CAUSE',
                'Distance_from_train_front_end_to_stop_wished',
                'Distance_from_train_front_end_to_stop_proposed',
                'Message_counter_OMAP', 'LOG_OMAP']

movement_cols_name = {'Control_software': 'SoftwareVersion',
                'NumTrain': 'Train',
                'Stop_Station': 'StopStation',
                'Distance_from_train_front_end_to_stop_wished': 'DistanceSSP',
                'Duree_MVT': 'Duree'}

cols_movement_drop=['Id_mvt', 'Date_Start', 'Abscisse_T_Start',
                'Abscisse_T_Stop',
                'Distance_from_train_front_end_to_stop_proposed',
                'LOG_OMAP', 'Message_counter_OMAP', 'Row_Id_start',
                'Row_Id_stop', 'Row_Id_max_kph', 'Row_Id_start_after_stop',
                'RSD_1_Vital_opening_command',
                'DistanceToSSP', 'DistanceToSSP__1cycle_avant_vitesse_nulle',
                'DistanceToSSP_avg__10cycles_avant_vitesse_nulle']

class Track:
    
    def __init__(self, trackdef=LilleL1, tracklist=None, pexMovements=None,
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


class Carrousel:

    def __init__(self, track, source, context, build=None, dataPath=None):
        self.track = track
        self.dataPath = dataPath
        self.source = source
        self.context = context
        self.build = build

    def get_movement_data(self, path=None, format='xls', sheet=0,
                          dropna=True, rename_cols=movement_cols_name,
                          drop_cols=cols_movement_drop):
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

        if format == 'xls':
            try:
                data = pd.read_excel(path, sheet_name=sheet)
            except XLRDError:
                message = (f"!! ERREUR !! Le classeur '{sheet}' " +
                           "n'existe pas dans le fichier excel")
                print(message)
                raise XLRDError(message)
        elif format == 'csv':
            if sheet != 0:
                print(f"'{sheet}' sheet not taken into account for 'csv' file")
            data = pd.read_csv(path)
        else:
            print(f"'{format}' files are not a valid data format")
            return

        # Define new column for mvt from mvt start to mvt stop
        data['Movement'] = (data['Start_Station'].str[:-2] + '-' +
                             data['Stop_Station'].str[:-2])
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
            data['Version'] = 'v' + data['Control_software'].str.replace(
                " ","").str.replace("_1_", "b").str[1:] + (
                    '_' + self.source + '_' + self.context)
        # determine type of movement
        if self.track:
            data['typeMovement'] = data['Movement'].apply(lambda x:
                            determine_type_movement(x))

        if drop_cols:
        # suppression des colonnes
            data = data.drop(columns=drop_cols)

        if rename_cols:
        # renaming des colonnes
            data = data.rename(columns=rename_cols)

        if dropna:
        # Suppression des valeurs manquantes (NaN)
            data = data.dropna()

        data['CorrectDocking'] = data['Train_correctly_docked'] != 0

        print(f"{data.shape[0]} mouvements importés")
        self.movements = data.reset_index()


    def determine_type_movement(self, mouvement):
        # force mouvement sous forme de string
        mouvement = str(mouvement)
        if mouvement in self.track['intersectors']:
            return 'intersecteur'
        elif (mouvement[-4:] in self.track['terminus']) or (
              mouvement[-3:] in self.track['terminus']):
            return 'terminus'
        elif (mouvement in self.track['turnbacks'])
            return 'retournement'
        else:
            return 'standard'



    def get_EB_data(self, path=None, format='xls', sheet=2, dropna=True,
                    moving=True, drop_cols=cols_EB_drop):
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

        if format == 'xls':
            try:
                data = pd.read_excel(path, sheet_name=sheet)
            except XLRDError:
                message = (f"!! ERREUR !! Le classeur '{sheet}' " +
                           "n'existe pas dans le fichier excel")
                print(message)
                raise XLRDError(message)
        elif format == 'csv':
            if sheet != 0:
                print(f"'{sheet}' sheet not taken into account for 'csv' file")
            data = pd.read_csv(path)
        else:
            print(f"'{format}' files are not a valid data format")
            return

        if drop_cols:
            data = data.drop(columns=drop_cols)

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
            data['Version'] = 'v' + data['Control_software'].str.replace(
                " ","").str.replace("_1_", "b").str[1:] + (
                    '_' + self.source + '_' + self.context)
        if moving:
            print(f"{data.shape[0]} EB en mouvement importés")
        else:
            print(f"{data.shape[0]} EB importés, dont certains peuvent être ",
                  end='')
            print("à l'arrêt")
        self.emergencyBrakings = data.reset_index()
