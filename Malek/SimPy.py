

import simpy
import numpy as np
import matplotlib.pyplot as plt

# np.random.seed(2022)

t_attente = []
obs_times = []
q_length = []

def generate_interarrival():
  return np.random.exponential(12*3600)
# Activ=charge/décharge

def generate_activ(tmc):
  return np.random.exponential(tmc*3600)

print(generate_interarrival())

def activ_bat(env,robots,tmc):
  i = 0
  while True:
    i += 1
    yield env.timeout(generate_interarrival())
    env.process(bateaux(env,i,robots,tmc))


def bateaux(env, bateaux, robots,tmc):
  with robots.request() as request:
    t_arrive=env.now
    print (env.now, 'bateau {} arrive'.format(bateaux))
    yield request
    print(env.now,'bateau {} se charge/décharge'.format(bateaux))
    t_charg=env.now
    yield env.timeout(generate_activ(tmc))

    print(env.now,'charge/décharge du bateau {} terminé'.format(bateaux))
    t_quitte=env.now
    t_attente.append( t_charg - t_arrive )



def observe(env, robots):
  while True:
    obs_times.append(env.now)
    q_length.append(len(robots.queue))
    yield env.timeout(1)


def get_user_input():
    nb_robots = input("Nombre des robots: ")
    temps_moyen_charg= input("Temps moyen de chargement/dechargement d un bateau: ")
    params = [nb_robots, temps_moyen_charg]
    if all(isinstance(i, float) for i in params):  # Check input is valid
        params = [nb_robots, temps_moyen_charg]
    else:
        print(
            "Could not parse input. The simulation will use default values:",
            "\n 2 robots, 9.5 heures comme temps moyen de chargement/dechargement d un bateau ",
        )
        params = [2,9.5]
    print(nb_robots,temps_moyen_charg)
    return params


def main():
  # Setup
  nb_robots, temps_moyen_charg = get_user_input()

  # Run the simulation
  env = simpy.Environment()

  robots = simpy.Resource(env, capacity=nb_robots)
  env.process(activ_bat(env, robots,temps_moyen_charg))
  env.process(observe(env, robots))
  env.run(until=144000000)


  # View the results
  #
  # print('le temps d attente dans le queue pour chaque bateaux est :', t_attente)
  # print('la longeur de queue a chaque observation :', q_length)


if __name__ == '__main__':
  main()

plt.plot(obs_times, q_length)
plt.xlabel('temps t ')
plt.ylabel('longuer du queue a l instant t')
plt.show()

print(len(obs_times))
print(len(q_length))