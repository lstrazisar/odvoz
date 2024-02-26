
class Driver:

    def __init__(self, problem, starting_location_index, capacity, overtime_cost, driver_index, driver_start):
        self.problem = problem
        self.starting_location_index = starting_location_index
        self.current_location_index = starting_location_index
        self.capacity = capacity
        self.overtime_cost = overtime_cost
        self.driver_index = driver_index
        self.time_spent = driver_start
        self.current_carry = 0
        self.clients_visited = []

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