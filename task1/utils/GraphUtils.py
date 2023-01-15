# ------- DESCRIPTION -------
# Util for pydelphin EDS graphs.
# Imported in FileIO.


# ------- IMPORTS -----------
import dgl
import torch
import numpy as np
from graphviz import Digraph


# ------- METHODS -----------
# Method for converting a pydelphin EDS graph to a DGL heterogeneous graph.
# Input: delphin.eds graph
# Output: dgl.heterograph
def eds_to_dgl_graph(eds):
    ids_to_predicate = {}       # Dictionary with (key: variable id, value: variable predicate).
    predicate_to_counter = {}   # Dictionary with (key: variable predicate, value: number of nodes with predicate type).
    for node in eds.nodes:
        ids_to_predicate[node.id] = node.predicate
        if node.predicate not in predicate_to_counter.keys():
            predicate_to_counter[node.predicate] = 1
        else:
            predicate_to_counter[node.predicate] += 1

    num_nodes_dict = predicate_to_counter.copy()

    ids_to_idx = {}
    for node in eds.nodes:
        if predicate_to_counter[node.predicate] > 0:
            ids_to_idx[node.id] = predicate_to_counter[node.predicate] - 1
            predicate_to_counter[node.predicate] -= 1

    data_dict = {}
    for node in eds.nodes:
        # Each value of the dictionary is a list of edge tuples.
        # Nodes are integer IDs starting from zero.
        # Node IDs of different types have separate counts.
        for label in node.edges.keys():
            dst_id = node.edges[label]
            triplet = (node.predicate, label, ids_to_predicate[dst_id])

            src = torch.Tensor(np.array([ids_to_idx[node.id]]))
            dst = torch.Tensor(np.array([ids_to_idx[dst_id]]))

            data_dict[triplet] = (src, dst)

    return dgl.heterograph(data_dict, idtype=torch.int32, num_nodes_dict=num_nodes_dict)


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
            output.edge(tail_name=node_name[tail], head_name=node_name[head], label=arc, color="blue")
            output.node(name=node_name[tail], color="red")

    output.render('../visual_graph_' + filename)


