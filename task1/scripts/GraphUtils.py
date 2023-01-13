# This module creates graph from deepbank EDS.
from graphviz import Digraph
import dgl
import torch
import numpy as np


# print(graph.top)            # e7
# print(graph.lnk)            #
# print(graph.surface)        # None
# print(graph.identifier)     # None
# print(node.id)              # e7
# print(node.predicate)       # focus_d
# print(node.edges)           # {'ARG1': 'e5', 'ARG2': 'e6'}
# print(node.properties)      # {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
# print(node.carg)            # None
# print(node.lnk)             # <0:54>
# print(node.surface)         # None
# print(node.base)            # None


def eds_to_dgl_graph(eds):
    ids_to_predicate = {}
    predicate_to_counter = {}
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


def visualise_graph(eds):
    output = Digraph(format='svg')
    node_name = {}
    i = 0
    while i < len(eds.nodes):
        node_name[eds.nodes[i].id] = eds.nodes[i].predicate
        i += 1

    for tail, arc, head in eds.edges:
        output.edge(tail_name=node_name[tail], head_name=node_name[head], label=arc)

    output.render('../single_eds_graph')
