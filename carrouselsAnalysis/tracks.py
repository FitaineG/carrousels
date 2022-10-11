# -*- coding: utf-8 -*-
"""

Ceci est un module python qui contient la définition des tracks de reference.

"""

# ************
# Default track configuration for LilleL1
# ************

# définir la liste des voies principales du carrousel
listeVoies = ['V1', 'V2']
# lister les mouvements nominaux, par voie déclarée ci-dessus
serviceCommercial = {'V1': ['4C1-CS1', 'CS1-TRI1', 'TRI1-HDV1', 'HDV1-PDB1',
                            'PDB1-LEZ1', 'LEZ1-HEL1', 'HEL1-MAR1', 'MAR1-FIV1',
                            'FIV1-CAU1', 'CAU1-GLF1', 'GLF1-RIH1', 'RIH1-REP1',
                            'REP1-GAM1', 'GAM1-WAZ1', 'WAZ1-PDP1', 'PDP1-LAM1',
                            'LAM1-CAL1'],
                     'V2': ['CAL2-LAM2', 'LAM2-PDP2', 'PDP2-WAZ2', 'WAZ2-GAM2',
                            'GAM2-REP2', 'REP2-RIH2', 'RIH2-GLF2', 'GLF2-CAU2',
                            'CAU2-FIV2', 'FIV2-MAR2', 'MAR2-HEL2', 'HEL2-LEZ2',
                            'LEZ2-PDB2', 'PDB2-HDV2', 'HDV2-TRI2', 'TRI2-CS2',
                            'CS2-4C2']}
# lister les movements de retournements
retournements = ['4C2-4CEV2', '4CEV2-4C1', 'CAL1-CALOV1', 'CALOV1-CAL2',
                 'HDV1-HDVOV1', 'HDVOV1-HDV2', 'FIV2-FIVEV2', 'FIVEV2-FIV1',
                 'REP2-REPEV2', 'REPEV2-REP1']
# lister les movements avec intersecteur
intersecteurs = ['HDV1-PDB1', 'MAR1-FIV1', 'RIH1-REP1', 'REP1-GAM1',
                 'GAM2-REP2', 'REP2-RIH2', 'FIV2-MAR2', 'PDB2-HDV2']
# lister les terminus
terminus = ['CAL1', '4C2']

# définition track LilleL1
LilleL1 = {'tracklist': listeVoies,
           'pexMovements': serviceCommercial,
           'turnbacks': retournements,
           'intersectors': intersecteurs,
           'terminus': terminus}
