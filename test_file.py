# This file tests the implementation of the classes
from lib.classes.stream import Stream
from lib.classes.utility import Utility
from lib.classes.minimum_utility_problem import Min_Utility_Problem
from lib.solvers.min_utility_solver import solve_min_utility_instace
from lib.solvers.transshipment_solver import solve_transshipment_model
from lib.classes.network import Network
from pyomo.environ import ConcreteModel, Var, NonNegativeReals, RangeSet, Objective, Constraint, SolverFactory, Binary


if __name__ == '__main__':

    problems = ["balanced5", "balanced8", "balanced10", "balanced12", "balanced15"]
    problems += ["unbalanced5", "unbalanced10", "unbalanced15", "unbalanced17", "unbalanced20"]

    problem = "balanced5"
    
    minup = Min_Utility_Problem.generate_from_data(problem)
    (sigma_HU, delta_HU) = solve_min_utility_instace(minup)
    network = Network(minup, sigma_HU, delta_HU)
    
    # declaring model
    model = ConcreteModel(name = "MIN_MATCHES_TRANSPORT")

    # declaring model inputs
    H = network.H               # hot streams including utilities
    C = network.C               # cold streams including utilities
    T = network.T               # temperature intervals
    sigma = network.sigmas      # heat supply per hot stream per interval
    delta = network.deltas      # heat demand per cold stream per interval
    U = network.U               # Big-M parameter

    # declaring model variables
    model.y = Var(H, C, within = Binary)
    model.q = Var(H, T, C, T, within = NonNegativeReals)

    # declaring model objective
    def matches_min_rule(model):
        return sum(model.y[h, c] for h in H for c in C)
    model.obj = Objective(rule = matches_min_rule)

    # heat balance for supplies
    def supply_balance_constraint(model, h, s):
        return sum(model.q[h, s, c, t] for c in C for t in T) == sigma[h, s]
    model.supply_balance_constraint = Constraint(H, T, rule = supply_balance_constraint)

    # heat balance for demands
    def demand_balance_constraint(model, c, t):
        return sum(model.q[h, s, c, t] for h in H for s in T) == delta[c, t]
    model.demand_balance_constraint = Constraint(C, T, rule = demand_balance_constraint)

    # big-M constraint
    def big_M_rule(model, h, c):
        return sum(model.q[h, s, c, t] for s in T for t in T) <= U[h, c] * model.y[h, c]
    model.big_M_constraint = Constraint(H, C, rule = big_M_rule)

    # zero heat transmition constraint
    def zero_heat_rule(model, h, c, s, t):
        s_index = T.index(s)
        t_index = T.index(t)
        if s_index > t_index:
            return model.q[h, s, c, t] == 0
        else:
            return Constraint.Skip
    model.zero_heat_constraint = Constraint(H, C, T, T, rule = zero_heat_rule)

    # solving model
    solver = SolverFactory("glpk")
    results = solver.solve(model)
    y = [model.y[h, c].value for h in H for c in C]
    print("HS: {}, CS: {}, TI: {}".format(len(H), len(C), len(T)))
    print("Objective: y = {}".format(sum(y)))
    print(results)
    model.y.pprint()
