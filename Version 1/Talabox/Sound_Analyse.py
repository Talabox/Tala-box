# -*- coding: UTF-8 -*-

import librosa
from librosa import display
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import subprocess


##Paramètres:

stepTime = 0.1
start_time = time.time()
maxPeak = 80
fix_move = 15
rand_move = 10

args = sys.argv
music_name = args[1]

secondesAV = 2.5
packer_coef = 0.3
pourcentageLim = 7

##Import du fichier audio

#TODO convertir la musique en un fichier wav qui convient
def import_and_convert():
    audio_data = '/home/pi/Documents/Musiques/' + music_name + '.wav'
    samples , sampling_rate = librosa.load(audio_data, sr = None)
    return samples,sampling_rate

##Passage du beat au fichier de commande


def getBeats(samp, samp_rate):
    onset_env = librosa.onset.onset_strength(samp, sr=samp_rate)
    beatListe = librosa.beat.beat_track(onset_envelope=onset_env, sr=samp_rate, units = 'time')
    return beatListe[1]

#TODO prendre en compte le tempo pour la vitesse horizontale
def command_creation(beat_list):
    new_list = [[0],[0],[0]]
    current_time = 0
    previous = 0
    for i in beat_list:
        timing = round(i,1)
        if new_list[1][-1]<30 :
            sens = 1
        elif new_list[1][-1]>70 :
            sens = -1
        else :
            sens = np.random.randint(0,2)*2-1
        movement = fix_move+np.random.randint(0,rand_move)
        while current_time < timing-stepTime:
            coef = stepTime/(timing-previous)
            new_list[1].append(new_list[1][-1]+ movement*sens*coef)
            new_list[0].append(new_list[0][-1]+ stepTime)
            current_time = round(current_time + stepTime,1)
        previous = timing
    return new_list


def command_to_csv(final_list):
    fic = open('/home/pi/Documents/Commandes/' + music_name + '.csv', "w+")
    nbMoves = len(final_list[0])
    for i in range(nbMoves):
        fic.write(str("%.2f"%final_list[0][i])+";"+("%.2f"%final_list[1][i])+";"+str("%.2f"%final_list[2][i])+";"+("%.2f"%(100-final_list[1][i]))+";"+str("%.2f"%final_list[2][i]))
        if (i < nbMoves-1):
            fic.write("\n")
    fic.close()
    subprocess.run(["sudo",'chmod','755','/home/pi/Documents/Musiques/' + music_name + '.wav'])


## Déroulé des opérations avec timer

print(time.time()-start_time)
samples , sampling_rate = import_and_convert()
print(time.time()-start_time)
beats = getBeats(samples,sampling_rate)
print(time.time()-start_time)
commande = command_creation(beats)
commande[2] = AnalyseSonV4.getYPos(samples,sampling_rate)
print(time.time()-start_time)
command_to_csv(commande)
print(time.time()-start_time)

"""
X = [k*len(samples)/sampling_rate/len(commande[0]) for k in range(len(commande[2]))]
plt.plot(commande[0],commande[1])
plt.title('Position selon X')
plt.show()
"""



def getBeatsV4(samp, samp_rate):
    onset_env = librosa.onset.onset_strength(samp, sr=samp_rate)
    beatL = librosa.beat.plp(onset_envelope=onset_env, sr=samp_rate)
    return list(onset_env)

def get_average(beatL,duration):
    zoneMid = secondesAV*len(beatL)/duration
    zoneTampon = [0 for k in range(int(zoneMid))]
    beatL = zoneTampon+beatL+zoneTampon
    newTab = []
    for i in range(int(duration*10)):
        numTabMin = int((i*zoneMid/10)/secondesAV - zoneMid)+len(zoneTampon)
        numTabMax = int((i*zoneMid/10)/secondesAV + zoneMid)+len(zoneTampon)
        valToAdd = np.mean(beatL[numTabMin:numTabMax])
        newTab.append(valToAdd)
    return newTab

#TODO plus de sensibilité verticale
def packer(beatL):
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
    duration = len(samples)/samplingR
    beatListe = getBeatsV4(samples, samplingR)
    beatLisse = get_average(beatListe,duration)
    beatTasse = packer(beatLisse)
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







