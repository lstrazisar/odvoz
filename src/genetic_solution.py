import sys
import math
import random
from People import Driver, Client
from Tour import Path, Route
from Problem import Problem
from Schedule import Schedule
from Genetics import Chromosome, Population

POPULATION_SIZE = 30
INF = 1e10

if __name__ == "__main__":
    problem = Problem(sys.argv[1], sys.argv[2])
    population = Population(problem, POPULATION_SIZE)
    population.initialize()
    
    best_score = INF
    best_optimized_score = INF
    gen = 0
    
    for chromosome in population.chromosomes:
            if chromosome.score < best_score:
                best_score = chromosome.score
                optimized_score, optimized_schedule = problem.get_optimized(chromosome.client_orders)
                if optimized_score < best_optimized_score:
                    best_optimized_score = optimized_score
                    optimized_schedule.print()
    
    while True:
        population = population.next_generation()
        for chromosome in population.chromosomes:
            if chromosome.score < best_score:
                best_score = chromosome.score
                 
            if chromosome.score < best_score + 1500:
                optimized_score, optimized_schedule = problem.get_optimized(chromosome.client_orders)
                if optimized_score < best_optimized_score:
                    best_optimized_score = optimized_score
                    optimized_schedule.print()
        
        if gen % 10 == 0:
            print(f"current generation: {gen}   current_otimized_score: {best_optimized_score}")
        gen += 1
    
    