import random
from Schedule import Schedule
from Problem import Problem

MAX_INVERT_LENGTH = 20
DIFFERENT_MUTATIONS = 2
DIFFERENT_CROSSOVERS = 5
ELITISM_NUMBER = 1
MUTATION_RATE = 1.0
CROSSOVER_RATE = 0.9
SWAP_ITERATIONS = 2

def swap(i, j, permutation):
    permutation[i], permutation[j] = permutation[j], permutation[i]

class Chromosome:
    
    def __init__(self, problem, permutation):
        schedule, barrel_cost, client_orders = problem.solve(permutation)
        
        self.problem = problem
        self.permutation = permutation
        self.schedule = schedule
        self.barrel_cost = barrel_cost
        self.client_orders = client_orders
        self.score = schedule.evaluate(barrel_cost)
        self.fitness = 1 / self.score
    
        

class Population:
    
    def __init__(self, problem, population_size):
        self.problem = problem
        self.chromosomes = []
        self.population_size = population_size
        
    def initialize(self):
        """
        permutation = [n for n in range(self.problem.number_of_clients)]
        for i in range(self.population_size):
            random.shuffle(permutation)
            self.chromosomes.append(Chromosome(self.problem, permutation))
        """
        for i in range(self.population_size):
            best_permutation = [n for n in range(self.problem.number_of_clients)]
            random.shuffle(best_permutation)
            best_schedule, best_barrels_cost, best_visits = self.problem.solve(best_permutation)
            best_value = best_schedule.evaluate(best_barrels_cost)
            for _ in range(SWAP_ITERATIONS):
                new_permutation = best_permutation.copy()
                a = random.randint(0, len(self.problem.clients) - 1)
                b = random.randint(0, len(self.problem.clients) - 1)
                new_permutation[a] = best_permutation[b]
                new_permutation[b] = best_permutation[a]

                new_schedule, new_barrel_cost, new_visits = self.problem.solve(new_permutation)
                new_value = new_schedule.evaluate(new_barrel_cost)
                if new_value < best_value:
                    best_schedule = new_schedule 
                    best_value = new_value
                    best_barrels_cost = new_barrel_cost
                    best_visits = new_visits
                    best_permutation = new_permutation
            self.chromosomes.append(Chromosome(self.problem, best_permutation))
    
    def sort(self):
        self.chromosomes.sort(key=lambda x: -x.fitness)
    
    def elitism(self):
        self.sort()
        return self.chromosomes[:ELITISM_NUMBER]
    
    def roulette_wheel_selection(self):
        fitness_sum = 0
        for chromosome in self.chromosomes:
            fitness_sum += chromosome.fitness
        
        r = random.uniform(0, fitness_sum)
        index = 0
        while r > 0:
            r -= self.chromosomes[index].fitness
            index += 1
        index -= 1
        return self.chromosomes[index]
            
    def mutation_swap(self, c):
        p = c.permutation.copy()
        #standard = Chromosome(self.problem, p)
        i = random.randint(0, len(p) - 1)
        j = random.randint(0, len(p) - 1)
        swap(i, j , p)
        mutated = Chromosome(self.problem, p)
        return mutated
        
        if mutated.score < standard.score:
            return mutated
        return standard
        
    
    def mutation_invert(self, c):
        p = c.permutation.copy()
        invert_length = random.randint(2, MAX_INVERT_LENGTH)
        i = random.randint(0, len(p) - invert_length)
        j = i + invert_length
        
        new_p = p[:i] + p[i:j][::-1] + p[j:]  #invert middle part
        return Chromosome(self.problem, new_p)
    
    def crossover_OX(self, c1, c2):
        parent1 = c1.permutation
        parent2 = c2.permutation
        
        size = len(parent1)
         # Select two random cut points
        cut1, cut2 = sorted(random.sample(range(size), 2))
        
        # Initialize offspring as copies of parents
        offspring1 = [-1] * size
        offspring2 = [-1] * size
        
        # Copy the segment between the cut points from parent1 to offspring1
        offspring1[cut1:cut2+1] = parent1[cut1:cut2+1]
        offspring2[cut1:cut2+1] = parent2[cut1:cut2+1]
        
        # Fill the remaining positions in offspring2 with vertices from parent2
        i = (cut2 + 1) % size
        j = (cut2 + 1) % size
        while offspring2[j] == -1:
            if parent2[i] not in offspring1:
                offspring2[j] = parent2[i]
                j = (j + 1) % size
            i = (i + 1) % size
        
        # Fill the remaining positions in offspring1 with vertices from parent2
        i = (cut2 + 1) % size
        j = (cut2 + 1) % size
        while offspring1[j] == -1:
            if parent1[i] not in offspring2:
                offspring1[j] = parent1[i]
                j = (j + 1) % size
            i = (i + 1) % size
        
        print(offspring1)
        return Chromosome(self.problem, offspring1)
        
    def crossover_PMX(self, c1, c2):
        parent1 = c1.permutation
        parent2 = c2.permutation
        
        size = len(parent1)
    
        # Select two random cut points
        cut1, cut2 = sorted(random.sample(range(size), 2))
        
        # Initialize offspring as copies of parents
        offspring1 = [-1] * size
        offspring2 = [-1] * size
        
        # Copy the segment between the cut points from parent1 to offspring1
        offspring1[cut1:cut2+1] = parent1[cut1:cut2+1]
        offspring2[cut1:cut2+1] = parent2[cut1:cut2+1]
        
        # Create a mapping from parent1 to parent2 and vice versa
        mapping1to2 = {}
        mapping2to1 = {}
        
        for i in range(cut1, cut2 + 1):
            mapping1to2[parent1[i]] = parent2[i]
            mapping2to1[parent2[i]] = parent1[i]
        
        # Fill the remaining positions in offspring1 using mapping2to1
        for i in range(size):
            if offspring1[i] == -1:
                vertex = parent2[i]
                while vertex in mapping2to1:
                    vertex = mapping2to1[vertex]
                offspring1[i] = vertex
        
        # Fill the remaining positions in offspring2 using mapping1to2
        for i in range(size):
            if offspring2[i] == -1:
                vertex = parent1[i]
                while vertex in mapping1to2:
                    vertex = mapping1to2[vertex]
                offspring2[i] = vertex
        #print(offspring1)
        return Chromosome(self.problem, offspring1)
    
    def crossover_ERX(self, c1, c2):
        def get_neighbors(chromosome):
            """
            Returns a dictionary containing neighbors of each vertex in the chromosome.
            """
            neighbors = {}
            for i, vertex in enumerate(chromosome):
                neighbors[vertex] = set([chromosome[(i-1)%len(chromosome)], chromosome[(i+1)%len(chromosome)]])
            return neighbors
        
        parent1 = c1.permutation
        parent2 = c2.permutation
        all_vertices = parent1 + parent2
        
        # Initialize offspring with the first vertex from parent1
        offspring = [parent1[0]]
        
        # Get neighbors of each vertex in parent1 and parent2
        neighbors1 = get_neighbors(parent1)
        neighbors2 = get_neighbors(parent2)
        
        # While offspring is not complete
        while len(offspring) < len(parent1):
            last_vertex = offspring[-1]
            # Get neighbors of the last vertex
            last_vertex_neighbors = neighbors1[last_vertex].union(neighbors2[last_vertex])
            
            # Filter out visited vertices
            unvisited_neighbors = [neighbor for neighbor in last_vertex_neighbors if neighbor not in offspring]
            
            if unvisited_neighbors:
                # Find the neighbor with the fewest unvisited neighbors
                min_unvisited_neighbors = float('inf')
                next_vertex = None
                for neighbor in unvisited_neighbors:
                    neighbors_count = len(neighbors1[neighbor].union(neighbors2[neighbor]) - set(offspring))
                    if neighbors_count < min_unvisited_neighbors:
                        min_unvisited_neighbors = neighbors_count
                        next_vertex = neighbor
                offspring.append(next_vertex)
            else:
                # If all neighbors are visited, choose any unvisited vertex randomly
                unvisited_vertices = [vertex for vertex in all_vertices if vertex not in offspring]
                next_vertex = random.choice(unvisited_vertices)
                offspring.append(next_vertex)
        #print(offspring)
        return Chromosome(self.problem, offspring)
    
    def crossover_CX(self, c1, c2):
        parent1 = c1.permutation
        parent2 = c2.permutation
        size = len(parent1)
    
        # Initialize offspring as a list of None values
        offspring = [None] * size
        
        # Initialize a set to keep track of visited indices
        visited_indices = set()
        
        # Begin the cycle
        while len(visited_indices) < size:
            # Find the index of the next unvisited vertex
            next_index = next(i for i in range(size) if i not in visited_indices)
            cycle_start_index = next_index
            cycle_value = parent1[cycle_start_index]
            
            # Perform the cycle
            while next_index not in visited_indices:
                visited_indices.add(next_index)
                # Determine the value to copy from the other parent
                if parent1[next_index] == cycle_value:
                    cycle_value = parent2[next_index]
                # Copy the value into the offspring at the corresponding index
                offspring[next_index] = cycle_value
                # Move to the next index
                next_index = parent1.index(parent2[next_index])
            
            # Complete the cycle by filling in the remaining positions with values from parent2
            for i in range(size):
                if offspring[i] is None:
                    offspring[i] = parent2[i]
        #print(offspring)
        return Chromosome(self.problem, offspring)
        
    def crossover_AEX(self, c1, c2):
        parent1 = c1.permutation
        parent2 = c2.permutation
        size = len(parent1)
    
        # Initialize offspring as a list of None values
        offspring = [None] * size
        
        # Initialize a set to keep track of visited vertices
        visited_vertices = set()
        
        # Choose the first vertex randomly
        first_vertex = random.choice(parent1)
        offspring[0] = first_vertex
        visited_vertices.add(first_vertex)
        
        # Start constructing the child cycle
        for i in range(1, size):
            last_vertex = offspring[i - 1]
            
            # Determine the possible next vertices from parent1 and parent2
            next_vertex_p1 = parent1[(parent1.index(last_vertex) + 1) % size]
            next_vertex_p2 = parent2[(parent2.index(last_vertex) + 1) % size]
            
            # Choose the next vertex from parent1 if it's not visited yet
            if next_vertex_p1 not in visited_vertices:
                offspring[i] = next_vertex_p1
                visited_vertices.add(next_vertex_p1)
            # Otherwise, choose the next vertex from parent2
            elif next_vertex_p2 not in visited_vertices:
                offspring[i] = next_vertex_p2
                visited_vertices.add(next_vertex_p2)
            # If both vertices are visited, choose randomly from the unvisited vertices
            else:
                unvisited_vertices = [vertex for vertex in parent1 if vertex not in visited_vertices]
                offspring[i] = random.choice(unvisited_vertices)
                visited_vertices.add(offspring[i])
        #print(offspring)
        return Chromosome(self.problem, offspring)
        
    def next_generation(self):
        population_size = len(self.chromosomes)
        new_population = Population(self.problem, population_size)
        for _ in range(population_size - ELITISM_NUMBER):
            c1 = self.roulette_wheel_selection()
            c2 = self.roulette_wheel_selection()
            
            new_chromosome = self.roulette_wheel_selection()
            if random.uniform(0, 1) <= CROSSOVER_RATE:
                """which type of crossover"""
                type = random.randint(3, DIFFERENT_CROSSOVERS)
                #type == 5
                #print(type)
                #if type == 1: new_chromosome = self.crossover_OX(c1, c2)
                #elif type == 2: new_chromosome = self.crossover_PMX(c1, c2)
                if type == 3: new_chromosome = self.crossover_CX(c1, c2)
                if type == 4: new_chromosome = self.crossover_ERX(c1, c2)
                if type == 5: new_chromosome = self.crossover_AEX(c1, c2)
            
            """mutation"""
            if random.uniform(0, 1) <= 0.5:
                new_chromosome = self.mutation_swap(new_chromosome)
            else:
                new_chromosome = self.mutation_invert(new_chromosome)
            """
            if random.uniform(0, 1) <= MUTATION_RATE:
                type = random.randint(1, DIFFERENT_MUTATIONS)
                if type == 1: new_chromosome = self.mutation_swap(new_chromosome)
                elif type == 2: new_chromosome = self.mutation_invert(new_chromosome)
            """
            
            new_population.chromosomes.append(new_chromosome)
            #print("1 change")
        
        new_population.chromosomes = new_population.chromosomes + self.elitism()
        return new_population