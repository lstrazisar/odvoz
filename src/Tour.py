from People import Driver

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