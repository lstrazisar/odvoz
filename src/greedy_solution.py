import sys
import math
import random
from People import Driver, Client
from Tour import Path, Route
from Problem import Problem
from Schedule import Schedule

ITERATIONS = 2000



if __name__ == "__main__":
    problem = Problem(sys.argv[1], sys.argv[2])
    best_permutation = [i for i in range(len(problem.clients))]
    random.shuffle(best_permutation)
    best_schedule, best_barrels_cost, best_visits = problem.solve(best_permutation)
    best_value = best_schedule.evaluate(best_barrels_cost)
    for t in range(ITERATIONS):
        new_permutation = best_permutation.copy()
        a = random.randint(0, len(problem.clients) - 1)
        b = random.randint(0, len(problem.clients) - 1)
        new_permutation[a] = best_permutation[b]
        new_permutation[b] = best_permutation[a]

        new_schedule, new_barrel_cost, new_visits = problem.solve(new_permutation)
        new_value = new_schedule.evaluate(new_barrel_cost)
        if new_value < best_value:
            best_schedule = new_schedule 
            best_value = new_value
            best_barrels_cost = new_barrel_cost
            best_visits = new_visits
            best_permutation = new_permutation

    best_schedule.print()
    score = best_schedule.evaluate(best_barrels_cost)
    
    for di in range(len(problem.drivers)):
        print(best_visits[di])
    print(score)
