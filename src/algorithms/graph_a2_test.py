import os
import pytest
from graph_builder import DirectNodeGraphWithParentNetworkBuilder
from graph import Graph


@pytest.fixture(scope="class")
def setup(request):
    rr_csv = os.path.join(request.config.rootdir, "data", "gleif_rr.csv")
    lookup_csv = os.path.join(request.config.rootdir, "data", "gleif_lei.csv")
    lei = "969500WU8KVE8U3TL824"
    builder = DirectNodeGraphWithParentNetworkBuilder()

    glei_network = Graph.from_csv(f=rr_csv, limit=None)
    Graph.set_lookup_table(f=lookup_csv)

    parent_graph, ultimate_parent = builder.build(glei_network, lei)

    if ultimate_parent:
        structure = parent_graph.set_levels(ultimate_parent).to_array()
    else:
        structure = parent_graph.set_levels(lei).to_array()

    return structure, lei


def test_structure_exists(setup):

    structure, _ = setup

    assert len(structure["nodes"]) > 0
    # this LEI does not have children nor a parent
    assert len(structure["edges"]) == 0


def test_a2_node_is_level_0(setup):
    # this LEI does not have an ultimate parent

    structure, lei = setup

    a2_node = [n for n in structure["nodes"] if n["id"] == lei][0]

    assert a2_node["level"] == 0

