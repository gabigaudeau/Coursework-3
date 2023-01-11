import os
import os.path
from task1.loaders.PMLoader import PMLoader as pm
from task1.loaders.DeepLoader import deep_loader
from task1.loaders.SemLoader import sem_loader
from task1.loaders.PTBLoader import ptb_loader
from task1.loaders.ONCompleter import on_completer
from task1.utils.Matcher import DB_SL_matcher
from task1.utils.Converter import DB_PM_converter
from delphin.codecs import eds

# (document_id) (sentence number) (token number) (standard) (verb-v) (VerbNet class)
#  (FrameNet Frame) (PB grouping) (SI grouping) (tense/aspect/mood info)
#  (ArgPointer)-ARG X=(VN Role);(FN Role/Optional Extra Fn Roles)
sem_parser = ["doc", "sent", "token", "stand", "verb", "verbnet", "frame", "PB", "SI", "TAM", "args"]

# nodes is a list of node, node is list of
# [handle, class, startpoint(token ord), endpoint(token ord, not include), extra information] (all elements are strings)
deepbank_parser = ["doc", "sent", "src", "nodes", "head"]


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


def process_db(loader):
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
                                                                                          sem_loader.framemiss_sentence))

    # Create output.txt file with all DB's EDS graphs.
    # create_eds_output(deepbank)

    graphs = {}
    for key in deepbank.keys():
        entry = deepbank.get(key)

        try:
            graphs[entry["doc"] + entry["sent"]] = eds.loads(entry["string"])[0]
        except eds.EDSSyntaxError:
            print("Error: EDS Parsing Syntax Error in sent." + entry["doc"] + entry["sent"])

    print(graphs)

    # Generate DeepLink outputs.
    # DB_SL_matcher(deepbank, semlink, wsj, False)
    # DB_PM_converter(deepbank)
