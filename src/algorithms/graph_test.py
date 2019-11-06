import pytest
from os import path
from graph import RR, Graph
import pandas as pd 

@pytest.fixture
def rr_test_csv(request):
    return path.join(request.config.rootdir, 'src/test_data', 'rr-test.csv')

@pytest.fixture
def lookup_test_csv(request):
    return path.join(request.config.rootdir, 'src/test_data', 'lei-test.csv')

def test_RR():
    rr = RR('LEI_1', 'LEI_2', RR.DIRECT)

    assert rr.start == 'LEI_1'
    assert rr.end == 'LEI_2'
    assert rr.rel_type == 'IS_DIRECTLY_CONSOLIDATED_BY'

    direct = RR('LEI_1', 'LEI_2', RR.DIRECT)
    assert direct.rel_type == 'IS_DIRECTLY_CONSOLIDATED_BY'

    ultimate = RR('LEI_1', 'LEI_2', RR.ULTIMATE)
    assert ultimate.rel_type == 'IS_ULTIMATELY_CONSOLIDATED_BY'

    branch = RR('LEI_1', 'LEI_2', RR.BRANCH)
    assert branch.rel_type == 'IS_INTERNATIONAL_BRANCH_OF'

def test_Graph_from_file(rr_test_csv):
    g = Graph.from_csv(rr_test_csv)

    assert list(g.nodes) == ['LEI_1', 'DIRECT_PARENT_LEI', 'ULTIMATE_PARENT_LEI']
    assert list(g.edges) == [
            ('LEI_1', 'DIRECT_PARENT_LEI', 0),
            ('LEI_1', 'ULTIMATE_PARENT_LEI', 0),
    ]

def test_node_get_direct_and_ultimate_parent():
    g = Graph([])

    assert g.get_direct_parent('ROI') is None
    assert g.get_ultimate_parent('ROI') is None

    g = Graph([
        RR('ROI', 'P1', RR.DIRECT),
    ])
    assert g.get_direct_parent('ROI') == 'P1'
    assert g.get_ultimate_parent('ROI') is None

    g = Graph([
        RR('ROI', 'UP1', RR.ULTIMATE),
    ])

    assert g.get_direct_parent('ROI') is None
    assert g.get_ultimate_parent('ROI') == 'UP1'

    g = Graph([
        RR('ROI', 'P1', RR.DIRECT),
        RR('ROI', 'UP1', RR.ULTIMATE),
    ])

    assert g.get_direct_parent('ROI') == 'P1'
    assert g.get_ultimate_parent('ROI') == 'UP1'

    # Catches inconsistency (more than one direct/ultimate parent)
    # TODO: Do while initializing graph?

    #  g = Graph([
    #      RR('ROI', 'P1', RR.DIRECT),
    #      RR('ROI', 'P1', RR.DIRECT),
    #  ])
    #  try:
    #      g.get_direct_parent('ROI')
    #  except Exception as e:
    #      assert str(e) == 'Found more than one Direct Parent for node ROI'
    #      return
    #  assert False, 'Expected Exception due to multiple direct parents'

def test_node_has_direct_and_ultimate_parent():
    g = Graph([])

    assert not g.has_direct_parent('ROI')
    assert not g.has_ultimate_parent('ROI')

    g = Graph([
        RR('ROI', 'P1', RR.DIRECT),
        RR('ROI', 'UP1', RR.ULTIMATE),
    ])

    assert g.has_direct_parent('ROI')
    assert g.has_ultimate_parent('ROI')

def test_remove_edge_type():
    g = Graph([
        RR('ROI', 'P1', RR.DIRECT),
        RR('ROI', 'UP1', RR.ULTIMATE),
        RR('A', 'B', RR.ULTIMATE),
        RR('C', 'A', RR.ULTIMATE),
        RR('C', 'A', RR.DIRECT),
        RR('A', 'C', RR.ULTIMATE),
    ])

    g.remove_edge_type(RR.ULTIMATE)
    assert sorted(list(g.edges)) == [
        ('C', 'A', 1),
        ('ROI', 'P1', 0),
    ]

def test_lookup_read_in(lookup_test_csv):
    g = Graph([])
    Graph.set_lookup_table(lookup_test_csv)

    assert isinstance(g.lookup_table, pd.DataFrame)

def test_lookup(rr_test_csv, lookup_test_csv):
    g = Graph.from_csv(rr_test_csv)
    Graph.set_lookup_table(lookup_test_csv)
    assert g.lookup_table.shape[0] == 3
    assert g.get_node_label("LEI_1") == "company1"

def test_node_not_found_in_G(rr_test_csv, lookup_test_csv):
    g = Graph.from_csv(rr_test_csv)
    Graph.set_lookup_table(lookup_test_csv)

    a = g.sub('LEI_2').to_array()
    nodes = a['nodes']
    edges = a['edges']

    assert g.lookup_table.shape[0] == 3    
    assert edges == []
    assert nodes == [{
        'label': 'company2',
        'title': 'LEI_2',
        'id': 'LEI_2',
        'level': None,
        'no_parent': None,
    }]

def test_node_not_found_in_G_and_lookup(rr_test_csv, lookup_test_csv):
    g = Graph.from_csv(rr_test_csv)
    g.set_lookup_table(lookup_test_csv)

    a = g.sub('LEI_NOT_FOUND').to_array()
    nodes = a['nodes']
    edges = a['edges']

    assert edges == []
    assert nodes == [{
        'label': 'id not found',
        'title': 'LEI_NOT_FOUND',
        'id': 'LEI_NOT_FOUND',
        'level': None,
        'no_parent': None,
    }]

def test_node_found_in_G(rr_test_csv, lookup_test_csv):
    g = Graph.from_csv(rr_test_csv)
    g.set_lookup_table(lookup_test_csv)
    a = g.sub('LEI_1').to_array()
    nodes = a['nodes']
    edges = a['edges']

    labels = [n['label'] for n in nodes]
    assert len(edges) == 2
    assert len(nodes) == 3
    assert 'company1' in labels

def test_Graph_to_array(lookup_test_csv):
    g = Graph([
        RR('LEI_1', 'LEI_2', RR.DIRECT),
        #  RR('LEI_1', 'LEI_3', RR.ULTIMATE),

        # TODO: More cases

        #  RR('LEI_2', 'LEI_X', RR.DIRECT),
        #  RR('LEI_X', 'LEI_1', RR.ULTIMATE),

        #  RR('LEI_A', 'LEI_X', RR.DIRECT),
        #  RR('LEI_A', 'LEI_X', RR.ULTIMATE),

        #  RR('LEI_B', 'LEI_Z', RR.DIRECT),
        #  RR('LEI_B', 'LEI_I', RR.ULTIMATE),
    ])
    print(lookup_test_csv)
    Graph.set_lookup_table(lookup_test_csv)

    a = g.to_array()
    nodes = a['nodes']
    edges = a['edges']

    assert type(nodes) is list and len(nodes) > 0
    assert type(edges) is list and len(edges) > 0

    assert nodes == [
        {
            'id': 'LEI_1',
            'title': 'LEI_1',
            'label': 'company1',
            'level': None,
            'no_parent': None,
        },
        {
            'id': 'LEI_2',
            'title': 'LEI_2',
            'label': 'company2',
            'level': None,
            'no_parent': None,
        }
    ]

    assert edges == [
        {
            'from': 'LEI_1',
            'to': 'LEI_2',
            'label': 'IS_DIRECTLY_CONSOLIDATED_BY',
        },
    ]

def test_Graph_subgraphs():
    g = Graph([

        # Parent chain
        RR('LEI_1', 'LEI_2', RR.DIRECT),
        RR('LEI_2', 'LEI_3', RR.DIRECT),
        RR('LEI_3', 'LEI_4', RR.DIRECT),

        # Isolated 2-node-graph
        RR('LEI_SOLO_A', 'LEI_SOLO_B', RR.DIRECT),

        # Multiple/duplicate edges
        RR('LEI_A', 'LEI_B', RR.DIRECT),
        RR('LEI_A', 'LEI_B', RR.DIRECT),  # duplicates will end up unique
        RR('LEI_A', 'LEI_B', RR.DIRECT),  # duplicates will end up unique
        RR('LEI_A', 'LEI_B', RR.DIRECT),  # duplicates will end up unique

        RR('LEI_B', 'LEI_A', RR.DIRECT),  # opposite direction

        RR('LEI_A', 'LEI_B', RR.ULTIMATE),  # ultimate same as direct

        # multiple (some same) ultimate/direct
        RR('LEI_A', 'LEI_B', RR.DIRECT),
        RR('LEI_A', 'LEI_C', RR.DIRECT),
        RR('LEI_A', 'LEI_D', RR.ULTIMATE),

        RR('LEI_D', 'LEI_E', RR.BRANCH),


        # Complex...
        #     B   D
        #    / \ /
        #   A   C   F
        #      / \ /
        #     E  (X)  K
        #        / \ /
        #   J   G   H
        #    \ /
        #     I
        RR('A', 'B', RR.DIRECT),
        RR('C', 'B', RR.DIRECT),
        RR('C', 'D', RR.ULTIMATE),
        RR('E', 'C', RR.ULTIMATE),
        RR('X', 'C', RR.DIRECT),
        RR('X', 'F', RR.DIRECT),
        RR('G', 'X', RR.BRANCH),
        RR('H', 'X', RR.DIRECT),
        RR('H', 'K', RR.DIRECT),
        RR('I', 'G', RR.DIRECT),
        RR('I', 'J', RR.DIRECT),

    ])

    # CASE: Grab start of chain
    a = g.sub('LEI_1').to_array()
    assert sorted([node['id'] for node in a['nodes']]) == ['LEI_1', 'LEI_2', 'LEI_3', 'LEI_4']
    assert sorted([(node['from'], node['to']) for node in a['edges']]) == [

        # NOTE: Always two edges (e.g. direct parent / direct child)

        ('LEI_1', 'LEI_2'),
        #  ('LEI_2', 'LEI_1'),

        ('LEI_2', 'LEI_3'),
        #  ('LEI_3', 'LEI_2'),

        ('LEI_3', 'LEI_4'),
        #  ('LEI_4', 'LEI_3'),
    ]

    # CASE: Grab middle of chain
    a = g.sub('LEI_2').to_array()
    assert sorted([node['id'] for node in a['nodes']]) == ['LEI_1', 'LEI_2', 'LEI_3', 'LEI_4']

    # CASE: Grab end of chain
    a = g.sub('LEI_4').to_array()
    assert sorted([node['id'] for node in a['nodes']]) == ['LEI_1', 'LEI_2', 'LEI_3', 'LEI_4']

    # CASE: Grab different isolated subgraph
    a = g.sub('LEI_SOLO_A').to_array()
    #  assert sorted([node['id'] for node in a['nodes']]) == ['LEI_SOLO_A', 'LEI_SOLO_B']

    # CASE: Mixed
    a = g.sub('LEI_A').to_array()
    assert sorted([node['id'] for node in a['nodes']]) == ['LEI_A', 'LEI_B', 'LEI_C', 'LEI_D', 'LEI_E']

    # CASE: Complex
    #     B   D
    #    / \ /
    #   A   C   F
    #      / \ /
    #     E  (X)  K
    #        / \ /
    #   J   G   H
    #    \ /
    #     I
    a = g.sub('X').to_array()
    assert sorted([node['id'] for node in a['nodes']]) == ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'X']
    assert sorted([(node['from'], node['to']) for node in a['edges']]) == [

        ('A', 'B'),
        ('C', 'B'),
        ('C', 'D'),
        ('E', 'C'),
        ('G', 'X'),
        ('H', 'K'),
        ('H', 'X'),
        ('I', 'G'),
        ('I', 'J'),
        ('X', 'C'),
        ('X', 'F'),
    ]

    # TODO: Test edges

@pytest.mark.skip("Direction not implemented")
def test_Graph_direction():
    assert False, "TODO: Implement MultiDiGraph"
