# This module creates graph from deepbank EDS.
from graphviz import Digraph


def visualise_graph(graph):
    output = Digraph(format='svg')
    node_name = {}
    i = 0
    while i < len(graph.nodes):
        node_name[graph.nodes[i].id] = graph.nodes[i].predicate
        i += 1

    for tail, arc, head in graph.edges:
        output.edge(tail_name=node_name[tail], head_name=node_name[head], label=arc)

    output.render('../single_eds_graph')
