from pyomo.environ import *
from pyomo.dae import *
from pyomo.dae.simulator import Simulator

m = ConcreteModel()

m.t = ContinuousSet(bounds=(0.0,10.0))

m.b = Param(initialize=0.25)
m.c = Param(initialize=5.0)

m.omega = Var(m.t)
m.theta = Var(m.t)

m.domegadt = DerivativeVar(m.omega,wrt=m.t)
m.dthetadt = DerivativeVar(m.theta,wrt=m.t)

# Setting the initial conditions
m.omega[0] = 0.0
m.theta[0] = 3.14-0.1

def _diffeq1(m,t):
    return m.domegadt[t] == -m.b*m.omega[t] - m.c*sin(m.theta[t])
m.diffeq1 = Constraint(m.t,rule=_diffeq1)

def _diffeq2(m,t):
    return m.dthetadt[t] == m.omega[t]
m.diffeq2 = Constraint(m.t,rule=_diffeq2)

# Simulate the model
sim = Simulator(m)
tsim, profiles = sim.simulate()
varorder = sim.get_variable_order()

# Discretize model using Orthogonal Collocation
discretizer = TransformationFactory('dae.collocation')
discretizer.apply_to(m,nfe=8,ncp=5)

# Initialize the discretized model using the simulator profiles
sim.initialize_model()

import matplotlib.pyplot as plt

time = list(m.t)
omega = [value(m.omega[t]) for t in m.t]
theta = [value(m.theta[t]) for t in m.t]

for idx,v in enumerate(varorder):
    plt.plot(tsim,profiles[:,idx],label=v)
plt.plot(time,omega,'o',label='omega interp')
plt.plot(time,theta,'o',label='theta interp')
plt.xlabel('t')
plt.legend(loc='best')
plt.show()
