import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt

# Déclaration des variables
moyenne_inter_arrivee_bateaux = 12  # Temps inter arrivé des bateaux (en heures)
dict_temps_dechargement = {2: 9.5, 3: 8, 6: 4.5, 8: 3.5, 13: 1.5}


# Fonction de temps d'inter arrivée des bateaux
def inter_arrival_time_boat():
    result = np.random.exponential(scale=moyenne_inter_arrivee_bateaux)
    result_sec = result * 3600
    return result_sec


# Fonction de temps de déchargement des bateaux
def decharging_time_boat(number_robots):
    time_with_n_robots = dict_temps_dechargement.get(number_robots)
    result = np.random.exponential(scale=time_with_n_robots)
    result_sec = result * 3600
    return result_sec

# Déclaration des variables / états
evenement = 0

#at event zero time is also zero
time_ = 0

#create counters for arrived and served customers
arrived_customers = 0
served_customers = 0
departed_customers = 0