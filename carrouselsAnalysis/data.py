# -*- coding: utf-8 -*-
"""

Ceci est un package python qui contient les fonctions
d'importation des données de carrousels

Il contient les fonctions suivantes:
    get_movement_data: importe les data sur les mouvements
    get_EB_data: importe les data sur les EB
    determine_type_movement: catégorise les mouvements en utilisant
        le dictionnaire des types de mouvements fourni

"""

import pandas as pd
from xlrd import XLRDError

intersecteurs = ['HDV1-PDB1', 'PDB2-HDV2', 'MAR1-FIV1', 'FIV2-MAR2',
                 'RIH1-REP1', 'REP2-RIH2', 'REP1-GAM1', 'GAM2-REP2']
terminus = ['CAL1', '4C2']
retournements = ['CALOV1', '4CEV2']

interstations = {'intersecteurs': intersecteurs,
                 'terminus': terminus,
                 'retournements': retournements}

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


def get_movement_data(path, source, context, format='xls', sheet=0, 
                       build=None, dropna=True,
                       mapping_interstations=interstations,
                       rename_cols=movement_cols_name,
                       drop_cols=cols_movement_drop):
    """
    import movement data from path into a pandas.DataFrame adding source,
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
        following movement types: 'interstation', 'retournement' or 'terminus'.
        To disable mapping, use {}.
        The default value is 'interstations' defined in this module.
    rename_cols : dict, optional
        provides mapping to rename columns.
        To disable renaming, use {}.
        The default value is 'movement_cols_name' defined in this module.
    drop_cols : list, optional
        list of columns to drop.
        To disable, use [].
        The default value is 'cols_movement drop' defined in this module.
    
    
    Raises
    ------
    XLRDError
        For error in case the 'sheet' input does not match with an actual
        sheet in the excel file from path.


    Returns
    -------
    pandas.DataFrame
        the data as a pandas.DataFrame with additional columns describing
        the source and context of the data

    """
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
    data['Mouvement'] = (data['Start_Station'].str[:-2] + '-' +
                         data['Stop_Station'].str[:-2])
    # Define new columns for source, and context
    data['Source'] = source
    data['Contexte'] = context
    if build:
    # use concatenation of 'build', 'source' and 'context' to uniquely
    # identify the data
        data['Version'] = build + '_' + source + '_' + context
    else:
    # use the 'Control_software' of data concatenated with 'source'
    # and 'context' to uniquely identify the data
        data['Version'] = 'v' + data['Control_software'].str.replace(
            " ","").str.replace("_1_", "b").str[1:] + (
                '_' + source + '_' + context)
    # determine type of movement
    if mapping_interstations:
        data['TypeMouvement'] = data['Mouvement'].apply(lambda x:
                determine_type_movement(x, mapping_interstations))
    
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
    return data.reset_index()


def determine_type_movement(mouvement, mapping):
    # force mouvement sous forme de sring
    mouvement = str(mouvement)
    if mouvement in mapping['intersecteurs']:
        return 'intersecteur'
    elif (mouvement[-4:] in mapping['terminus']) or (
            mouvement[-3:] in mapping['terminus']):
        return 'terminus'
    elif (mouvement[-6:] in mapping['retournements']) or (
            mouvement[-5:] in mapping['retournements']) or (
            mouvement[:6] in mapping['retournements']) or (
            mouvement[:5] in mapping['retournements']):
        return 'retournement'
    else:
        return 'standard'


def get_EB_data(path, source, context, format='xls', sheet=2, 
                       build=None, dropna=True, en_mouvement=True,
                       drop_cols=cols_EB_drop):
    """
    import EB data from path into a pandas.DataFrame adding source,
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
    context: string
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

    Raises
    ------
    XLRDError
        For error in case the 'sheet' input does not match with an actual
        sheet in the excel file from path.

    Returns
    -------
    pandas.DataFrame
        the EB data as a pandas.DataFrame with additional columns describing
        the source and context of the EB data

    """
    
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
    
    if en_mouvement:
        # suppression des EB à vitesse nulle
        data = data[data['Speed'] != 0]
    # Define new columns for source, and context
    data['Source'] = source
    data['Contexte'] = context
    if build:
    # use concatenation of 'build', 'source' and 'context' to uniquely
    # identify the data
        data['Version'] = build + '_' + source + '_' + context
    else:
    # use the 'Control_software' of data concatenated with 'source'
    # and 'context' to uniquely identify the data
        data['Version'] = 'v' + data['Control_software'].str.replace(
            " ","").str.replace("_1_", "b").str[1:] + (
                '_' + source + '_' + context)
    if en_mouvement:
        print(f"{data.shape[0]} EB en mouvement importés")
    else:
        print(f"{data.shape[0]} EB importés, dont certains peuvent être ",
              end='')
        print("à l'arrêt")
    return data.reset_index()
