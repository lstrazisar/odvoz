import sys
import math
import random
from People import Driver, Client
from Tour import Path, Route
from Problem import Problem
from Schedule import Schedule

SHUFFLE_ITERATIONS = 15
SWAP_ITERATIONS = 3000



if __name__ == "__main__":
    problem = Problem(sys.argv[1], sys.argv[2])

    best_permutation_ever = [i for i in range(len(problem.clients))]
    random.shuffle(best_permutation_ever)
    best_schedule_ever, best_barrels_cost_ever, best_visits_ever = problem.solve(best_permutation_ever)
    best_value_ever = best_schedule_ever.evaluate(best_barrels_cost_ever)
    for t1 in range(SHUFFLE_ITERATIONS):

        best_permutation = [i for i in range(len(problem.clients))]
        random.shuffle(best_permutation)
        best_schedule, best_barrels_cost, best_visits = problem.solve(best_permutation)
        best_value = best_schedule.evaluate(best_barrels_cost)
        for t2 in range(SWAP_ITERATIONS):
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
            
            if new_value < best_value_ever:
                best_schedule_ever = new_schedule 
                best_value_ever = new_value
                best_barrels_cost_ever = new_barrel_cost
                best_visits_ever = new_visits
                best_permutation_ever = new_permutation
    
    score = best_schedule_ever.evaluate(best_barrels_cost_ever)

    empty_matrix = problem.optimize_client_orders(best_visits_ever)
    new_schedule, new_barrel_cost = problem.client_orders2schedule(best_visits_ever, empty_matrix)
    new_score = new_schedule.evaluate(new_barrel_cost)
    new_schedule.print()

    for line in best_visits_ever:
        print(line)

    print(score)
    print(new_score)
