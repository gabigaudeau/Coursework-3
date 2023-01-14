# ------- DESCRIPTION -------
# TODO. Add Description.

# ------- IMPORTS -------
import os
import os.path
import dgl
import torch
import numpy as np
import random

from delphin.codecs import eds
from sklearn.model_selection import train_test_split

from task1.loaders.DeepBankLoader import DeepBankLoader
from task1.loaders.SemLinkLoader import SemLinkLoader
from task1.loaders.PTBLoader import PTBLoader
from task1.scripts.EDSUtils import convert_to_eds, annotate_eds
from task1.scripts.GraphUtils import eds_to_dgl_graph, visualise_graph
from task1.scripts.HeteroRGCN import HeteroRGCN


# ------- FIELDS -------
# Set the seed value all over the place to make this reproducible.
seed_val = 42
# (document_id) (sentence number) (token number) (standard) (verb-v) (VerbNet class)
#  (FrameNet Frame) (PB grouping) (SI grouping) (tense/aspect/mood info)
#  (ArgPointer)-ARG X=(VN Role);(FN Role/Optional Extra Fn Roles)
sem_parser = ["doc", "sent", "token", "stand", "verb", "verbnet", "frame", "PB", "SI", "TAM", "args"]

# nodes is a list of node, node is list of
# [handle, class, startpoint(token ord), endpoint(token ord, not include), extra information] (all elements are strings)
deepbank_parser = ["doc", "sent", "src", "nodes", "head"]


# ------- METHODS -------
def traverse_dir(path, operator):
    sentence_set = {}
    parents = os.listdir(path)
    for parent in parents:
        child = os.path.join(path, parent)
        if os.path.isdir(child):
            sentence_set.update(traverse_dir(child, operator))
        else:
            sentence_set.update(operator.load(child))
    return sentence_set


def create_eds_output(deepbank):
    text_file = open("../deepbank_eds.txt", "w")
    for key in deepbank.keys():
        entry = deepbank.get(key)
        output = entry["doc"] + entry["sent"] + "\n" + entry["string"] + "\n\n"
        text_file.write(output)
    text_file.close()


def create_final_output(graphs):
    text_file = open("../final_eds.txt", "w")
    for key in graphs.keys():
        entry = graphs.get(key)
        decoded = eds.encode(entry)
        output = key + "\n" + decoded + "\n\n"
        text_file.write(output)
    text_file.close()


def process_ptb():
    print("[1] Processing PennTreebank...")

    wsj = dict()
    for i in range(25):
        if i < 10:
            string = "0" + str(i)
        else:
            string = str(i)
        wsj.update(traverse_dir("../data/wsj/" + string, PTBLoader))
    return wsj


def process_db(deep_loader):
    print("[2] Processing DeepBank...")

    deepbank = dict()
    for j in range(22):
        if j < 10:
            string = "0" + str(j)
        else:
            string = str(j)

        for letter in ['a', 'b', 'c', 'd', 'e']:
            directory = "../data/deepbank/wsj" + string + letter
            if os.path.exists(directory):
                deepbank.update(traverse_dir(directory, deep_loader))
    return deepbank


def process_sml():
    print("[3] Processing SemLink...")

    semlink = dict()
    for k in range(25):
        print("SemLink folder: " + str(k))
        if k < 10:
            string = "0" + str(k)
        else:
            string = str(k)
        semlink.update(traverse_dir("../data/semlink/" + string, SemLinkLoader))

    return semlink


# ------- MAIN -------
if __name__ == "__main__":
    print("========================Start Basic Checking=========================")

    # Check current path.
    # print("File location using os.getcwd():", os.getcwd())

    # [1] Process Penn Treebank.
    wsj = process_ptb()

    # Initialise DeepBank loader.
    DeepBankLoader.set_src(wsj)

    # [2] Process DeepBank.
    deepbank = process_db(DeepBankLoader)

    # [3] Process SemLink.
    semlink = process_sml()

    print("Basic Checking Complete.")
    print("SemLink size: {}, Deepbank size: {}".format(len(semlink), len(deepbank)))
    print('{} of {} verbs in all Semlink lacked FN link, in {} sentences totally.'.format(SemLinkLoader.missing_frames,
                                                                                          SemLinkLoader.total_verb,
                                                                                          SemLinkLoader.missing_frame_sentences)
          )

    print("========================Start Main Process=========================")
    # Create deepbank_eds.txt file with all DB's EDS graphs.
    create_eds_output(deepbank)

    print("[4] Converting DB to EDS graphs...")
    eds_graphs = convert_to_eds(deepbank)

    print("[5] Annotate EDS graphs with SemLink data...")
    eds_graphs, complete, incomplete = annotate_eds(eds_graphs, semlink)
    print("Number of EDS graphs that are complete: {}, incomplete: {}".format(len(complete), len(incomplete)))
    create_final_output(eds_graphs)

    print("[6] Create DGL graph dataset from complete EDS graphs...")
    dgl_graphs = {}
    for key in complete:
        dgl_graphs[key] = eds_to_dgl_graph(eds_graphs[key])

    # Create training-validation split
    keys = list(dgl_graphs.keys())
    print(keys)
    random.Random(seed_val).shuffle(keys)

    train_keys = keys[:int((len(keys)+1)*.75)]
    val_keys = keys[int((len(keys)+1)*.75):]

    train_data = [dgl_graphs[key] for key in train_keys]
    val_data = [dgl_graphs[key] for key in val_keys]

    print("[7] Generate visual for a single EDS graph...")
    graph = graphs['0024006']
    visualise_graph(graph)


    print("Main Process Complete.")
    print("========================End Main Process=========================")

    # graph = dgl_graphs['0024006']
    # print(graph) # Graph(num_nodes={'_barrel_n_1': 1, '_for_p': 1, '_new_a_1': 1, '_reserve_n_1': 1, '_the_q': 1,
    # '_total_v_1-fn.Amounting_to': 1, 'card': 3, 'named': 1, 'times': 1, 'udef_q': 2}, num_edges={('_for_p', 'ARG1',
    # '_reserve_n_1'): 1, ('_for_p', 'ARG2', 'named'): 1, ('_new_a_1', 'ARG1', 'named'): 1, ('_the_q', 'BV',
    # 'named'): 1, ('_total_v_1-fn.Amounting_to', 'ARG1-fn.Theme;Attribute', '_reserve_n_1'): 1,
    # ('_total_v_1-fn.Amounting_to', 'ARG2-fn.Value;Value', '_barrel_n_1'): 1, ('card', 'ARG1', '_barrel_n_1'): 1,
    # ('card', 'ARG1', 'named'): 1, ('times', 'ARG2', 'card'): 1, ('times', 'ARG3', 'card'): 1, ('udef_q', 'BV',
    # '_barrel_n_1'): 1, ('udef_q', 'BV', '_reserve_n_1'): 1}, metagraph=[('_for_p', '_reserve_n_1', 'ARG1'),
    # ('_for_p', 'named', 'ARG2'), ('_new_a_1', 'named', 'ARG1'), ('_the_q', 'named', 'BV'),
    # ('_total_v_1-fn.Amounting_to', '_reserve_n_1', 'ARG1-fn.Theme;Attribute'), ('_total_v_1-fn.Amounting_to',
    # '_barrel_n_1', 'ARG2-fn.Value;Value'), ('card', '_barrel_n_1', 'ARG1'), ('card', 'named', 'ARG1'), ('times',
    # 'card', 'ARG2'), ('times', 'card', 'ARG3'), ('udef_q', '_barrel_n_1', 'BV'), ('udef_q', '_reserve_n_1',
    # 'BV')])
    # print(graph.ntypes) # ['_barrel_n_1', '_for_p', '_new_a_1', '_reserve_n_1', '_the_q',
    #                       '_total_v_1-fn.Amounting_to', 'card', 'named', 'times', 'udef_q']
    # print(graph.etypes) # ['ARG1', 'ARG2', 'ARG1', 'BV', 'ARG1-fn.Theme;Attribute', 'ARG2-fn.Value;Value',
    #                       'ARG1', 'ARG1', 'ARG2', 'ARG3', 'BV', 'BV']

    # eds_to_dgl_graph(eds_graphs['0024006'])

    # for key in complete:
    #     print(semlink[key])
    #     print(deepbank[key]['src'])

    # item = graphs.popitem()
    # key = item[0]
    # graph = item[1]
    #
    # print(graph.top)            # e7
    # print(graph.lnk)            #
    # print(graph.surface)        # None
    # print(graph.identifier)     # None
    # print("nodes \n")
    # for node in graph.nodes:
    #     print(node.id)          # e7
    #     print(node.predicate)   # focus_d
    #     print(node.edges)       # {'ARG1': 'e5', 'ARG2': 'e6'}
    #     print(node.properties)  # {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
    #     print(node.carg)        # None
    #     print(node.lnk)         # <0:54>
    #     print(node.surface)     # None
    #     print(node.base)        # None
    #