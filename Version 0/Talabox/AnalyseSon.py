# -*- coding: UTF-8 -*-

import librosa
import matplotlib.pyplot as plt
import numpy as np
import time
import AnalyseSonV4
import sys
import subprocess


##Paramètres:

pasDeTemps = 0.1
debut = time.time()
maxPic = 80
deplaFix = 15
deplaRand = 10

args = sys.argv
nom_musique = args[1]

##Import du fichier audio

#TODO convertir la musique en un fichier wav qui convient
def importerETconvertir():
    audio_data = '/home/pi/Documents/Musiques/' + nom_musique + '.wav'
    samples , sampling_rate = librosa.load(audio_data, sr = None)
    return samples,sampling_rate

##Passage du beat au fichier de commande


def getBeats(samp, samp_rate):
    onset_env = librosa.onset.onset_strength(samp, sr=samp_rate)
    beatListe = librosa.beat.beat_track(onset_envelope=onset_env, sr=samp_rate, units = 'time')
    return beatListe[1]

#TODO prendre en compte le tempo pour la vitesse horizontale
def creaCommande(tabBeats):
    newTab = [[0],[0],[0]]
    temps = 0
    previous = 0
    for i in tabBeats:
        timing = round(i,1)
        if newTab[1][-1]<30 :
            sens = 1
        elif newTab[1][-1]>70 :
            sens = -1
        else :
            sens = np.random.randint(0,2)*2-1
        depla = deplaFix+np.random.randint(0,deplaRand)
        while temps < timing-pasDeTemps:
            coef = pasDeTemps/(timing-previous)
            newTab[1].append(newTab[1][-1]+ depla*sens*coef)
            newTab[0].append(newTab[0][-1]+ pasDeTemps)
            temps = round(temps + pasDeTemps,1)
        previous = timing
    return newTab


def commandeTOcsv(tabFinal):
    fic = open('/home/pi/Documents/Commandes/' + nom_musique + '.csv', "w+")
    nbMoves = len(tabFinal[0])
    for i in range(nbMoves):
        fic.write(str("%.2f"%tabFinal[0][i])+";"+("%.2f"%tabFinal[1][i])+";"+str("%.2f"%tabFinal[2][i])+";"+("%.2f"%(100-tabFinal[1][i]))+";"+str("%.2f"%tabFinal[2][i]))
        if (i < nbMoves-1):
            fic.write("\n")
    fic.close()
    subprocess.run(["sudo",'chmod','755','/home/pi/Documents/Musiques/' + nom_musique + '.wav'])


## Déroulé des opérations avec timer

print(time.time()-debut)
samples , sampling_rate = importerETconvertir()
print(time.time()-debut)
beats = getBeats(samples,sampling_rate)
print(time.time()-debut)
commande = creaCommande(beats)
commande[2] = AnalyseSonV4.getYPos(samples,sampling_rate)
print(time.time()-debut)
commandeTOcsv(commande)
print(time.time()-debut)

"""
X = [k*len(samples)/sampling_rate/len(commande[0]) for k in range(len(commande[2]))]
plt.plot(commande[0],commande[1])
plt.title('Position selon X')
plt.show()
"""








