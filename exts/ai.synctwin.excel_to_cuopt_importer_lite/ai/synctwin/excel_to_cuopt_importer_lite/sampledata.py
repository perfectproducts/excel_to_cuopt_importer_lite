import scipy as sp
import numpy as np
from scipy.sparse import csr_matrix

class SampleData:
    def sample_waypoints_csr_json(self):
        csr = self.sample_waypoints_csr()
        way_point_graph = { 'edges':csr.indices.tolist(), 'offsets':csr.indptr.tolist(), 'weights':csr.data.tolist()}
        return way_point_graph

    def sample_waypoints_csr(self):
        indptr = np.array([0,       3,    5,           9,    11,   13,   15,   17, 18, 19, 20, 21])
        indices = np.array([1, 2, 9, 0, 7, 0, 3, 4, 10, 2, 4, 2, 5, 6, 9, 5, 8, 1,  6,  0,  5])
        data = np.array([1, 1, 2, 1, 2, 1, 1, 1,  3, 2, 3, 2, 1, 2, 1, 3, 4, 2,  3,  1,  1])
        matrix = csr_matrix((data, indices, indptr))
        return matrix 
        # Sample waypoint graph
        way_point_graph = {
            "offsets": [0,       3,    5,           9,    11,   13,   15,   17, 18, 19, 20, 21], # noqa
            "edges":   [1, 2, 9, 0, 7, 0, 3, 4, 10, 2, 4, 2, 5, 6, 9, 5, 8, 1,  6,  0,  5], # noqa
            "weights": [1, 1, 2, 1, 2, 1, 1, 1,  3, 2, 3, 2, 1, 2, 1, 3, 4, 2,  3,  1,  1]  # noqa
        }
        return way_point_graph

    def sample_fleet_data(self):
        fleet_data = {
                "vehicle_locations": [0, 0, 0, 0, 0],
                "capacities": [[10, 12, 15, 8, 10]],
                "vehicle_time_windows": [[0, 80], [1, 40], [3, 30], [5, 80], [20, 100]],
            }
        return fleet_data

    def sample_task_data(self):
        # index 0 for service time states the depot has no service time
        task_data = {
            "task_locations": [0, 1, 3, 4, 6, 8],
            "demand": [[0, 3, 4, 4, 3, 2]],
            "task_time_windows": [
                [0, 1000],
                [3, 20],
                [5, 30],
                [1, 20],
                [4, 40],
                [0, 30],
            ],
            "service_times": [0, 3, 1, 8, 4, 0],
        }
        return task_data