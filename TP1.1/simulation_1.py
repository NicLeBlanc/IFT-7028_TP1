import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

def simuler_port(nb_robots, periode_rechauffement):
    # Déclaration des variables
    temps_simulation = (40000 * 60 * 60) + (periode_rechauffement * 60 * 60)
    temps_simulation_heure = temps_simulation / (60 * 60)
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
    temps = 0

    # Créer des compteurs pour l'arrivée des bateaux
    bateaux_arrives = 0
    bateaux_decharges = 0
    bateaux_partis = 0

    # Premier évènement
    temps_inter_arrivee = inter_arrival_time_boat()
    prochain_temps_arrivee = temps + temps_inter_arrivee
    statut_quai = 'vide'
    file = 0
    bateaux_arrives += 1
    evenement += 1
    print('%3d arrive au port à %.2f' % (bateaux_arrives, prochain_temps_arrivee / (60*60)))

    # Créer le dataframe des résultats et le populer avec le premier évènement
    columns_df = ['evenement', 'temps', 'type_evenement', 'file', 'arrivee_bateau', 'bateau_decharge', 'depart_bateau']
    df_simu = pd.DataFrame([[1, float(prochain_temps_arrivee), 'arrivee', file, bateaux_arrives, 0, 0]], columns=columns_df)

    # Boucle jusqu'à l'horizon de simulation
    while temps < temps_simulation:

        type_evenement = df_simu['type_evenement'].iloc[evenement-1]
        temps = df_simu['temps'].iloc[evenement-1]

        # Si l'évènement est de type "arrivee"
        if type_evenement == 'arrivee':

            # Augmenter le compteur d'arrivée
            bateaux_arrives += 1

            # Générer le prochain temps d'arrivée
            temps_inter_arrivee = inter_arrival_time_boat()
            prochain_temps_arrivee = temps + temps_inter_arrivee

            # Imprimer l'arrivée du bateau
            print('%3d arrive au port à %.2f' % (bateaux_arrives, prochain_temps_arrivee / (60*60) ))

            # Si la file est vide, le bateau accède tout de suite à l'espace de déchargement
            if statut_quai == 'vide':

                # Le bateau est déchargé et le compteur est incrémenté de 1
                bateaux_decharges += 1

                # Imprimer l'arrivée à la station de chargement / déchargement
                print('%3d accède au chargement/déchargement à %.2f' % (bateaux_decharges, temps / (60*60)))

                # Le bateau est ajouté à l'historique des bateaux déchargés
                df_simu['bateau_decharge'].iloc[evenement-1] = bateaux_decharges

                # Générer le prochain évènement (déchargement et moment de départ)
                temps_dechargement = decharging_time_boat(number_robots=nb_robots)
                temps_depart = temps + temps_dechargement
                bateaux_partis += 1

                # Imprimer le départ du bateau
                print('%3d part du port à %.2f' % (bateaux_partis, temps_depart / (60*60)))

                # Ajouter l'évènement à l'historique
                prochain_evenement = pd.DataFrame([[99, float(temps_depart), 'depart', 0, 0, 0, bateaux_partis], [99, float(prochain_temps_arrivee), 'arrivee', 0, bateaux_arrives, 0, 0]], columns=columns_df)
                df_simu = pd.concat([df_simu, prochain_evenement])

                # Classer par ordre de temps
                df_simu = df_simu.sort_values(['temps'])
                df_simu.reset_index(drop=True, inplace=True)

                # Assigner le numéro d'évènement selon l'ordre
                df_simu['evenement'] = list(range(1, df_simu.shape[0] + 1))

                # L'évènement est complété, incrémenté de 1
                evenement += 1

            # Si l'emplacement de déchargement est déjà occupé
            if statut_quai == 'occupe':

                # Le bateau est ajouté à la file et sa taille est incrémentée de 1
                file += 1

                # Imprimer l'arrivée dans la file
                print('%3d entre dans la file à at %.2f' % (bateaux_arrives, prochain_temps_arrivee / (60*60)))

                # Ajouter l'évènement à l'historique
                prochain_evenement = pd.DataFrame([[1, float(prochain_temps_arrivee), 'arrivee', 0, bateaux_arrives, 0, 0]], columns=columns_df)
                df_simu = pd.concat([df_simu, prochain_evenement])

                # Classer par ordre de temps
                df_simu = df_simu.sort_values(['temps'])
                df_simu.reset_index(drop=True, inplace=True)

                # Assigner le numéro d'évènement selon l'ordre
                df_simu['evenement'] = list(range(1, df_simu.shape[0] + 1))

                # Ajouter à la file
                df_simu['file'].iloc[evenement-1] = file
                evenement += 1

        # Si l'évènement est de type "depart"
        if type_evenement == 'depart':

            # Si la file est de 0 et qu'un bateau part,
            if file == 0:

                # Le statut de l'emplacement de déchargement reste 'vide'
                statut_quai = 'vide'

                # L'évènement se complète, le compteur est incrémenté
                evenement += 1

            # Si la file est non vide
            if file > 0:

                # Le nombre de bateaux déchargés augmente de 1
                bateaux_decharges += 1

                # Le bateau est ajouté à la liste des bateaux déchargés
                df_simu['bateau_decharge'].iloc[evenement-1] = bateaux_decharges

                # La file est diminuée de 1
                file -= 1

                # Le statut de l'emplacement reste 'occupe'
                statut_quai = 'occupe'

                print('%3d accède au chargement/déchargement à %.2f' % (bateaux_decharges, temps / (60*60)))

                # Générer le prochain évènement (déchargement et moment de départ)
                temps_dechargement = decharging_time_boat(number_robots=nb_robots)
                temps_depart = temps + temps_dechargement
                bateaux_partis += 1

                # Imprimer le départ du bateau
                print('%3d part du port à %.2f' % (bateaux_partis, temps_depart / (60*60)))

                # Ajouter l'évènement à l'historique
                prochain_evenement = pd.DataFrame([[99, float(temps_depart), 'depart', 0, 0, 0, bateaux_partis]], columns=columns_df)
                df_simu = pd.concat([df_simu, prochain_evenement])

                # Classer par ordre de temps
                df_simu = df_simu.sort_values(['temps'])
                df_simu.reset_index(drop=True, inplace=True)

                # Assigner le numéro d'évènement selon l'ordre
                df_simu['evenement'] = list(range(1, df_simu.shape[0] + 1))

                # Ajouter à la file
                df_simu['file'].iloc[evenement - 1] = file

                # L'évènement est fini, le compteur est incrémenté de 1
                evenement += 1

        # Lorsque complété, déterminer l'état de l'espace de déchargement
        if prochain_temps_arrivee < temps_depart:
            statut_quai = 'occupe'
        else:
            statut_quai = 'vide'

    # Résumé des expérimentations

    # Arrivées des bateaux
    arrivees = df_simu.loc[df_simu['type_evenement'] == 'arrivee', ['temps', 'arrivee_bateau']]
    arrivees.columns = ['temps', 'bateau']

    # Départs des bateaux
    departs = df_simu.loc[df_simu['type_evenement'] == 'depart', ['temps', 'depart_bateau']]
    departs.columns = ['temps', 'bateau']

    # Temps de service des bateaux
    dechargement = df_simu.loc[df_simu['bateau_decharge'] != 0, ['temps', 'bateau_decharge']]
    dechargement.columns = ['temps', 'bateau']

    # Longueur de la file de bateaux
    df_file = df_simu[['temps', 'file']]
    df_file.columns = ['temps', 'longueur_file']

    # Concaténation
    df_bateaux = arrivees.merge(departs, on='bateau')
    df_bateaux = df_bateaux.merge(dechargement, on='bateau')
    # Nommer les colonnes
    df_bateaux.columns = ['temps_arrivee', 'bateau', 'temps_depart', 'temps_dechargement']
    # Réorganiser les colonnes
    df_bateaux = df_bateaux[['bateau', 'temps_arrivee', 'temps_dechargement', 'temps_depart']]

    # Bateaux déchargés par heure
    df_bateaux['departs_heure'] = df_bateaux['temps_depart'] / (60 * 60)
    df_bateaux['nombre_bateaux_partis'] = df_bateaux.index + 1
    df_bateaux['ratio_dechargement'] = df_bateaux['nombre_bateaux_partis'] / df_bateaux['departs_heure']

    # Nombre de bateaux dans la file
    df_file['temps_heure'] = df_file['temps'] / (60 * 60)
    df_file['moyenne_cumulative_longueur_file'] = df_file['longueur_file'].expanding().mean()

    # Temps passé dans la file
    df_bateaux['temps_dans_file'] = df_bateaux['temps_dechargement'] - df_bateaux['temps_arrivee']
    df_bateaux['temps_dans_file_heure'] = df_bateaux['temps_dans_file'] / (60 * 60)
    df_bateaux['moyenne_cumulative_temps_file'] = df_bateaux['temps_dans_file_heure'].expanding().mean()

    # Temps passé dans la zone de déchargement
    df_bateaux['temps_dans_dechargement'] = df_bateaux['temps_depart'] - df_bateaux['temps_dechargement']
    # Taux d'occupation
    df_bateaux['taux_occupation'] = df_bateaux['temps_dans_dechargement'].cumsum() / df_bateaux['temps_depart']

    kpi1_convergence = df_bateaux['ratio_dechargement'].iloc[-1]
    kpi2_convergence = df_file['moyenne_cumulative_longueur_file'].iloc[-1]
    kpi3_convergence = df_bateaux['moyenne_cumulative_temps_file'].iloc[-1]
    kpi4_convergence = df_bateaux['taux_occupation'].iloc[-1]

    print('------')
    print('Le nombre de bateaux déchargés par heure sur l\'horizon de simulation est de {:.2f}'.format(kpi1_convergence))
    print('Le nombre bateaux dans la file sur l\'horizon de simulation est de {:.2f}'.format(kpi2_convergence))
    print('Le temps d\'attente dans la file sur l\'horizon de simulation est de {:.2f} heures'.format(kpi3_convergence))
    print('Le taux d\'occupation du quai sur l\'horizon de simulation est de {:.2f} %'.format(kpi4_convergence))
    print('------')

    plt.figure(1)
    plt.plot(df_bateaux['departs_heure'], df_bateaux['ratio_dechargement'])
    plt.title('Nombre de bateaux déchargés par heure')
    plt.axvline(x=periode_rechauffement, color='r', label='axvline - full height')
    plt.xlim(0, temps_simulation_heure)
    plt.xlabel("Temps (h)")
    plt.ylabel("Nombre de bateaux déchargés par heure (bateaux)")

    plt.figure(2)
    plt.plot(df_file['temps_heure'], df_file['moyenne_cumulative_longueur_file'])
    plt.title('Moyenne cumulative de la longueur de la file')
    plt.axvline(x=periode_rechauffement, color='r', label='axvline - full height')
    plt.xlim(0, temps_simulation_heure)
    plt.xlabel("Temps (h)")
    plt.ylabel("Longueur de la file (bateaux)")

    plt.figure(3)
    plt.plot(df_bateaux['departs_heure'], df_bateaux['moyenne_cumulative_temps_file'])
    plt.title('Moyenne cumulative du temps d\'attente dans la file')
    plt.axvline(x=periode_rechauffement, color='r', label='axvline - full height')
    plt.xlim(0, temps_simulation_heure)
    plt.xlabel("Temps (h)")
    plt.ylabel("Temps d'attente dans la file (h)")

    plt.figure(4)
    plt.plot(df_bateaux['departs_heure'], df_bateaux['taux_occupation'])
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
        df_resultats.to_csv(r'./resultats_1/resultats_scenario_{}_robots.csv'.format(nb_robots), index=False)
