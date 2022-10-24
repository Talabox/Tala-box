# -*- coding: UTF-8 -*-

import librosa
import matplotlib.pyplot as plt
import numpy as np
import time
from librosa import display



##Paramètres:

pasDeTemps = 0.1
debut = time.time()
maxPic = 80
secondesAV = 2.5
coefTassage = 0.3
pourcentageLim = 7

##Récupération du beat


def getBeatsV4(samp, samp_rate):
    onset_env = librosa.onset.onset_strength(samp, sr=samp_rate)
    beatL = librosa.beat.plp(onset_envelope=onset_env, sr=samp_rate)
    return list(onset_env)

def moyenneur(beatL,duree):
    zoneMid = secondesAV*len(beatL)/duree
    zoneTampon = [0 for k in range(int(zoneMid))]
    beatL = zoneTampon+beatL+zoneTampon
    newTab = []
    for i in range(int(duree*10)):
        numTabMin = int((i*zoneMid/10)/secondesAV - zoneMid)+len(zoneTampon)
        numTabMax = int((i*zoneMid/10)/secondesAV + zoneMid)+len(zoneTampon)
        valToAdd = np.mean(beatL[numTabMin:numTabMax])
        newTab.append(valToAdd)
    return newTab

#TODO plus de sensibilité verticale
def tasseur(beatL):
    moy = np.mean(beatL)
    newTab = []
    mini = min(beatL)
    maxi = max(beatL)
    for i in range(len(beatL)):
        newTab.append(np.log(100*(beatL[i]-mini)*99/(maxi-mini)+1))
    limite = np.percentile(newTab, pourcentageLim)
    mini = limite
    maxi = max(newTab)
    for i in range(len(newTab)):
        if newTab[i] < limite:
            newTab[i] = limite
        newTab[i]=(newTab[i]-mini)*100/(maxi-mini)
    return newTab

def getYPos(samples,samplingR):
    duree = len(samples)/samplingR
    beatListe = getBeatsV4(samples, samplingR)
    beatLisse = moyenneur(beatListe,duree)
    beatTasse = tasseur(beatLisse)
    return beatTasse

"""
X = [k*len(samples)/samplingR/len(beatLisse) for k in range(len(beatLisse))]
plt.title('Beat intensity')
plt.plot(X,beatTasse)
plt.show()

plt.figure()
librosa.display.waveplot(y = samples, sr = samplingR)
plt.xlabel("Times (seconds)")
plt.ylabel("Amplitude")
plt.show()
"""
