import simpy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def simuler_port(nb_robots):
    # Déclaration des variables / constantes
    capacite_dechargement = 1
    temps_simulation = 40000 * 60 * 60
    moyenne_inter_arrivee_bateaux = 12  # Temps inter arrivé des bateaux (en heures)
    dict_temps_dechargement = {2: 9.5, 3: 8, 6: 4.5, 8: 3.5, 13: 1.5}

    # Déclaration des listes utilisées pour stocker
    arrivees, departs = [], []
    temps_dans_file, temps_dans_systeme = [], []
    temps_de_file, longueur_de_file = [], []
    entre_file, sortie_file = [], []

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
            print('%3d arrive au port à %.2f' % (id_prochain_bateau, env.now))

            env.process(dechargement_bateau(env, no_dechargement, nb_robots,
                                            id_prochain_bateau, temps_arrive))

    # Fonction de simulation du déchargement des bateaux
    def dechargement_bateau(env, no_dechargement, nb_robots, numero_bateau, temps_arrive):
        with file_attente.request() as req:
            print('%3d entre dans la file à at %.2f' %
                  (numero_bateau, env.now))

            temps_entre_file = env.now
            longueur = len(file_attente.queue)
            temps_de_file.append(temps_entre_file)
            longueur_de_file.append(longueur)
            entre_file.append(temps_entre_file)

            yield req
            print('%3d accède au chargement/déchargement à %.2f' %
                  (numero_bateau, env.now))
            temps_sortie_file = env.now
            longueur = len(file_attente.queue)
            temps_de_file.append(temps_sortie_file)
            longueur_de_file.append(longueur)
            sortie_file.append(temps_sortie_file)

            # Distribution exponentielle du temps de déchargement
            temps_dechargement = decharging_time_boat(nb_robots)

            yield env.timeout(temps_dechargement)
            temps_depart = env.now
            print('%3d part du port à %.2f' % (numero_bateau, temps_depart))
            departs.append(temps_depart)
            temps_systeme = temps_depart - temps_arrive
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


    def avg_line(df_length):
        # Nombre de bateaux moyen dans la file d'attente
        df_length['delta_time'] = df_length['temps'].shift(-1) - df_length['temps']
        df_length = df_length[0:-1]
        avg = np.average(df_length['longueur_file'],weights=df_length['delta_time'])
        return avg


    def server_utilization(df_length):
        # Utilisation de la file
        sum_server_free = df_length[df_length['longueur_file']==0] ['delta_time'].sum()
        first_event = df_length['temps'].iloc[0]
        sum_server_free = sum_server_free + first_event
        utilization = round((1 - sum_server_free / temps_simulation) * 100, 2)
        return utilization


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

    df5 = pd.DataFrame(entre_file, columns=['entre_file'])
    df6 = pd.DataFrame(sortie_file, columns=['sortie_file'])
    df_resultats3 = pd.concat([df5, df6], axis=1)

    # df_resultats3['temps_sans_bateau'] = np.where((df_resultats3['entre_file'] == df_resultats3['sortie_file']),df_resultats3['entre_file'] - df_resultats3['sortie_file'].shift(1))

    df_resultats3.to_csv('test.csv')

    df_3 = pd.DataFrame(arrivees, columns=['arrivées'])
    df_4 = pd.DataFrame(departs, columns=['départs'])

    avg_length = avg_line(df_resultats1)
    utilization = server_utilization(df_resultats1)
    avg_delay_inqueue = np.mean(temps_dans_file)
    avg_delay_insyst = np.mean(temps_dans_systeme)

    print('  ')
    print('Le temps d\'attente moyen dans la file est de %.2f' % (avg_delay_inqueue))
    print('The average delay in system is %.2f' % (avg_delay_insyst))
    print('Le nombre moyen de bateaux dans la file est de %.2f' %  (avg_length))
    print('L\'utilisation de la file est de %.2f' % (utilization))

    plt.figure(1)
    plt.plot(df_resultats2['departs_heure'], df_resultats2['ratio_dechargement'])
    plt.title('Nombre de bateaux déchargés par heure')
    plt.axvline(x = 20000, color = 'r', label = 'axvline - full height')

    plt.figure(2)
    plt.plot(df_resultats1['temps_heure'], df_resultats1['moyenne_cumulative_longueur_file'])
    plt.title('Moyenne cumulative de la longueur de la file')
    plt.axvline(x = 20000, color = 'r', label = 'axvline - full height')

    plt.figure(3)
    plt.plot(df_resultats2['departs_heure'], df_resultats2['moyenne_cumulative_temps_file'])
    plt.title('Moyenne cumulative du temps d\'attente dans la file')
    plt.axvline(x = 20000, color = 'r', label = 'axvline - full height')

    # plt.figure(4)
    # plt.plot(df_resultats1['temps_heure'], df_resultats1['moyenne_cumulative_occupation_quai'])
    # plt.title('Moyenne cumulative du taux d\'occupation du quai')
    # plt.axvline(x = 20000, color = 'r', label = 'axvline - full height')

    plt.show()