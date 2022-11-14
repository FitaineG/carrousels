# -*- coding: utf-8 -*-
"""

Ceci est un module python qui contient les données d'interface des deux
formants possible MG et Fabisis

"""

# ************
# Définition des interfaces pour le format MG
# ************

MG_format = {
    'EB_cols_drop': ['id', 'Abscisse_Temps', 'EB_CAUSE',
                     'Distance_from_train_front_end_to_stop_wished',
                     'Distance_from_train_front_end_to_stop_proposed',
                     'Message_counter_OMAP', 'LOG_OMAP', 'EB_COUNT',
                     'End_track_id', 'End_abscissa'],
    'EB_cols_name': {'NumTrain': 'Train',
                     'Control_software': 'SoftwareVersion',
                     'Date_Time': 'DateEB',
                     'Start_track_id': 'EBTrackId',
                     'Start_abscissa': 'EB_KP',
                     'EB_INDEX': 'EBCause',
                     'EB_TRAIN_ARRET': 'TrainImmo',
                     'EB_TRAIN_MVT': 'TrainEB'},
    'movement_cols_name': {
                'Id_mvt': 'idMovement',
                'Control_software': 'SoftwareVersion',
                'NumTrain': 'Train',
                'Date_Stop': 'DateStop',
                'End_track_id': 'StopTrackId',
                'End_track': 'StopTrackId',
                'Stop_Station': 'StopStation',
                'Start_Station': 'StartStation',
                'Sens': 'Direction',
                'Sens_Temps_de_parcours': 'RunningTimePerDir',
                'Distance_from_train_front_end_to_stop_wished': 'DistanceSSP',
                'Duree_MVT': 'Duree',
                'Train_correctly_docked': 'TrainCorrectlyDocked',
                'Nb_cycle_NV_piloting_command_sup_40percent': 'NVCommandSup40p',
                'Nb_cycle_NV_piloting_command_sup_50percent': 'NVCommandSup50p',
                'Nb_cycle_50ms_NV_piloting_command_sup_40percent': 'NVCommandSup40p',
                'Nb_cycle_50ms_NV_piloting_command_sup_50percent': 'NVCommandSup50p'
                },
    'movement_cols_drop': [
                'Date_Start', 'Abscisse_T_Start',
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
                'Nb_JOG'],
    'stationRegex': '^(SA_)?(?P<station>.*)(?P<pos>_[01])(.*)?'
    }

# ************
# Définition des interfaces pour le format Fabisis
# ************


Fabisis_format = {
    'EB_cols_drop': ['Omap_counter', 'Omap_file', 'Nb_cycle'],
    'EB_cols_name': {'Date_throw': 'DateEB',
                    'Date_fade': 'FinEB',
                    'Num_train': 'Train',
                    'Id_mvt': 'MovementRef',
                    'Start_Station': 'StartStation',
                    'Stop_Station': 'StopStation',
                    'sens': 'Direction',
                    'Track_id': 'EBTrackId',
                    'Control_software': 'SoftwareVersion',
                    'Abscissa_throw': 'EB_KP',
                    'EB_first_causes': 'EBCause',
                    'EB_other_causes': 'addEBCause'},
    'movement_cols_name': {'Id_mvt': 'idMovement',
                'Control_software': 'SoftwareVersion',
                'Num_train': 'Train',
                'Date_stop': 'DateStop',
                'Passengers_exchange': 'PexMovement',
                'Track_id': 'StopTrackId',
                'Start_station': 'StartStation',
                'Stop_station': 'StopStation',
                'sens': 'Direction',
                'Temps_de_parcours': 'RunningTimePerDir',
                'Distance_to_whished_stop': 'DistanceSSP',
                'Duree_MVT': 'Duree',
                'EB_on_MVT': 'EBCause',
                'Correctly_docked': 'TrainCorrectlyDocked',
                'Nb_cycle_NV_piloting_command_sup_40percent': 'NVCommandSup40p',
                'Nb_cycle_NV_piloting_command_sup_50percent': 'NVCommandSup50p'
                },
    'movement_cols_drop': [
                'Date_start', 'Abscissa', 'Duree_ARRET',
                'Omap_file', 'Omap_counter', 'Last_beacon1', 'Last_beacon2',
                'PSD_lower_boundary', 'PSD_upper_boundary',
                'Total_distance_done', 'Nb_cycle_NVFT_accel_FD_inf_-1.6',
                'Control_acceleration_avg_2_1_KPH',
                'Nb_cycle_coasting_10_1_KPH', 'Nb_cycle_motoring_10_1_KPH'],
    'stationRegex': '^(SA_)?(?P<station>.*)(?P<pos>_[01])(.*)?'
    }

# ************
# Définition du dictionnaire des format de données
# ************


carrouselFormat = {
    'MG': MG_format,
    'Fabisis': Fabisis_format
    }
