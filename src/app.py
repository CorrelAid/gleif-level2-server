import os
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from algorithms.graph import Graph
from algorithms.graph_builder import DirectNodeGraphWithParentNetworkBuilder as Builder

origins = ["*"]

api = FastAPI()
api.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"]
)
ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA_PATH = os.path.join(ROOT_DIR, "data")

relationship_data_path = os.path.join(DATA_PATH, "gleif_rr.csv")
lei_lookup_data_path = os.path.join(DATA_PATH, "gleif_lei.csv")

glei_network = Graph.from_csv(f=relationship_data_path, limit=None)
Graph.set_lookup_table(f=lei_lookup_data_path)


@api.get("/company/{node_id}/structure")
def get_company_structure(node_id: str):
    """
    This endpoint returns the complete holding structure based on a single node id.
    :param node_id:
    :return:
    """
    builder = Builder()
    parent_graph, parent_node = builder.build(glei_network, node_id)

    if parent_node is None:
        # no ultimate parent 
        return parent_graph.set_levels(node_id).to_array()
    else: 
        return parent_graph.set_levels(parent_node).to_array()
