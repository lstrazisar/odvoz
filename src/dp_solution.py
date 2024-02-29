import sys
import math
import random
from People import Driver, Client
from Tour import Path, Route
from Problem import Problem
from Schedule import Schedule

SHUFFLE_ITERATIONS = 5
SWAP_ITERATIONS = 200



if __name__ == "__main__":
    problem = Problem(sys.argv[1], sys.argv[2])

    """
    client_orders = [[],
                    [4],
                    [],
                    [],
                    [],
                    [7],
                    [5, 9, 1],
                    [],
                    [],
                    [3, 0, 2, 8, 6]]
    
    empty_matrix = problem.optimize_client_orders(client_orders)
    schedule, barrel_cost = problem.client_orders2schedule(client_orders, empty_matrix)
    schedule.print()
    score = schedule.evaluate(barrel_cost)
    print(score)

    for line in empty_matrix:
        print(line)
    for line in empty_matrix:
        print(line)
    quit()
    """

    
    best_permutation_ever = [i for i in range(len(problem.clients))]
    random.shuffle(best_permutation_ever)

    best_client_orders_ever = problem.get_client_orders(best_permutation_ever)
    best_empty_matrix_ever = problem.optimize_client_orders(best_client_orders_ever)
    best_schedule_ever, best_barrels_cost_ever = problem.client_orders2schedule(best_client_orders_ever, best_empty_matrix_ever)
    best_value_ever = best_schedule_ever.evaluate(best_barrels_cost_ever)

    for shuffle_it in range(SHUFFLE_ITERATIONS):
        best_permutation = [i for i in range(len(problem.clients))]
        random.shuffle(best_permutation)

        best_client_orders = problem.get_client_orders(best_permutation)
        best_empty_matrix = problem.optimize_client_orders(best_client_orders)
        best_schedule, best_barrels_cost = problem.client_orders2schedule(best_client_orders, best_empty_matrix)
        best_value = best_schedule.evaluate(best_barrels_cost)

        for swap_it in range(SWAP_ITERATIONS):
            new_permutation = best_permutation.copy()
            a = random.randint(0, len(problem.clients) - 1)
            b = random.randint(0, len(problem.clients) - 1)
            new_permutation[a] = best_permutation[b]
            new_permutation[b] = best_permutation[a]

            new_client_orders = problem.get_client_orders(new_permutation)
            new_empty_matrix = problem.optimize_client_orders(new_client_orders)
            new_schedule, new_barrel_cost = problem.client_orders2schedule(new_client_orders, new_empty_matrix)
            new_value = new_schedule.evaluate(new_barrel_cost)

            if new_value < best_value:
                best_schedule = new_schedule 
                best_value = new_value
                best_barrels_cost = new_barrel_cost
                best_permutation = new_permutation
                best_empty_matrix = new_empty_matrix
                best_client_orders = new_client_orders

            if new_value < best_value_ever:
                best_schedule_ever = new_schedule 
                best_value_ever = new_value
                best_barrels_cost_ever = new_barrel_cost
                best_permutation_ever = new_permutation
                best_empty_matrix_ever = new_empty_matrix
                best_client_orders_ever = new_client_orders

    best_schedule_ever.print()
    score = best_schedule_ever.evaluate(best_barrels_cost_ever)
    
    
    for di in range(len(problem.drivers)):
        print(best_client_orders_ever[di])
    
    print(score)

    