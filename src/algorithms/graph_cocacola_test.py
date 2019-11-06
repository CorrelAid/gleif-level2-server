import os
import pytest
from graph_builder import DirectNodeGraphWithParentNetworkBuilder
from graph import Graph


@pytest.fixture(scope="class")
def setup():
    rr_csv = os.path.join("data", "gleif_rr.csv")
    lookup_csv = os.path.join("data", "gleif_lei.csv")
    lei = "UWJKFUJFZ02DKWI3RY53"
    builder = DirectNodeGraphWithParentNetworkBuilder()

    glei_network = Graph.from_csv(f=rr_csv, limit=None)
    Graph.set_lookup_table(f=lookup_csv)

    parent_graph, ultimate_parent = builder.build(glei_network, lei)

    structure = parent_graph.set_levels(lei).to_array()
    return structure, lei


@pytest.mark.skip("Only for local testing when data is available")
def test_nodes_edges_more_than_0(setup):
    structure, lei = setup

    assert len(structure["nodes"]) > 0
    assert len(structure["edges"]) > 0


# @pytest.mark.skip("Only for local testing when data is available")
def test_lei_in_nodes(setup):
    structure, lei = setup
    cocacolacompany_node = [n for n in structure["nodes"] if n["id"] == lei][0]

    assert cocacolacompany_node["level"] == 0


@pytest.mark.skip("Only for local testing when data is available")
def test_direct_children(setup):
    structure, lei = setup
    # direct children
    direct_children = [n for n in structure["nodes"] if n["level"] == 1]
    assert len(direct_children) == 8

