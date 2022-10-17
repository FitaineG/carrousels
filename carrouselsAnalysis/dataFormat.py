# -*- coding: utf-8 -*-
"""

Ceci est un module python qui contient les données d'interface des deux
formants possible MG et Fabisis

"""

# ************
# Définition des interfaces pour le format MG
# ************

MG_format = {
    'EB_cols_drop': ['id', 'EB_TRAIN_ARRET', 'Abscisse_Temps', 'EB_CAUSE',
                     'Distance_from_train_front_end_to_stop_wished',
                     'Distance_from_train_front_end_to_stop_proposed',
                     'Message_counter_OMAP', 'LOG_OMAP', 'EB_COUNT',
                     'End_track_id', 'End_abscissa'],
    'EB_cols_name': {'NumTrain': 'Train',
                     'Control_software': 'SoftwareVersion',
                     'Date_Time': 'DateEB',
                     'Start_track_id': 'EB_trackID',
                     'Start_abscissa': 'EB_KP',
                     'EB_INDEX': 'EBCause'},
    'EB_filter': 'EB_TRAIN_MVT',
    'movement_cols_name': {
                'Control_software': 'SoftwareVersion',
                'NumTrain': 'Train',
                'Date_Stop': 'DateStop',
                'End_track_id': 'StopTrackID',
                'Stop_Station': 'StopStation',
                'Start_Station': 'StartStation',
                'Sens': 'Direction',
                'Distance_from_train_front_end_to_stop_wished': 'DistanceSSP',
                'Duree_MVT': 'Duree',
                'Train_correctly_docked': 'TrainCorrectlyDocked',
                'Nb_cycle_NV_piloting_command_sup_40percent': 'NVCommandSup40p',
                'Nb_cycle_NV_piloting_command_sup_50percent': 'NVCommandSup50p'
                },
    'movement_cols_drop': [
                'Id_mvt', 'Date_Start', 'Abscisse_T_Start',
                'Abscisse_T_Stop', 'Start_track_id', 'Start_abscissa',
                'End_abscissa', 'Diff_Start_End_abscissa',
                'Strategy_id__5cycles_avant_vitesse_nulle',
                'Start_Station_id', 'Stop_Station_id',
                'Distance_from_train_front_end_to_stop_proposed',
                'LOG_OMAP', 'Message_counter_OMAP', 'Row_Id_start',
                'Row_Id_stop', 'Row_Id_max_kph', 'Row_Id_start_after_stop',
                'RSD_1_Vital_opening_command',
                'DistanceToSSP', 'DistanceToSSP__1cycle_avant_vitesse_nulle',
                'DistanceToSSP_avg__10cycles_avant_vitesse_nulle',
                'Control_acc_avg_30_15_KPH', 'Duree_ARRET',
                'Antenna_1_Last_Detected_beacon',
                'Antenna_2_Last_Detected_beacon',
                'RSD_1_Door_open_vital_cond_for_PSD_align_lower_boundary',
                'RSD_1_Door_open_vital_cond_for_PSD_align_upper_boundary',
                'Nb_cycle_NVFT_accel_FD_inf_-1.6',
                'Control_acceleration_avg_2_1_KPH',
                'Nb_cycle_coasting_10_1_KPH',
                'Nb_cycle_motoring_10_1_KPH',
                'Nb_JOG']
    }

# ************
# Définition des interfaces pour le format Fabisis
# ************


Fabisis_format = {
    'EB_cols_drop': [],
    'EB_cols_name': {},
    'EB_filter': '',
    'movement_cols_name': {},
    'movement_cols_drop': []
    }

# ************
# Définition du dictionnaire des format de données
# ************


carrouselFormat = {
    'MG': MG_format,
    'Fabisis': Fabisis_format
    }
