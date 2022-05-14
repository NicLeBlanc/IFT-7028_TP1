from numpy import random
import simpy

# Déclaration des variables / constantes
average_inter_arrival_time_boat = 12  # Temps inter arrivé des bateaux (en heures)
dict_average_decharging_time_boat = {2:9.5, 3:8, 6:4.5, 8:3.5, 13:1.5}

# Fonction de temps d'inter arrivée des bateaux
def inter_arrival_time_boat(average):
    expo = random.exponential(scale=1, size=1)
    result = expo * average_inter_arrival_time_boat
    return result

# Fonction de temps d'inter arrivée
def decharging_time_boat(number_robots):
    time_with_n_robots = dict_average_decharging_time_boat.get(number_robots)
    expo = random.exponential(scale=1, size=1)
    result = expo * time_with_n_robots
    return result

