###############################################################################################################################
# Avec l'aide de l'exemple de Dario Weitz : https://towardsdatascience.com/introduction-to-simulation-with-simpy-322606d4ba0c #
###############################################################################################################################

import simpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

nombre_robots = [2, 3, 6, 8, 13]

def simuler_port(nb_robots, periode_rechauffement):
    # Déclaration des variables / constantes
    capacite_dechargement = 1
    temps_simulation = 40000 * 60 * 60 + (periode_rechauffement * 60 * 60)
    temps_simulation_heure = temps_simulation / (60 * 60)
    moyenne_inter_arrivee_bateaux = 12  # Temps inter arrivé des bateaux (en heures)
    dict_temps_dechargement = {2: 9.5, 3: 8, 6: 4.5, 8: 3.5, 13: 1.5}

    # Déclaration des listes utilisées pour stocker
    arrivees, departs = [], []
    temps_dans_file, temps_dans_systeme = [], []
    temps_de_file, longueur_de_file = [], []
    temps_depart_liste, temps_quai_liste = [], []

    # Fonction de temps d'inter arrivée des bateaux
    def inter_arrival_time_boat():
        result = np.random.exponential(moyenne_inter_arrivee_bateaux)
        result_sec = result * 3600
        return result_sec

    # Fonction de temps de déchargement des bateaux
    def decharging_time_boat(number_robots):
        time_with_n_robots = dict_temps_dechargement.get(number_robots)
        result = np.random.exponential(time_with_n_robots)
        result_sec = result * 3600
        return result_sec

    # Fonction de simulation de l'arrivée des bateaux
    def arrive_bateau(env, no_dechargement, nb_robots):
        # ID des bateaux
        id_prochain_bateau = 0
        while True:
            # Distribution exponentielle des arrivées
            temps_prochain_bateau = inter_arrival_time_boat()
            # On attend le bateau
            yield env.timeout(temps_prochain_bateau)
            temps_arrive = env.now
            arrivees.append(temps_arrive)
            id_prochain_bateau += 1
            print('%3d arrive au port à %.2f' % (id_prochain_bateau, env.now / (60*60)))

            env.process(dechargement_bateau(env, no_dechargement, nb_robots,
                                            id_prochain_bateau, temps_arrive))

    # Fonction de simulation du déchargement des bateaux
    def dechargement_bateau(env, no_dechargement, nb_robots, numero_bateau, temps_arrive):
        with file_attente.request() as req:
            print('%3d entre dans la file à at %.2f' %
                  (numero_bateau, env.now / (60*60)))

            temps_entre_file = env.now
            longueur = len(file_attente.queue)
            temps_de_file.append(temps_entre_file)
            longueur_de_file.append(longueur)

            yield req
            print('%3d accède au chargement/déchargement à %.2f' %
                  (numero_bateau, env.now / (60*60)))
            temps_sortie_file = env.now
            longueur = len(file_attente.queue)
            temps_de_file.append(temps_sortie_file)
            longueur_de_file.append(longueur)

            # Distribution exponentielle du temps de déchargement
            temps_dechargement = decharging_time_boat(nb_robots)

            yield env.timeout(temps_dechargement)
            temps_depart = env.now
            print('%3d part du port à %.2f' % (numero_bateau, temps_depart / (60*60)))
            departs.append(temps_depart)
            temps_systeme = temps_depart - temps_arrive
            temps_quai = temps_depart - temps_sortie_file
            # Calcul KPI #4
            temps_depart_liste.append(temps_depart)
            temps_quai_liste.append(temps_quai)

            temps_dans_systeme.append(temps_systeme)
            temps_file = temps_sortie_file - temps_entre_file
            temps_dans_file.append(temps_file)

    # Environnement
    env = simpy.Environment()
    # Définir les ressources
    file_attente = simpy.Resource(env, capacity=capacite_dechargement)

    # Définir le procédé
    env.process(arrive_bateau(env, file_attente, nb_robots=nb_robots))
    # Rouler la simulation
    env.run(until=temps_simulation)

    df1 = pd.DataFrame(temps_de_file, columns=['temps'])
    df2 = pd.DataFrame(longueur_de_file, columns=['longueur_file'])
    df_resultats1 = pd.concat([df1, df2], axis=1)

    df_resultats1['temps_heure'] = df_resultats1['temps'] / (60 * 60)
    df_resultats1['moyenne_cumulative_longueur_file'] = df_resultats1['longueur_file'].expanding().mean()
    df_resultats1['delta_time'] = df_resultats1['temps_heure'].shift(-1) - df_resultats1['temps_heure']

    df3 = pd.DataFrame(temps_dans_file, columns=['temps_dans_file'])
    df4 = pd.DataFrame(departs, columns=['departs'])
    df_resultats2 = pd.concat([df4, df3], axis=1)

    df_resultats2['departs_heure'] = df_resultats2['departs'] / (60 * 60)
    df_resultats2['temps_dans_file_heure'] = df_resultats2['temps_dans_file'] / (60*60)
    df_resultats2['moyenne_cumulative_temps_file'] = df_resultats2['temps_dans_file_heure'].expanding().mean()

    df_resultats2['nombre_bateaux_partis'] = df_resultats2.index + 1
    df_resultats2['ratio_dechargement'] = df_resultats2['nombre_bateaux_partis'] / df_resultats2['departs_heure']

    df5 = pd.DataFrame(temps_depart_liste, columns=['temps_depart'])
    df6 = pd.DataFrame(temps_quai_liste, columns=['temps_quai'])
    df_resultats3 = pd.concat([df5, df6], axis=1)
    df_resultats3['temps_depart_heure'] = df_resultats3['temps_depart'] / (60 * 60)
    df_resultats3['taux_occupation'] = df_resultats3['temps_quai'].cumsum() / df_resultats3['temps_depart']

    kpi1_convergence = df_resultats2['ratio_dechargement'].iloc[-1]
    kpi2_convergence = df_resultats1['moyenne_cumulative_longueur_file'].iloc[-1]
    kpi3_convergence = df_resultats2['moyenne_cumulative_temps_file'].iloc[-1]
    kpi4_convergence = df_resultats3['taux_occupation'].iloc[-1]

    print('------')
    print('Le nombre de bateaux déchargés par heure sur l\'horizon de simulation est de {:.2f}'.format(kpi1_convergence))
    print('Le nombre bateaux dans la file sur l\'horizon de simulation est de {:.2f}'.format(kpi2_convergence))
    print('Le temps d\'attente dans la file sur l\'horizon de simulation est de {:.2f} heures'.format(kpi3_convergence))
    print('Le taux d\'occupation du quai sur l\'horizon de simulation est de {:.2f} %'.format(kpi4_convergence * 100))
    print('------')

    plt.figure(1)
    plt.plot(df_resultats2['departs_heure'], df_resultats2['ratio_dechargement'])
    plt.title('Nombre de bateaux déchargés par heure')
    plt.axvline(x=periode_rechauffement, color='r', label='axvline - full height')
    plt.xlim(0, temps_simulation_heure)
    plt.xlabel("Temps (h)")
    plt.ylabel("Nombre de bateaux déchargés par heure (bateaux)")

    plt.figure(2)
    plt.plot(df_resultats1['temps_heure'], df_resultats1['moyenne_cumulative_longueur_file'])
    plt.title('Moyenne cumulative de la longueur de la file')
    plt.axvline(x=periode_rechauffement, color='r', label='axvline - full height')
    plt.xlim(0, temps_simulation_heure)
    plt.xlabel("Temps (h)")
    plt.ylabel("Longueur de la file (bateaux)")

    plt.figure(3)
    plt.plot(df_resultats2['departs_heure'], df_resultats2['moyenne_cumulative_temps_file'])
    plt.title('Moyenne cumulative du temps d\'attente dans la file')
    plt.axvline(x=periode_rechauffement, color='r', label='axvline - full height')
    plt.xlim(0, temps_simulation_heure)
    plt.xlabel("Temps (h)")
    plt.ylabel("Temps d'attente dans la file (h)")

    plt.figure(4)
    plt.plot(df_resultats3['temps_depart_heure'], df_resultats3['taux_occupation'])
    plt.title('Taux d\'occupation du quai')
    plt.axvline(x=periode_rechauffement, color='r', label='axvline - full height')
    plt.xlim(0, temps_simulation_heure)
    plt.xlabel("Temps (h)")
    plt.ylabel("Taux d'occupation (%)")

    plt.show()

    return kpi1_convergence, kpi2_convergence, kpi3_convergence, kpi4_convergence

def replications_simu(nb_replications, nb_robots, periode_rechauffement):
    df_resultats = pd.DataFrame(columns=['replication', 'kpi1', 'kpi2', 'kpi3', 'kpi4'])
    for k in range(nb_replications):
        replication = k+1
        print('Réplication #{}/{} pour le scénario avec {} robots'.format(replication, nb_replications, nb_robots))
        print(' ')
        kpi = simuler_port(nb_robots, periode_rechauffement)
        list_kpi = list(kpi)
        df_resultats.loc[k] = ['replication' + str(replication)] + list_kpi
        df_resultats.to_csv(r'./resultats_2/resultats_scenario_{}_robots.csv'.format(nb_robots), index=False)
