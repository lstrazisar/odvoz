from People import Driver, Client
from Tour import Path, Route

START_OF_WORKTIME = 480
END_OF_WORKTIME = 960
WORKTIME_DURATION = END_OF_WORKTIME - START_OF_WORKTIME
START_OF_DAY = 0
DAY_LENGTH = 1440
INF = 1e10

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