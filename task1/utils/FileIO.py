import os
import os.path
import re

from task1.loaders.DeepLoader import deep_loader
from task1.loaders.SemLoader import sem_loader
from task1.loaders.PTBLoader import ptb_loader
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
    text_file = open("../output.txt", "w")
    for key in deepbank.keys():
        entry = deepbank.get(key)
        output = entry["filename"] + "\n" + entry["string"] + "\n\n"
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
        semlink.update(traverse_dir("../data/semlink/" + string, sem_loader))

    return semlink


# ------- MAIN -------
if __name__ == "__main__":
    print("========================Start Basic Checking=========================")

    # Check current path.
    # print("File location using os.getcwd():", os.getcwd())

    # [1] Process Penn Treebank.
    wsj = process_ptb()

    # Initialise DeepBank loader.
    deep_loader.set_src(wsj)

    # [2] Process DeepBank.
    deepbank = process_db(deep_loader)

    # [3] Process SemLink.
    semlink = process_sml()

    print("Basic Checking Complete.")
    print("SemLink size: {}, Deepbank size: {}".format(len(semlink), len(deepbank)))
    print('{} of {} verbs in all Semlink lacked FN link, in {} sentences totally.'.format(sem_loader.framemiss,
                                                                                          sem_loader.total_verb,
                                                                                          sem_loader.framemiss_sentence)
          )

    print("========================Start Main Process=========================")
    # Create output.txt file with all DB's EDS graphs.
    # create_eds_output(deepbank)

    print("[4] Converting DB to EDS graphs...")
    graphs = {}
    for key in deepbank.keys():
        entry = deepbank.get(key)

        try:
            graphs[entry["doc"] + entry["sent"]] = eds.loads(entry["string"])[0]
        except eds.EDSSyntaxError:
            print("Error: EDS Parsing Syntax Error in sent." + entry["doc"] + entry["sent"])

    print(graphs)

    print("[5] Looping to find verbs")
    for key in graphs.keys():

        # Check if corresponding SemLink entry exists, if not skip.
        if key in semlink.keys():
            sml = semlink.get(key)
            graph = graphs.get(key)

            for node in graph.nodes:
                # Check if predicate is verb, and if it is match it to SemLink verb.
                if re.match(r"_[a-z]*_v_[1-9]", node.predicate):
                    verb = node.predicate.split('_')[1]
                    verb = verb + "-v"

                    for entry in sml:
                        if entry['verb'] == verb:
                            print(True)
                        else:
                            print(verb)
                            print(sml)
            sml = semlink.get(key)
            graph = graphs.get(key)

            for node in graph.nodes:
                # Check if predicate is verb, and if it is match it to SemLink verb.
                if re.match(r"_[a-z]*_v_[1-9]", node.predicate):
                    verb = node.predicate.split('_')[1]
                    verb = verb + "-v"

                    for entry in sml:
                        if entry['verb'] == verb:
                            print(True)
                        else:
                            print(False)
                            print(verb)
                            print(sml)


    #_recover_v_1
    item = graphs.popitem()
    key = item[0]
    graph = item[1]

    print(graph.top)            # e7
    print(graph.lnk)            #
    print(graph.surface)        # None
    print(graph.identifier)     # None
    print("nodes \n")
    for node in graph.nodes:
        print(node.id)          # e7
        print(node.predicate)   # focus_d
        print(node.edges)       # {'ARG1': 'e5', 'ARG2': 'e6'}
        print(node.properties)  # {'SF': 'prop', 'TENSE': 'untensed', 'MOOD': 'indicative', 'PROG': '-', 'PERF': '-'}
        print(node.carg)        # None
        print(node.lnk)         # <0:54>
        print(node.surface)     # None
        print(node.base)        # None

    print(semlink.get(key))

    # Generate DeepLink outputs.
    # DB_SL_matcher(deepbank, semlink, wsj, False)
    # DB_PM_converter(deepbank)

    print("Main Process Complete.")
