

import simpy
import numpy as np
# Cas de 2 robots pour un tenps moyen de 9.5 h
np.random.seed(2022)





def generate_interarrival():
  return np.random.exponential(12*60)
# Activ=charge/décharge
def generate_activ():
  return np.random.exponential(9.5*60)

def activ_bat(env,robots):
  i = 0
  while True:
    i += 1
    yield env.timeout(generate_interarrival())
    env.process(bateaux(env,i,robots))


def bateaux(env,bateaux,robots):
  with robots.request() as request:
    t_arrive=env.now
    print (env.now, 'bateau {} arrive'.format(bateaux) )
    yield request
    print(env.now,'bateau {} se charge/décharge'.format(bateaux))
    t_charg=env.now
    yield env.timeout(generate_activ())
    print(env.now,'charge/décharge du bateau {} terminé'.format(bateaux))
    t_quitte=env.now
    t_attente.append( t_charg - t_arrive)

t_attente = []
obs_times = []
q_length = []

def observe(env, robots):
  while True:
    obs_times.append(env.now)
    q_length.append(len(robots.queue))
    yield env.timeout(60)

env = simpy.Environment()

robots=simpy.Resource(env, capacity=1)
env.process(activ_bat(env,robots))
env.process(observe(env,robots))
env.run(until=6500)

t_attente
