
import sys
import math
import functools
import random

DRIVER_START = 0
START_OF_WORKTIME = 480
END_OF_WORKTIME = 960
WORKTIME_DURATION = END_OF_WORKTIME - START_OF_WORKTIME
START_OF_DAY = 0
DAY_LENGTH = 1440
INF = 1e10

class Driver:

    def __init__(self, problem, starting_location_index, capacity, overtime_cost, driver_index):
        self.problem = problem
        self.starting_location_index = starting_location_index
        self.current_location_index = starting_location_index
        self.capacity = capacity
        self.overtime_cost = overtime_cost
        self.driver_index = driver_index
        self.time_spent = DRIVER_START  #let's say that nobody works before the start of worktime
        self.current_carry = 0

class Client:

    def __init__(self, problem, location_index, number_of_barrels, barrel_cost, overtime_cost):
        self.problem = problem
        self.location_index = location_index
        self.starting_number_of_barrels = number_of_barrels
        self.barrel_cost = barrel_cost
        self.overtime_cost = overtime_cost
        self.current_number_of_barrels = number_of_barrels
        self.barrels_left = number_of_barrels
        self.closest_dump_index = None

    def calculate_closest_dump(self):
        self.closest_dump_index = sorted(self.problem.dump_indexes, 
                                         key=lambda i : self.problem.get_real_distance(self.location_index, i))[0]

class Path:

    def __init__(self, problem, node_sequence):
        time = 0
        distance = 0
        current = node_sequence[0]
        for next in node_sequence[1:]:
            time += problem.get_time(current, next)
            distance += problem.get_distance(current, next)
            current = next

        self.start = node_sequence[0]
        self.end = node_sequence[-1]
        self.stops = node_sequence[1:] #nodes on the path to end
        self.duration = time
        self.distance = distance

class Route:

    def __init__(self, problem, path, driver, start_time, duration, barrel_change_at_start, barrel_change_at_end):
        self.problem = problem
        self.path = path
        self.driver = driver
        self.start_time = start_time
        self.duration = duration
        self.end_time = start_time + duration
        self.barrel_change_at_start = barrel_change_at_start
        self.barrel_change_at_end = barrel_change_at_end
    
    """1st category is driver_index, second category is start time"""
    def compare(route1, route2):
        driver1_index = route1.driver.driver_index
        driver2_index = route1.driver.driver_index

        if driver1_index < driver2_index:
            return -1
        elif driver1_index > driver2_index:
            return 1
        if route1.start_time < route2.start_time:
            return -1
        elif route1.start_time > route2.start_time:
            return 1
        return 0

class Schedule:

    def __init__(self, problem, routes):
        self.problem = problem
        self.routes = routes
        self.score = None

    def clear(self):
        for route in self.routes:
            del route
        self.routes = []
        self.score = None

    def add_route(self, route):
        self.routes.append(route)

    def evaluate(self, barrels_cost):
        driver_starts = [DAY_LENGTH + 1 for i in range(len(self.problem.drivers))]
        driver_ends = [-1 for i in range(len(self.problem.drivers))]
        client_starts = [DAY_LENGTH + 1 for i in range(self.problem.number_of_locations)]
        client_ends = [-1 for i in range(self.problem.number_of_locations)]

        kilometers = 0
        for travel in self.represent():
            driver_index = travel[0]
            kilometers += self.problem.get_distance(travel[1], travel[2])

        for route in self.routes:
            driver_index = route.driver.driver_index
            if driver_starts[driver_index] == -1 or driver_starts[driver_index] > route.start_time:
                driver_starts[driver_index] = route.start_time
            if driver_ends[driver_index] == -1 or driver_ends[driver_index] < route.start_time + route.duration:
                driver_ends[driver_index] = route.start_time + route.duration

            if route.barrel_change_at_start != 0 and route.path.start in self.problem.client_indexes:
                client_index = route.path.start
                if client_ends[client_index] < route.start_time:
                    client_ends[client_index] = route.start_time
                if client_starts[client_index] > route.start_time:
                    client_starts[client_index] = route.start_time

            if route.barrel_change_at_end != 0 and route.path.stops[-1] in self.problem.client_indexes:
                client_index = route.path.stops[-1]
                if client_starts[client_index] > route.start_time + route.duration:
                    client_starts[client_index] = route.start_time + route.duration
                if client_ends[client_index] < route.start_time + route.duration:
                    client_ends[client_index] = route.start_time + route.duration
                
        
        drivers_overtime_cost = 0
        for i, (start_time, end_time) in enumerate(zip(driver_starts, driver_ends)):
            drivers_overtime_cost += self.problem.drivers[i].overtime_cost * (max(0, START_OF_WORKTIME - start_time) + max(0, end_time - END_OF_WORKTIME))

        clients_overtime_cost = 0
        for i in self.problem.client_indexes:
            start_time = client_starts[i]
            end_time = client_ends[i]
            clients_overtime_cost += self.problem.client_overtime_costs[i] * (max(0, START_OF_WORKTIME - start_time) + max(0, end_time - END_OF_WORKTIME))

        #print(kilometers, drivers_overtime_cost, clients_overtime_cost)
        #print(kilometers * self.problem.cost_per_kilometer + drivers_overtime_cost + clients_overtime_cost)
        return kilometers * self.problem.cost_per_kilometer + drivers_overtime_cost + clients_overtime_cost + barrels_cost

    
    def get_score(self):
        return None
    
    def sort_routes(self):
        #self.routes.sort(key=functools.cmp_to_key(Route.compare))
        self.routes.sort(key=lambda x : x.driver.driver_index)

    def print_move(self, driver_index, start_location, destination, start_time, barrel_change_at_start, barrel_change_at_end):
        print(driver_index,
              start_location,
              destination,
              start_time,
              barrel_change_at_start,
              barrel_change_at_end)

    def print(self):
        with open(self.problem.output_file_name, "w") as f:
            travels = self.represent()

            f.write("372629\n")
            f.write("Odvoz\n\n")
            f.write(str(self.problem.problem_number) + "\n")
            f.write(str(len(travels)) + "\n")
            for travel in travels:
                line = " ".join([str(travel[0] + 1),
                    str(travel[1] + 1),
                    str(travel[2] + 1),
                    str(travel[3]),
                    str(travel[4]),
                    str(travel[5])])
                f.write(line + "\n")
    
    def represent_move(self, driver_index, start_location, destination, start_time, barrel_change_at_start, barrel_change_at_end):
        return (driver_index,
              start_location,
              destination,
              start_time,
              barrel_change_at_start,
              barrel_change_at_end)

    def represent(self):
        self.sort_routes()

        travels = []
        for route in self.routes:
            if len(route.path.stops) == 1:
                travels.append(self.represent_move(route.driver.driver_index,
                                route.path.start,
                                route.path.stops[0],
                                route.start_time,
                                route.barrel_change_at_start,
                                route.barrel_change_at_end))

            else:
                """first travel in route (shortest path from location1 to location2)"""
                travels.append(self.represent_move(route.driver.driver_index,
                                route.path.start,
                                route.path.stops[0],
                                route.start_time,
                                route.barrel_change_at_start,
                                0))

                """auxilliary travels"""
                current_location = route.path.stops[0]
                current_time = route.start_time + self.problem.get_time(route.path.start, route.path.stops[0])
                for destination in route.path.stops[1:-1]:
                    travels.append(self.represent_move(route.driver.driver_index,
                                    current_location,
                                    destination,
                                    current_time,
                                    0,
                                    0))
                    current_time += self.problem.get_time(current_location, destination)
                    current_location = destination

                """last travel"""
                travels.append(self.represent_move(route.driver.driver_index,
                                current_location,
                                route.path.end,
                                current_time,
                                0,
                                route.barrel_change_at_end))
        return travels

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
                drivers.append(Driver(self, location_index - 1, capacity, overtime_cost, i))
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

        for client in self.clients:
            client.calculate_closest_dump()

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
                d = dist[x] + 4*self.get_distance(x, y) + 0* self.get_time(x, y) #can be modified to care about time too
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
        for client in self.clients:
            client.barrels_left = client.starting_number_of_barrels
    
    def solve(self):
        self.restart()
        schedule = Schedule(problem, [])
        #self.clients.sort(key=lambda x : self.get_real_time(x.location_index, x.closest_dump_index) + self.get_real_time(x.closest_dump_index, x.location_index))

        random.shuffle(self.clients)
        for client in self.clients:
            ci = client.location_index #Client Index
            best_score = INF
            best_driver_index = -1
            best_time_spent = -1
            best_tours = -1

            for driver in self.drivers:
                score = self.cost_per_kilometer * self.get_real_distance(driver.current_location_index, ci) #to get to the client
                time = self.get_real_time(driver.current_location_index, ci)

                tours_needed = int(math.ceil((client.starting_number_of_barrels + driver.current_carry) / driver.capacity))
                score += self.cost_per_kilometer * (tours_needed - 1) * (self.get_real_distance(ci, client.closest_dump_index) + self.get_real_distance(client.closest_dump_index, ci)) #always except the last tour we have to go back
                time += (tours_needed - 1) * (self.get_real_time(ci, client.closest_dump_index) + self.get_real_time(client.closest_dump_index, ci))
                score += max(0, (time - WORKTIME_DURATION) * client.overtime_cost) #client overtime penalty

                score += self.cost_per_kilometer * self.get_real_distance(ci, client.closest_dump_index)
                time += self.get_real_time(ci, client.closest_dump_index)

                score += self.cost_per_kilometer * self.get_real_distance(client.closest_dump_index, driver.starting_location_index)  # to get back home (ussualy driver will have just 1 client)
                time += self.get_real_time(client.closest_dump_index, driver.starting_location_index)
                score += max(0, (time - (WORKTIME_DURATION - driver.time_spent) - WORKTIME_DURATION) * driver.overtime_cost)


                if score < best_score and driver.time_spent + time <= DAY_LENGTH:  
                    best_score = score
                    best_driver_index = driver.driver_index
                    best_time_spent = time - self.get_real_time(client.closest_dump_index, driver.starting_location_index)
                    best_tours = tours_needed

            if best_driver_index != -1:
                driver = self.drivers[best_driver_index]
                """output and time update"""
                # indexes start at 1, in our case they start at 0, so we have to add 1
                added = min(client.barrels_left, driver.capacity - driver.current_carry)
                path = self.get_path(driver.current_location_index, client.location_index)
                schedule.add_route(Route(self, path, driver, driver.time_spent,
                                         self.get_real_time(driver.current_location_index, client.location_index), 0, added))
                driver.time_spent += self.get_real_time(driver.current_location_index, client.location_index)
                client.barrels_left -= added
                driver.current_carry += added
                driver.current_location_index = client.location_index

                for tour in range(best_tours - 1):
                    path = self.get_path(client.location_index, client.closest_dump_index)
                    schedule.add_route(Route(self, path, driver, driver.time_spent,
                                             self.get_real_time(client.location_index, client.closest_dump_index), 0, -driver.current_carry))
                    driver.time_spent += self.get_real_time(client.location_index, client.closest_dump_index)
                    driver.current_carry = 0
                    
                    path = self.get_path(client.closest_dump_index, client.location_index)
                    schedule.add_route(Route(self, path, driver, driver.time_spent,
                                             self.get_real_time(client.closest_dump_index, client.location_index), 0, min(client.barrels_left, driver.capacity)))
                    driver.time_spent += self.get_real_time(client.closest_dump_index, client.location_index)
                    driver.current_carry = min(driver.capacity, client.barrels_left)
                    client.barrels_left -= min(driver.capacity, client.barrels_left)

                """last travel of the tour"""
                if driver.current_carry >= driver.capacity * (1/3):
                    path = self.get_path(client.location_index, client.closest_dump_index)
                    schedule.add_route(Route(self, path, driver, driver.time_spent,
                                            self.get_real_time(client.location_index, client.closest_dump_index), 0, -driver.current_carry))
                    driver.time_spent += self.get_real_time(client.location_index, client.closest_dump_index)
                    driver.current_location_index = client.closest_dump_index
                    driver.current_carry = 0
                
        
        """at the end all drivers empty their vehicles and moe home"""
        for driver in self.drivers:
            if driver.current_carry != 0:
                dump = None
                for client in self.clients:
                    if driver.current_location_index == client.location_index:
                        dump = client.closest_dump_index 
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
        return schedule, barrels_cost
    
    def solve2(self):
        self.restart()
        schedule = Schedule(problem, [])
        #self.clients.sort(key=lambda x : self.get_real_time(x.location_index, x.closest_dump_index) + self.get_real_time(x.closest_dump_index, x.location_index))

        random.shuffle(self.clients)
        for client in self.clients:
            ci = client.location_index #Client Index
            best_score = INF
            best_driver_index = -1
            best_tours = -1

            for driver in self.drivers:
                score = 0
                time = 0
                di = driver.current_location_index #driver index
                carry = driver.current_carry

                #if driver.current_carry >= driver.capacity // 3:
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

                score += self.cost_per_kilometer * self.get_real_distance(dump, driver.starting_location_index)  # to get back home (ussualy driver will have just 1 client)
                time += self.get_real_time(dump, driver.starting_location_index)
                #score += max(0, (time - (WORKTIME_DURATION - driver.time_spent) - WORKTIME_DURATION) * driver.overtime_cost)
                score += max(0, (time + driver.time_spent - 2*WORKTIME_DURATION ) * driver.overtime_cost)

                if score < best_score and driver.time_spent + time <= DAY_LENGTH:  
                    best_score = score
                    best_driver_index = driver.driver_index
                    best_tours = tours_needed

            if best_driver_index != -1:
                driver = self.drivers[best_driver_index]
                """empty (if current carry is big)"""
                #if driver.current_carry >= driver.capacity // 3:
                dump_index = self.best_dumps_moving_from_a2b[driver.current_location_index][client.location_index]
                path = self.get_path(driver.current_location_index, dump_index)
                schedule.add_route(Route(self, path, driver, driver.time_spent,
                                        self.get_real_time(driver.current_location_index, dump_index), 0, -driver.current_carry))
                driver.time_spent += self.get_real_time(driver.current_location_index, dump_index)
                driver.current_carry  = 0
                driver.current_location_index = dump_index

                """go to client"""
                added = min(driver.capacity, client.barrels_left)
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
        return schedule, barrels_cost

if __name__ == "__main__":
    #print(372629)
    #print("Odvoz")
    
    problem = Problem(sys.argv[1], sys.argv[2])
    best_schedule, best_barrels_cost = problem.solve2()
    best_value = best_schedule.evaluate(best_barrels_cost)
    for t in range(1000):
        new_schedule, new_barrel_cost = problem.solve2()
        new_value = new_schedule.evaluate(new_barrel_cost)
        if new_value < best_value:
            best_schedule = new_schedule 
            best_value = new_value
            best_barrels_cost = new_barrel_cost

    
    #print(problem.dump_indexes)
    #print(problem.client_indexes)
    best_schedule.print()
    score = best_schedule.evaluate(best_barrels_cost)
    print(score)
        
