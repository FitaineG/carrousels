__version__ = '0.9.1'
__author__ = "Tiphaine GRAILLAT for ALSTOM"


import seaborn as sns

# on utilise le style graphique de Seaborn avec un arrière plan de légendes
# blanc fonction set_theme() pour versions à partir de 0.11
if ((int(sns.__version__.split('.')[0]) > 0) or
    (int(sns.__version__.split('.')[1])) > 10):
    sns.set_theme({'legend.facecolor': 'white'})
# fonction set() jusque version 0.10    
else:
    sns.set({'legend.facecolor': 'white'})

titleFontSize = 16
xaxisFontSize = 14
yaxisFontSize = 14
print('Style graphique par défaut de carrouselsAnalysis activé')
    
def set_carrouselsAnalysis_graphic_style(titleSize=16, xaxisSize=14,
                                         yaxisSize=14):
    global titleFontSize
    titleFontSize = titleSize
    global xaxisFontSize
    xaxisFontSize = xaxisSize
    global yaxisFontSize
    yaxisFontSize = yaxisSize
    return print('Style graphique de carrouselsAnalysis modifié')
