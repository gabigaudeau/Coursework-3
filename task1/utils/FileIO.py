import os
import os.path
import re

from task1.loaders.DeepLoader import DeepLoader
from task1.loaders.SemLoader import SemLoader
from task1.loaders.PTBLoader import ptb_loader
from task1.utils.EDSUtils import convert_to_eds, annotate_eds
from task1.utils.GraphUtils import visualise_graph
from delphin.codecs import eds
from task1.loaders.PMLoader import PMLoader as pm
from task1.loaders.ONCompleter import on_completer
from task1.utils.Matcher import DB_SL_matcher
from task1.utils.Converter import DB_PM_converter

# ------- FIELDS -------
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
        wsj.update(traverse_dir("../data/wsj/" + string, ptb_loader))
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
        semlink.update(traverse_dir("../data/semlink/" + string, SemLoader))

    return semlink


# ------- MAIN -------
if __name__ == "__main__":
    print("========================Start Basic Checking=========================")

    # Check current path.
    # print("File location using os.getcwd():", os.getcwd())

    # [1] Process Penn Treebank.
    wsj = process_ptb()

    # Initialise DeepBank loader.
    DeepLoader.set_src(wsj)

    # [2] Process DeepBank.
    deepbank = process_db(DeepLoader)

    # [3] Process SemLink.
    semlink = process_sml()

    print("Basic Checking Complete.")
    print("SemLink size: {}, Deepbank size: {}".format(len(semlink), len(deepbank)))
    print('{} of {} verbs in all Semlink lacked FN link, in {} sentences totally.'.format(SemLoader.missing_frames,
                                                                                          SemLoader.total_verb,
                                                                                          SemLoader.missing_frame_sentences)
          )

    print("========================Start Main Process=========================")
    # Create deepbank_eds.txt file with all DB's EDS graphs.
    create_eds_output(deepbank)

    print("[4] Converting DB to EDS graphs...")
    graphs = convert_to_eds(deepbank)

    print("[5] Annotate EDS graphs...")
    graphs, complete, incomplete = annotate_eds(graphs, semlink)
    print("Number of EDS graphs that are complete: {}, incomplete: {}".format(len(complete), len(incomplete)))
    create_final_output(graphs)

    print("[6] Generate visual for a single EDS graph...")
    graph = graphs['0024006']
    visualise_graph(graph)

    print("Main Process Complete.")
    print("========================End Main Process=========================")

    # for key in complete:
    #     print(semlink[key])
    #     print(deepbank[key]['src'])

    # Generate DeepLink outputs.
    # DB_SL_matcher(deepbank, semlink, wsj, False)
    # DB_PM_converter(deepbank)

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