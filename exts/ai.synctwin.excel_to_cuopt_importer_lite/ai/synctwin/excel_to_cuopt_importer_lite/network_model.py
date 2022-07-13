from pydantic import BaseModel 
from typing import List 
from pxr import Gf 
import networkx as nx 

class Location3d(BaseModel):
    x : float = 0
    y : float = 0
    z : float = 0 

class NetworkNodeModel(BaseModel):
    name: str = ""
    node_type: str = ""
    position: Location3d = Location3d() 

class NetworkEdgeModel(BaseModel):
    from_node_idx:int 
    to_node_idx:int 
    weight:float 
    weight_back: float = 0 # if directed edge > 0 

class NetworkModel(BaseModel):
    nodes: List[NetworkNodeModel]=[]
    edges:List[NetworkEdgeModel]=[]
    
    def node_by_name(self, name:str)->NetworkNodeModel:
        for node in self.nodes:
            if node.name == name : 
                return node
        return None  

    def contains_node(self, name:str)->bool:
        return self.node_by_name(name) != None 


def networkx_graph_to_network_model(graph:nx.Graph)->NetworkModel:
    result = NetworkModel()
    id2idx = {}
    for node_id in graph.nodes:
        node = graph.nodes[node_id]
        pos = node['position']
        node_type = node['node_type']

        node_model = NetworkNodeModel(            
            name=node['name'], 
            node_type=node_type, 
            position=Location3d(x=pos[0],y=pos[1],z=pos[2]))
        id2idx[node_id] = len(result.nodes)
        result.nodes.append(node_model)

    for a,b in graph.edges:
        node_a = graph.nodes[a]    
        node_b = graph.nodes[b]    
        edge_vector = node_b['position'] - node_a['position']
        weight = edge_vector.GetLength()
        edge_model = NetworkEdgeModel(from_node_idx=id2idx[a], to_node_idx=id2idx[b], weight=weight, weight_back=weight)
        result.edges.append(edge_model)
    return result

def network_model_to_networkx_graph(model:NetworkModel)->nx.Graph:
    graph = nx.Graph()
    idx = 0
    for node in model.nodes:
        p = node.position
        graph.add_node(idx, name = node.name, node_type= node.node_type, position=[p.x,p.y,p.z] )
        idx+=1
    for edge in model.edges:
        graph.add_edge(edge.from_node_idx, edge.to_node_idx, weight=edge.weight)
        if edge.weight != edge.weight_back: 
            print("# for directed graph use nx.DiGraph")
    return graph


