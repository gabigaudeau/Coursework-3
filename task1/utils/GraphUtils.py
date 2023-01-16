# ------- DESCRIPTION -------
# Util for pydelphin EDS graphs.
# Imported in FileIO.


# ------- IMPORTS -----------
from graphviz import Digraph


# ------- METHODS -----------
# Method for generating '.svg' visualisation of a pydelphin EDS graph.
# Input: delphin.eds graph
def visualise_graph(eds, filename):
    node_name = {}
    i = 0
    while i < len(eds.nodes):
        node_name[eds.nodes[i].id] = eds.nodes[i].predicate
        i += 1

    output = Digraph(format='png')
    for tail, arc, head in eds.edges:
        if "-fn." in arc:
            output.edge(tail_name=node_name[tail], head_name=node_name[head], label=arc, color="blue", fontcolor="blue")
            output.node(name=node_name[tail], color="red", fontcolor="red")
        else:
            output.edge(tail_name=node_name[tail], head_name=node_name[head], label=arc)

    output.render('../visual_graph_' + filename)


