import networkx as nx 
import requests as req
from .transport_fleet_customdata import TransportFleetModelCustomData

from .transport_fleet_model import TransportFleetModel
from .network_builder import NetworkBuilder
from .network_customdata import NetworkModelCustomData 
from .network_model import NetworkModel, network_model_to_networkx_graph
from pxr import Usd 


class CuOptConnector:
    def __init__(self, host_url) -> None:
        self._host_url = host_url
        self._is_connected = False 
        self.network=NetworkModel()


    def is_connected(self)->bool:
        response = req.get(f"{self._host_url}/health")
        print(response)
        return response.status_code == 200

    
    
    def show_results(self, res):
        print("\n====================== Response ===========================\n")
        print("Solver status: ", res["status"])
        if res["status"] == 0:
            print("Cost         : ", res["solution_cost"])
            print("Vehicle count: ", res["num_vehicles"])
            for key, item in res["vehicle_data"].items():
                print()
                print("Vehicle: ", key)
                print("Tasks  : ", item['tasks'])
                print("Routes : ", item['routes'])
                print("Type   : ", item['type'], "\n\n")

        else:
            print("Error: ", res["error"])
        print("\n======================= End ===============================\n")

    def solve(self):
        # larger problems might require more time and/or more climbers
        solver_config = {"time_limit": 0.01, "number_of_climbers": 128}

        data_params = {"return_data_state": False} 
        solve_parameters = {
            "use_capacities": True,
            "use_vehicle_time_windows": True,
            "use_task_time_windows": True,
            "is_pickup_and_delivery": False,
            "return_status": False,
            "return_data_state": False,
        }
        solver_config_response = req.post(
            f"{self._host_url}/set_solver_config", params=data_params, json=solver_config
        )
        print(f"SOLVER CONFIG ENDPOINT RESPONSE: {solver_config_response.json()}\n")

        # Solve the problem
        # Note for now all vehicles will start and end at the depot
        solver_response = req.get(
            f"{self._host_url}/get_optimized_routes", params=solve_parameters
        )
        print(f"SOLVER RESPONSE: {solver_response.json()}\n")
        self.show_results(solver_response.json()["response"]["solver_response"])
    