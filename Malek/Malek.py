import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

np.random.seed(2022)
inter_arrival = 12*60
service_t = 9.5 * 60# POUR 2 ROBOTS POUR LE MOMENT
event = 0
horizon = 40000 * 60

departure_time = 0

#at event zero time is also zero
time_ = 0

bateaux_arrive=0
bateaux_decharg=0
depart_bateaux =0


interarrival_time = np.random.exponential(inter_arrival)
next_arrival_time = time_ + interarrival_time

server_status = "idle" #le serveur est vide au début
queue = 0
bateaux_arrive += 1

### premier evenement
event += 1
ts_columns = ['event', 'time', 'type',
              'queue', 'arr bateaux', 'decharged bateaux', 'depart bateaux']

time_series =  pd.DataFrame([[1, float(next_arrival_time), "arrival",
                              queue, bateaux_arrive, 0, 0]],
                             columns = ts_columns)



while time_ <= horizon:

    event_type = time_series['type'].iloc[event - 1]
    time_ = time_series['time'].iloc[event - 1]

# Si le prochain evénement est un arrivé d'un' bateaux
    if event_type == "arrival":
        bateaux_arrive += 1
        interarrival_time = np.random.exponential(inter_arrival)
        next_arrival_time = time_ + interarrival_time

        # si le serveur est libre le bateaux est déchargé directement
        if server_status == "libre":
            bateaux_decharg += 1
            time_series['decharged bateaux'].iloc[event - 1] = bateaux_decharg

            service_time = np.random.exponential(service_t)
            departure_time = time_ + service_time
            depart_bateaux += 1
            #UPDATE DATAFRAME
            generated_events = pd.DataFrame([
                [99, float(departure_time), "departure", 0, 0, 0, depart_bateaux],
                [99, float(next_arrival_time), "arrival", 0, bateaux_arrive, 0, 0]
            ], columns=ts_columns)

            #Organiser les événements par time
            time_series = pd.concat([time_series, generated_events])
            time_series = time_series.sort_values(['time'])
            time_series.reset_index(drop=True, inplace=True)
            time_series['event'] = list(range(1, time_series.shape[0] + 1))

            event += 1

            # si le serveur est occupé on augmente le queue et on génére des arrivés
        if server_status == "occupé":
            queue += 1
            generated_events = pd.DataFrame([
                [99, float(next_arrival_time), "arrival",
                 0, bateaux_arrive, 0, 0]]
                , columns=ts_columns)

            time_series = pd.concat([time_series, generated_events])
            time_series = time_series.sort_values(['time'])
            time_series.reset_index(drop=True, inplace=True)
            time_series['event'] = list(range(1, time_series.shape[0] + 1))
            time_series['queue'].iloc[event - 1] = queue
            event += 1

# IF EVENT IS A DEPARTURE ####################################
    if event_type == "departure":

        # SI le queue est vide et le bateaux quitte, le statut de serveur devient libre
        if queue == 0:
            server_status = "libre"
            event += 1

        # si le queue n'est pas vide (>0), serveur est occupé et on augmente le queue
        if queue != 0:
            bateaux_decharg += 1
            time_series['decharged bateaux'].iloc[event - 1] = bateaux_decharg

            queue -= 1
            server_status = "occupé"

            service_time = np.random.exponential(service_time)
            departure_time = time_ + service_time
            depart_bateaux += 1

            generated_events = pd.DataFrame([
                [99, float(departure_time), "departure", 0, 0, 0, depart_bateaux]
            ], columns=ts_columns)

            time_series = pd.concat([time_series, generated_events])
            time_series = time_series.sort_values(['time'])
            time_series.reset_index(drop=True, inplace=True)
            time_series['event'] = list(range(1, time_series.shape[0] + 1))
            time_series['queue'].iloc[event - 1] = queue

            event += 1


    if next_arrival_time < departure_time :
        server_status = "occupé"
    else:
        server_status = "libre"

#Collecte de données pour les indicateurs

#arrivé des bateaux
arrivals = time_series.loc[time_series['type'] == 'arrival', ['time', 'arr bateaux' ]]
arrivals.columns = ['time', 'bateaux']
#depart des bateaux
depature = time_series.loc[time_series['type'] == 'departure', ['time', 'depart bateaux' ]]
depature.columns = ['time', 'bateaux']
#bateaux déchargé
serving = time_series.loc[time_series['decharged bateaux'] != 0 , ['time', 'decharged bateaux' ]]
serving.columns = ['time', 'bateaux']

#merge
bateaux_df = arrivals.merge(depature, on='bateaux')
bateaux_df = bateaux_df.merge(serving, on='bateaux')
bateaux_df.columns = ['arrival time', 'bateaux', 'departure time', 'decharging time']
bateaux_df = bateaux_df[['bateaux', 'arrival time', 'decharging time', 'departure time']]

#time in queue
bateaux_df['time in queue'] = bateaux_df['decharging time'] - bateaux_df['arrival time']
#time in system
bateaux_df['time in system'] = bateaux_df['departure time'] - bateaux_df['arrival time']
#time in server
bateaux_df['time in decharging'] = bateaux_df['departure time'] - bateaux_df['decharging time']
#round all floats to 2 digits
bateaux_df = bateaux_df.round(2)

bateaux_df['nombre_bateaux_partis'] = bateaux_df.index + 1
bateaux_df['ratio_dechargement'] = bateaux_df['nombre_bateaux_partis'] / bateaux_df['departure time']

print(time_series)
print(bateaux_df)

#plots
#KPI 1
# plt.figure(1)
# plt.plot(bateaux_df['departure time'], bateaux_df['ratio_dechargement'])
# plt.title('Nombre de bateaux déchargés par heure')


plt.figure(2)
plt.plot(time_series['time'],time_series['queue'].expanding().mean())
plt.title('Moyenne cummulative des bateaux dans la queue')
plt.axvline(x=20000, color='r', label='axvline - full height')

#KPI 3
plt.figure(3)
plt.plot(bateaux_df['departure time'],bateaux_df['time in queue'].expanding().mean())
plt.title('Moyenne cummulative de temps d attente des bateaux dans la queue')
plt.axvline(x=20000, color='r', label='axvline - full height')

plt.show()