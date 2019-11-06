import json
import csv
import copy
from typing import Iterator, KeysView, Union

import networkx as nx
import pandas as pd


def iter_csv(f: str, limit: int = None):
    """
    Convenience function to retrieve rows from a csv file.
    """
    with open(f) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for i, row in enumerate(reader):
            if limit is not None and limit < i + 1:
                return
            yield row


class RR:
    DIRECT = 'IS_DIRECTLY_CONSOLIDATED_BY'
    #  DIRECT_CHILD = 'direct_child'

    ULTIMATE = 'IS_ULTIMATELY_CONSOLIDATED_BY'
    #  ULTIMATE_CHILD = 'ultimate_child'

    BRANCH = 'IS_INTERNATIONAL_BRANCH_OF'

    #  HEADQUARTERS = 'headquarters'

    def __init__(self, start: str, end: str, rel_type: str):
        self.start = start
        self.end = end
        self.rel_type = rel_type

    @staticmethod
    def from_csv_row(row: dict) -> 'RR':
        return RR(
            row['Relationship.StartNode.NodeID'],
            row['Relationship.EndNode.NodeID'],
            row['Relationship.RelationshipType']
        )


class Graph:
    lookup_table = pd.DataFrame()

    def __init__(self, rr: Iterator[RR]):
        self.g = nx.MultiDiGraph()
        self.__load_rr(rr)

    def __str__(self):
        return self.to_json()

    @property
    def nodes(self):
        return self.g.nodes

    @property
    def edges(self):
        return self.g.edges

    @property
    def out_edges(self):
        return self.g.out_edges

    @property
    def in_edges(self):
        return self.g.in_edges

    def __load_rr(self, rr: Iterator[RR]):
        """
        This helper function is used to build the graph from csv files.
        It reads the individual rows from a tuple generator representing lines
        in the csv file.
        """

        def mk_edge(rr: RR):
            """
            Edge transformation function to bring the edge format from custom
            class RR to networkx tuple form (start, end, data).
            """
            return rr.start, rr.end, {'type': rr.rel_type}

        self.g.add_edges_from(map(mk_edge, list(rr)))

    def deepcopy(self) -> 'Graph':
        return copy.deepcopy(self)

    def merge(self, other_graph: 'Graph') -> 'Graph':
        """
        Wrapper function to merge the Networkx graph attributes
        of the custom Graph class.
        """
        return Graph.from_graph(nx.compose(self.g, other_graph.g))

    def get_edge_data(self, u: str, v: str, key: str = None, default: dict = None):
        """
        Wrapper function to retrieve data associated with the specified edge.
        """
        default = {} if not default else default
        return self.g.get_edge_data(u, v, key, default)

    def get_edge_types(self, u: str, v: str) -> list:
        """
        Wrapper function to retrieve edge type.
        """
        return [e['type'] for e in self.get_edge_data(u, v).values()]

    def get_direct_parent(self, node: str) -> str:
        """
        This function retrieves the direct parent of a given edge
        based on the edge relation type.
        """
        for e in self.out_edges(node):
            if 'IS_DIRECTLY_CONSOLIDATED_BY' in self.get_edge_types(e[0], e[1]):
                return e[1]

    def get_ultimate_parent(self, node: str) -> str:
        """
        This function retrieves the ultimate parent of a given edge
        based on the edge relation type.
        """
        for e in self.out_edges(node):
            if 'IS_ULTIMATELY_CONSOLIDATED_BY' in self.get_edge_types(e[0], e[1]):
                return e[1]

    def remove_edge_type(self, rel_type: str):
        """
        This function removes all edges of a given type from the graph.
        It updates the graph object inplace.
        """
        remove = [(u, v, key) for (u, v, key) in self.edges if self.get_edge_data(u, v, key=key)['type'] == rel_type]
        self.g.remove_edges_from(remove)
        return self

    def has_direct_parent(self, node: str) -> bool:
        """
        Convenience function to check if a node has a direct parent.
        """
        return self.get_direct_parent(node) is not None

    def has_ultimate_parent(self, node: str) -> bool:
        """
        Convenience function to check if a node has a ultimate parent.
        """
        return self.get_ultimate_parent(node) is not None

    def connected_nodes(self, lei: str) -> KeysView:
        """
        This function transforms the graph to a undirected version of itself
        and finds all connected nodes for a given LEI identifier, based on all
        computable paths from the LEI node.
        """
        # NOTE: Convertinv graph to undirected, in order to easily get all connected nodes regardless of edge direction
        #       (i.e. including inbound connections)
        return nx.single_source_shortest_path(self.g.to_undirected(), lei).keys()

    def get_shortest_direct_parent_path_lengths(self, reference_node: str) -> dict:
        """
        This function computes the path lengths from a given reference to all
        other via direct parent edges reachable nodes. It does NOT convert the graph to a undirected
        version before and respects directions. Dict form is {node_id: distance}.
        """
        g = self.deepcopy().remove_edge_type(RR.ULTIMATE)  # TODO: What about BRANCH?
        return dict(nx.single_target_shortest_path_length(g.g, reference_node))

    def sub(self, lei: str) -> 'Graph':
        """
        This function subsets the graph based on the nodes connected with the
        given LEI node.
        """
        self.g.add_node(lei)  # Add dummy node
        nodes = self.connected_nodes(lei)
        return Graph.from_graph(self.g.subgraph(nodes))

    def get_node_label(self, lei: str) -> str:
        """
        Wrapper function to retrieve the legal name of an entity based
        on its LEI from the lookup table attached to the graph.
        """
        try:
            return self.lookup_table.loc[lei]['Entity.LegalName']
        except KeyError:
            return 'id not found'

    def transform_node(self, node: dict) -> dict:
        """
        Convenience function to rename node dictionary keys for final return array.
        """
        return {
            'id': node['id'],
            'title': node['id'],
            'label': self.get_node_label(node['id']),
            'level': node.get('level'),
            'no_parent': node.get('no_parent'),
        }

    def transform_link(self, link: dict) -> dict:
        """
        Convenience function to rename edge dictionary keys for final return array.
        """
        return {
            'from': link['source'],
            'to': link['target'],
            'label': link['type'],
        }

    def to_array(self) -> dict:
        """
        Convenience function for preparing the graph data to json dump.
        """
        data = nx.node_link_data(self.g)
        return {
            'nodes': list(map(self.transform_node, data['nodes'])),
            'edges': list(map(self.transform_link, data['links'])),
        }

    def to_json(self):
        return json.dumps(self.to_array(), indent=2)

    def set_levels(self, parent: str = None) -> 'Graph':
        """
        This function sets the levels on a graph as a node attribute.
        """
        subgraph = self
        if parent:
            distances = self._level_computation(subgraph=subgraph, root_node=parent)
            distances = {
                node: {
                    'level': distances[node] if distances[node] is not 'no_parent' else 1,
                    'no_parent': False if distances[node] is not 'no_parent' else True
                } for node in distances
            }
            nx.set_node_attributes(subgraph.g, distances)
        else:
            print('No parent found. TODO')
            raise ValueError
        return subgraph

    @staticmethod
    def _level_computation(subgraph, root_node: str) -> dict:
        """
        This function computes the levels with respect to the given root node by using
        single target shortest path algorithm from networkx. It returns a dictionary
        of node ids with the computed depth in the graph.
        """
        compute_graph = subgraph.remove_edge_type(rel_type=RR.ULTIMATE)
        distances = nx.single_target_shortest_path_length(compute_graph.g, target=root_node)
        distances = dict(distances)
        distances.update({node: 'no_parent' for node in subgraph.nodes if not distances.get(node) and
                          node is not root_node})
        distances.update({root_node: 0})
        return distances

    @staticmethod
    def from_graph(_g: nx.MultiDiGraph) -> 'Graph':
        g = Graph([])
        g.g = copy.deepcopy(_g)
        return g

    @staticmethod
    def set_lookup_table(f):
        Graph.lookup_table = pd.read_csv(f, index_col=["LEI"], usecols=["LEI", "Entity.LegalName"])

    @staticmethod
    def from_csv(f: str, limit: int = None) -> 'Graph':
        return Graph(RR.from_csv_row(row) for row in iter_csv(f, limit))
