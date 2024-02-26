import sys
import math
import random
from People import Driver, Client
from Tour import Path, Route
from Schedule import Schedule


DISTANCE_FACTOR = 3
TIME_FACTOR = 1
DRIVER_START = 480
START_OF_WORKTIME = 480
END_OF_WORKTIME = 960
WORKTIME_DURATION = END_OF_WORKTIME - START_OF_WORKTIME
START_OF_DAY = 0
DAY_LENGTH = 1440
INF = 1e10

class Problem:

    def __init__(self, input_file_name, output_file_name):

        with open(input_file_name) as file:
            _ = file.readline()
            problem_number = file.readline()

            number_of_locations, number_of_clients, number_of_drivers, cost_per_kilometer = list(map(int, file.readline().split()))

            time_matrix = []
            for i in range(number_of_locations):
                time_matrix.append(list(map(int, file.readline().split())))

            distance_matrix = []
            for i in range(number_of_locations):
                distance_matrix.append(list(map(int, file.readline().split())))

            dump = list(map(int, file.readline().split()))  #1 if location is dump, 0 else
            location_types = ["normal" for i in range(number_of_locations)]

            clients = []
            client_indexes = []
            client_overtime_costs = [None for i in range(number_of_locations)]
            for i in range(number_of_clients):
                location_index, number_of_barrels, barrel_cost, overtime_cost = list(map(int, file.readline().split()))
                client_indexes.append(location_index - 1)
                clients.append(Client(self, location_index - 1, number_of_barrels, barrel_cost, overtime_cost))
                client_overtime_costs[location_index - 1] = overtime_cost
                location_types[location_index - 1] = "client"

            drivers = []
            driver_indexes = []
            for i in range(number_of_drivers):
                location_index, capacity, overtime_cost = list(map(int, file.readline().split()))
                driver_indexes.append(location_index - 1)
                drivers.append(Driver(self, location_index - 1, capacity, overtime_cost, i, DRIVER_START))
                location_types[location_index - 1] = "driver"

            dump_indexes = []
            for i in range(number_of_locations):
                if dump[i] == 1:
                    dump_indexes.append(i)
                    location_types[i] = "dump"

        self.problem_number = int(problem_number)
        self.output_file_name = output_file_name
        self.number_of_locations = number_of_locations
        self.number_of_clients = number_of_clients
        self.number_of_drivers = number_of_drivers
        self.cost_per_kilometer = cost_per_kilometer
        self.clients = clients
        self.drivers = drivers
        self.client_indexes = client_indexes
        self.driver_indexes = driver_indexes
        self.dump_indexes = dump_indexes
        self.location_types = location_types
        self.time_matrix = time_matrix
        self.distance_matrix = distance_matrix
        self.client_overtime_costs = client_overtime_costs

        self.path_matrix = self.calculate_real_distances()
        self.real_time_matrix = []
        self.real_distance_matrix = []
        for row in self.path_matrix:
            times = []
            distances = []
            for path in row:
                times.append(path.duration)
                distances.append(path.distance)
            self.real_time_matrix.append(times)
            self.real_distance_matrix.append(distances)

        self.closest_dumps = []
        for index in range(number_of_locations):
            closest_dump = self.dump_indexes[0]
            best_score = INF
            for ci in self.dump_indexes:
                score = self.get_real_distance(index, ci)
                if score < best_score:
                    closest_dump = ci
                    best_score = score
            self.closest_dumps.append(closest_dump)

        self.best_dumps_moving_from_a2b = []
        for y in range(number_of_locations):
            line = []
            for x in range(number_of_locations):
                line.append(self.calculate_best_dump_moving_from(y, x))
            self.best_dumps_moving_from_a2b.append(line)

    def type(self, location_index):
        return self.location_types[location_index]
    
    """distance when traveling from i1 to i2"""
    def get_distance(self, i1, i2):
        return self.distance_matrix[i1][i2]

    """time when traveling form i1 to i2"""
    def get_time(self, i1, i2):
        return self.time_matrix[i1][i2]
    
    """distance when traveling from i1 to i2 via shortest path"""
    def get_real_distance(self, i1, i2):
        return self.real_distance_matrix[i1][i2]

    """time when traveling form i1 to i2 via shortest path"""
    def get_real_time(self, i1, i2):
        return self.real_time_matrix[i1][i2]
    
    def get_path(self, i1, i2):
        return self.path_matrix[i1][i2]
    
    def get_best_dump_moving_from(self, i1, i2):
        return self.best_dumps_moving_from_a2b[i1][i2]
    
    def calculate_best_dump_moving_from(self, i1, i2):
        best_index = self.dump_indexes[0]
        best_score = INF
        for index in self.dump_indexes:
            score = self.get_real_distance(i1, index) + self.get_real_distance(index, i2)
            if score < best_score:
                best_score = score
                best_index = index

        return best_index
    
    def dijkstra(self, start):
        #-1 for not yet visited, -2 for done
        dist = [-1 for l in range(self.number_of_locations)]
        p = [-1 for l in range(self.number_of_locations)] #provisional distance (-1 = unvisited, -2 = done)
        prev = [None for l in range(self.number_of_locations)]

        p[start] = 0
        while True:
            x = -1 #smallest provisional
            for i in range(self.number_of_locations):
                if p[i] >= 0 and (x == -1 or p[i] < p[x]):
                    x = i
            
            if x == -1: break

            dist[x] = p[x]; p[x] = -2
            for y in range(self.number_of_locations):
                d = dist[x] + DISTANCE_FACTOR *self.get_distance(x, y) + TIME_FACTOR * self.get_time(x, y) #can be modified to care about time too
                if p[y] == -1 or p[y]>=0 and d < p[y]:
                    p[y] = d
                    prev[y] = x
            
        return dist, prev
    
    """Dijkstra only returns the previous element for each element, but we want whole path"""
    def reconstruct_path_from_prev(self, start, end, prev):
        sequence_reversed = [end]
        current = end
        while current != start:
            sequence_reversed.append(prev[current])
            current = prev[current]

        return sequence_reversed[::-1]
    
    """In the input we are given the distances between locations, but they are not necessarily the shortest.
       Because of that we are going to calculate real shortest paths between locations and their lengths"""
    def calculate_real_distances(self):
        matrix = []
        for location in range(self.number_of_locations):
            dist, prev = self.dijkstra(location)
            row = []
            for destination in range(self.number_of_locations):
                sequence = self.reconstruct_path_from_prev(location, destination, prev)
                row.append(Path(self, sequence))
            matrix.append(row)

        return matrix
    
    def restart(self):
        for driver in self.drivers:
            driver.time_spent = DRIVER_START
            driver.current_location_index = driver.starting_location_index
            driver.current_carry = 0
            driver.clients_visited = []
        for client in self.clients:
            client.barrels_left = client.starting_number_of_barrels

    def solve(self, permutation):
        self.restart()
        schedule = Schedule(self, [])
        #self.clients.sort(key=lambda x : self.get_real_time(x.location_index, x.closest_dump_index) + self.get_real_time(x.closest_dump_index, x.location_index))

        visits = [[] for di in range(len(self.drivers))]

        for index in permutation:
            client = self.clients[index]
            ci = client.location_index #Client Index
            best_score = INF
            best_driver_index = -1
            best_tours = -1

            for driver in self.drivers:
                score = 0
                time = 0
                di = driver.current_location_index #driver index
                carry = driver.current_carry

                if driver.current_carry >= (1*driver.capacity) // 2:
                    score = self.cost_per_kilometer * self.get_real_distance(di, self.best_dumps_moving_from_a2b[di][ci])  #go to dump on path to next client
                    time = self.get_real_time(di, self.best_dumps_moving_from_a2b[di][ci])
                    di = self.best_dumps_moving_from_a2b[di][ci]
                    carry = 0


                score += self.cost_per_kilometer * self.get_real_distance(di, ci) #to get to the client
                time += self.get_real_time(di, ci)

                tours_needed = int(math.ceil((client.starting_number_of_barrels + carry) / driver.capacity))
                dump_index = self.best_dumps_moving_from_a2b[ci][ci]
                score += self.cost_per_kilometer * (tours_needed - 1) * (self.get_real_distance(ci, dump_index) + self.get_real_distance(dump_index, ci)) #always except the last tour we have to go back
                time += (tours_needed - 1) * (self.get_real_time(ci, dump_index) + self.get_real_time(dump_index, ci))
                score += max(0, (time - WORKTIME_DURATION) * client.overtime_cost) #client overtime penalty

                dump = self.best_dumps_moving_from_a2b[ci][driver.starting_location_index]
                score += self.cost_per_kilometer * self.get_real_distance(ci, dump)
                time += self.get_real_time(ci, dump)

                if time + driver.time_spent >= START_OF_WORKTIME + 800:
                    score += self.cost_per_kilometer * self.get_real_distance(ci, dump)
                    score += self.cost_per_kilometer * self.get_real_distance(dump, driver.starting_location_index)  
                    score -= self.cost_per_kilometer * self.get_real_distance(driver.current_location_index, driver.starting_location_index)
                
                time += self.get_real_time(dump, driver.starting_location_index)
                score += max(0, (time + driver.time_spent - WORKTIME_DURATION - START_OF_WORKTIME) * driver.overtime_cost)

                #score_random = score * random.uniform(0.9, 1.1)

                if score < best_score and driver.time_spent + time <= DAY_LENGTH:  
                    best_score = score
                    best_driver_index = driver.driver_index
                    best_tours = tours_needed

            if best_driver_index != -1:
                driver = self.drivers[best_driver_index]
                driver.clients_visited.append(index)
                visits[best_driver_index].append(index)
                """empty (if current carry is big)"""
                if driver.current_carry >= (1*driver.capacity) // 2:
                    dump_index = self.best_dumps_moving_from_a2b[driver.current_location_index][client.location_index]
                    path = self.get_path(driver.current_location_index, dump_index)
                    schedule.add_route(Route(self, path, driver, driver.time_spent,
                                            self.get_real_time(driver.current_location_index, dump_index), 0, -driver.current_carry))
                    driver.time_spent += self.get_real_time(driver.current_location_index, dump_index)
                    driver.current_carry  = 0
                    driver.current_location_index = dump_index
                

                """go to client"""
                added = min(driver.capacity - driver.current_carry, client.barrels_left)
                path = self.get_path(driver.current_location_index, client.location_index)
                schedule.add_route(Route(self, path, driver, driver.time_spent,
                                         self.get_real_time(driver.current_location_index, client.location_index), 0, added))
                driver.time_spent += self.get_real_time(driver.current_location_index, client.location_index)
                client.barrels_left -= added
                driver.current_carry += added
                driver.current_location_index = client.location_index

                """collect barrels and get them to the dump (if there ary any left at that client)"""
                while client.barrels_left > 0:
                    dump_index = self.best_dumps_moving_from_a2b[client.location_index][client.location_index]
                    path = self.get_path(client.location_index, dump_index)
                    schedule.add_route(Route(self, path, driver, driver.time_spent,
                                             self.get_real_time(client.location_index, dump_index), 0, -driver.current_carry))
                    driver.time_spent += self.get_real_time(client.location_index, dump_index)
                    driver.current_carry = 0
                    
                    path = self.get_path(dump_index, client.location_index)
                    change =  min(client.barrels_left, driver.capacity)
                    schedule.add_route(Route(self, path, driver, driver.time_spent,
                                             self.get_real_time(dump_index, client.location_index), 0, change))
                    driver.time_spent += self.get_real_time(dump_index, client.location_index)
                    driver.current_carry = change
                    client.barrels_left -= change
                
        
        """at the end all drivers empty their vehicles and moe home"""
        for driver in self.drivers:
            if driver.current_carry != 0:
                dump = self.best_dumps_moving_from_a2b[driver.current_location_index][driver.starting_location_index]
                path = self.get_path(driver.current_location_index, dump)
                schedule.add_route(Route(self,path, driver, driver.time_spent, self.get_real_time(driver.current_location_index, dump), 0, -driver.current_carry))
                driver.time_spent += self.get_real_time(driver.current_location_index, dump)
                driver.current_location_index = dump

            if driver.current_location_index != driver.starting_location_index:
                path = self.get_path(driver.current_location_index, driver.starting_location_index)
                schedule.add_route(Route(self,path, driver, driver.time_spent, self.get_real_time(driver.current_location_index, driver.starting_location_index), 0, 0))
                driver.time_spent += self.get_real_time(driver.current_location_index, driver.starting_location_index)
        
        barrels_cost = 0
        for client in self.clients:
            barrels_cost += client.barrels_left * client.barrel_cost

        self.restart()
        return schedule, barrels_cost, visits