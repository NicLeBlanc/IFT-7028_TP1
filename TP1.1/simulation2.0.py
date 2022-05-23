import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.mode.chained_assignment = None

# Déclaration des variables
temps_simulation = (40000 * 60 * 60) #+ (periode_rechauffement * 60 * 60)
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

        # Si la file est vide, le bateau accède tout de suite à l'espace de déchargement
        if statut_quai == 'vide':

            # Le bateau est déchargé et le compteur est incrémenté de 1
            bateaux_decharges += 1

            # Le bateau est ajouté à l'historique des bateaux déchargés
            df_simu['bateau_decharge'].iloc[evenement-1] = bateaux_decharges

            # Générer le prochain évènement (déchargement et moment de départ)
            temps_dechargement = decharging_time_boat(number_robots=2)
            temps_depart = temps + temps_dechargement
            bateaux_partis += 1

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

            # Générer le prochain évènement (déchargement et moment de départ)
            temps_dechargement = decharging_time_boat(number_robots=2)
            temps_depart = temps + temps_dechargement
            bateaux_partis += 1

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

# Concaténation
df_bateaux = arrivees.merge(departs, on='bateau')
df_bateaux = df_bateaux.merge(dechargement, on='bateau')
# Nommer les colonnes
df_bateaux.columns = ['temps_arrivee', 'bateau', 'temps_dechargement', 'temps_depart']
# Réorganiser les colonnes
df_bateaux = df_bateaux[['bateau', 'temps_arrivee', 'temps_dechargement', 'temps_depart']]


# Bateaux déchargés par heure


# Nombre de bateaux dans la file


# Temps passé dans la file
df_bateaux['temps_dans_file'] = df_bateaux['temps_dechargement'] - df_bateaux['temps_arrivee']

# Temps passé dans la zone de déchargement
df_bateaux['temps_dans_dechargement'] = df_bateaux['temps_depart'] - df_bateaux['temps_dechargement']




