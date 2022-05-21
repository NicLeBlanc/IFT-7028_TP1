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


# Fonction de simulation du port
def simuler_port(n, mean_arrival_rate, mean_service_rate):
    params = build_params(n, mean_arrival_rate, mean_service_rate)
    result = run_simulation(params)
    # dump_stats(result)
    # plot_result(result)


# Fonction pour déclarer les paramètres
def build_params(num_jobs, mean_arrival_rate, mean_service_rate):
    return {
        "n": num_jobs,
        "mean_arrival_rate": mean_arrival_rate,
        "mean_service_rate": mean_service_rate,
        "mean_interarrival_time": 1.0 / mean_arrival_rate,
        "mean_service_time": 1.0 / mean_service_rate,
        "num_bins": int(num_jobs / mean_arrival_rate)
    }


def run_simulation(params, number_robots):
    n = params["n"]

    # Simulation data and results
    temps_inter_arrive = inter_arrival_time_boat(size=n)
    temps_arrive = np.cumsum(temps_inter_arrive)
    temps_dechargement = decharging_time_boat(size=n, number_robots=number_robots)

    jobs_df = build_jobs_df(params, temps_inter_arrive, temps_arrive, temps_dechargement)
    events_df = build_events_df(params, jobs_df)

    total_width = get_total_width(jobs_df)

    sim_mean_interarrival_time = jobs_df["interarrival_time"].mean()
    sim_mean_arrival_rate = 1.0 / sim_mean_interarrival_time
    sim_mean_service_time = jobs_df["service_time"].mean()
    sim_mean_service_rate = 1.0 / sim_mean_service_time
    sim_mean_wait_time = jobs_df["wait_time"].mean()
    sim_response_time_mean = jobs_df["response_time"].mean()
    sim_response_time_var = jobs_df["response_time"].var()

    # mean_num_jobs_in_system and mean_num_jobs_in_queue
    width = events_df["width"]
    total_weighted_num_jobs_in_system = (width * events_df["num_jobs_in_system"]).sum()
    total_weighted_num_jobs_in_queue = (width * events_df["num_jobs_in_queue"]).sum()
    sim_mean_num_jobs_in_system = total_weighted_num_jobs_in_system / total_width
    sim_mean_num_jobs_in_queue = total_weighted_num_jobs_in_queue / total_width

    # throughput mean and variance
    departures = events_df.loc[events_df["num_jobs_in_system_change"] == -1.0, "lo_bd"]
    hist, _ = np.histogram(departures, bins=int(total_width) + 1)
    sim_throughput_mean = np.mean(hist)

    # utilization
    util = estimate_util(jobs_df)

    return {
        "params": params,
        "jobs_df": jobs_df,
        "events_df": events_df,
        "total_duration": total_width,
        "mean_arrival_rate": sim_mean_arrival_rate,
        "mean_interarrival_time": sim_mean_interarrival_time,
        "mean_service_rate": sim_mean_service_rate,
        "mean_service_time": sim_mean_service_time,
        "mean_wait_time": sim_mean_wait_time,
        "response_time_mean": sim_response_time_mean,
        "response_time_var": sim_response_time_var,
        "mean_num_jobs_in_system": sim_mean_num_jobs_in_system,
        "mean_num_jobs_in_queue": sim_mean_num_jobs_in_queue,
        "throughput_mean": sim_throughput_mean,
        "utilization": util,
    }


def build_jobs_df(params, interarrival_times, arrival_times, service_times):
    n = params["n"]

    jobs_df = pd.DataFrame({
        "interarrival_time": interarrival_times,
        "arrive_time": arrival_times,
        "service_time": service_times,
        "start_time": np.zeros(n),
        "depart_time": np.zeros(n)
    })

    jobs_df.loc[0, "start_time"] = jobs_df.loc[0, "arrive_time"]
    jobs_df.loc[0, "depart_time"] = jobs_df.loc[0, "start_time"] + jobs_df.loc[0, "service_time"]

    for i in range(1, n):
        jobs_df.loc[i, "start_time"] = max(jobs_df.loc[i, "arrive_time"], jobs_df.loc[i - 1, "depart_time"])
        jobs_df.loc[i, "depart_time"] = jobs_df.loc[i, "start_time"] + jobs_df.loc[i, "service_time"]

    jobs_df["response_time"] = jobs_df["depart_time"] - jobs_df["arrive_time"]
    jobs_df["wait_time"] = jobs_df["start_time"] - jobs_df["arrive_time"]

    return jobs_df


# Serialize the jobs into events (arrival, start, departure) so we can compute job counts.
def build_events_df(params, jobs_df):
    n = params["n"]
    arrivals = jobs_df["arrive_time"]
    starts = jobs_df["start_time"]
    departures = jobs_df["depart_time"]

    # width = up_bd - lo_bd, num_jobs_in_queue = num_jobs_in_system - 1
    events_df = pd.DataFrame(columns=["lo_bd", "up_bd", "width", "num_jobs_in_system", "num_jobs_in_queue"])

    lo_bd = 0.0
    arrive_idx = 0
    start_idx = 0
    depart_idx = 0
    num_jobs_in_system = 0
    num_jobs_in_queue = 0

    while depart_idx < n:
        arrival = arrivals[arrive_idx] if arrive_idx < n else float("inf")
        start = starts[start_idx] if start_idx < n else float("inf")
        departure = departures[depart_idx]

        if arrival <= start and arrival <= departure:
            up_bd = arrival
            n_change, nq_change = 1, 1
            arrive_idx = arrive_idx + 1
        elif start <= arrival and start <= departure:
            up_bd = start
            n_change, nq_change = 0, -1
            start_idx = start_idx + 1
        else:
            up_bd = departure
            n_change, nq_change = -1, 0
            depart_idx = depart_idx + 1

        width = up_bd - lo_bd
        events_df = events_df.append({
            "lo_bd": lo_bd,
            "up_bd": up_bd,
            "width": width,
            "num_jobs_in_system": num_jobs_in_system,
            "num_jobs_in_queue": num_jobs_in_queue,
            "num_jobs_in_system_change": n_change,
            "num_jobs_in_queue_change": nq_change,
        }, ignore_index=True)

        num_jobs_in_system = num_jobs_in_system + n_change
        num_jobs_in_queue = num_jobs_in_queue + nq_change

        lo_bd = up_bd

    return events_df


def get_total_width(jobs_df):
    return jobs_df.iloc[-1]["depart_time"] - jobs_df.iloc[0]["arrive_time"]


def estimate_util(jobs_df):
    busy = (jobs_df["depart_time"] - jobs_df["start_time"]).sum()
    return busy / get_total_width(jobs_df)