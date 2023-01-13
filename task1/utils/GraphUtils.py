# This module creates graph from deepbank.
import re
from graphviz import Digraph
from graphviz import dot as dotx
import pydot

sem_parser = ["doc", "sent", "token", "stand", "verb", "verbnet", "frame", "PB", "SI", "TAM", "args"]
deepbank_parser = ["doc", "sent", "src", "head", "nodes"]


class Node:
    def __init__(self, handle, cls, addr, *, name=None, attr=None):
        self.handle = handle
        self.cls = cls
        self.addr = list(addr)  # typeof tuple
        self.attr = attr
        self.name = name
        self.prev = []  # (edge type, previous points)
        self.succ = []  # (edge type, succeeding points)

    def setName(self, name):
        self.name = name

    def setAttr(self, attr):
        self.attr = attr

    def addPrev(self, startpoint):
        self.prev.append(list(startpoint))

    def addSucc(self, endpoint):
        self.succ.append(list(endpoint))


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
