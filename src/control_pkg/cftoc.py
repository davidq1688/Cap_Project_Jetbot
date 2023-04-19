import numpy as np
import pyomo.environ as pyo

def solve_cftoc(x0, xf, ul_prev, ur_prev):

  Ts = 0.1    # 10 samples per second
  N = 5       # length of horizon
  r_R = 0.03  # radius of right wheel [m]
  r_L = 0.03  # radius of left wheel [m]
  L   = 0.1   # shaft length [m]
  w_max = 10  # maximum anular speed [rad/s]

  model = pyo.ConcreteModel()
  model.tidx = pyo.Set(initialize=range(0, N+1)) # length of finite optimization problem
  model.xidx = pyo.Set(initialize=range(0, 3))
  model.uidx = pyo.Set(initialize=range(0, 2))

  # create state and input variables trajectory:
  model.x = pyo.Var(model.xidx, model.tidx)
  model.u = pyo.Var(model.uidx, model.tidx)

  # cost Function:
  model.cost = pyo.Objective(expr = sum((model.x[0, t]-xf[0])**2 + (model.x[1, t]-xf[1])**2 + 0.00003*(model.x[2, t]-xf[2])**2
                                        # + 0.01*((model.u[0, 0] - ur_prev)**2 + (model.u[1, 0] - ul_prev)**2)
                                        + 0.00001*(model.u[0, t]**2 + model.u[1, t]**2)
                                        for t in model.tidx if t <= N - 1), sense=pyo.minimize)

  # initial conditions
  model.constarint1 = pyo.Constraint(model.xidx, rule=lambda model, i: model.x[i, 0] == x0[i])

  # modeling of the problem (eurler discretization of states)
  model.constarint2 = pyo.Constraint(model.tidx, rule=lambda model, t: model.x[0, t+1] == model.x[0, t] + Ts*(r_R/2*pyo.cos(model.x[2, t])*model.u[0, t] + r_L/2*pyo.cos(model.x[2, t])*model.u[1, t])
                                    if t <= N - 1 else pyo.Constraint.Skip)

  model.constarint3 = pyo.Constraint(model.tidx, rule=lambda model, t: model.x[1, t+1] == model.x[1, t] + Ts*(r_R/2*pyo.sin(model.x[2, t])*model.u[0, t] + r_L/2*pyo.sin(model.x[2, t])*model.u[1, t])
                                    if t <= N - 1 else pyo.Constraint.Skip)

  model.constarint4 = pyo.Constraint(model.tidx, rule=lambda model, t: model.x[2, t+1] == model.x[2, t] + Ts*(r_R/L*model.u[0, t] - r_L/L*model.u[1, t])
                                    if t <= N - 1 else pyo.Constraint.Skip)

  # input constraints (abs(angular speed) less and equal to 5 rad/s)
  model.constarint5 = pyo.Constraint(model.tidx, rule=lambda model, t: model.u[0, t] <= w_max
                                    if t <= N - 1 else pyo.Constraint.Skip)

  model.constarint6 = pyo.Constraint(model.tidx, rule=lambda model, t: model.u[0, t] >= -w_max
                                    if t <= N - 1 else pyo.Constraint.Skip)

  model.constarint7 = pyo.Constraint(model.tidx, rule=lambda model, t: model.u[1, t] <= w_max 
                                    if t <= N - 1 else pyo.Constraint.Skip)

  model.constarint8 = pyo.Constraint(model.tidx, rule=lambda model, t: model.u[1, t] >= -w_max 
                                    if t <= N - 1 else pyo.Constraint.Skip)

  # call non-linear solver:
  results = pyo.SolverFactory('ipopt').solve(model)

  uOpt = np.asarray([model.u[:, t]() for t in model.tidx]).T

  omega_R_opt = uOpt[0, 0]
  omega_L_opt = uOpt[1, 0]

  return [omega_L_opt, omega_R_opt]
