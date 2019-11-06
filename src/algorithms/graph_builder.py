from typing import Tuple, Union

from algorithms.graph import RR, Graph


class DirectNodeGraphWithParentNetworkBuilder:
    def __init__(self):
        pass

    def build(self, g: Graph, node: str) -> Tuple[Graph, str]:
        """
        For given node:
            - build the "direct" graph of node
            - merge with "direct" graph of ultimate parent, if exists

        The result might be a network with disjunct graphs.


        "Direct" graph is the graph that connects nodes only via direct parent relationships (in all directions)
        """
        g = g.deepcopy()

        parent_graph, parent_node = self.ultimate_parent_direct_graph(g, node)
        node_graph = self.node_direct_graph(g, node)

        return parent_graph.merge(node_graph), parent_node

    def node_direct_graph(self, g: Graph, node: str) -> Graph:
        g = g.deepcopy()
        return g.remove_edge_type(RR.ULTIMATE).sub(node)

    def ultimate_parent_direct_graph(self, g: Graph, node: str) -> Tuple[Graph, Union[str, None]]:
        """for given node and its full graph, get the sub graph of the ultimate parent
        
        Arguments:
            g {Graph} -- graph of node
            node {str} -- lei of node 
        
        Returns:
            [tuple] -- sub graph of ultimate parent and its lei
        """
        g = g.deepcopy()
        parent = g.get_ultimate_parent(node)

        # if there is no ultimate parent, we return an empty graph
        if parent is None:
            return Graph([]), parent

        # first remove ultimate edge
        g_without_ultimate_edge = g.remove_edge_type(RR.ULTIMATE)

        # get graph for parent
        parent_sub = g_without_ultimate_edge.sub(parent)

        # then subgraph for parent
        return parent_sub, parent
