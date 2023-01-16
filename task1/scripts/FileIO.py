# ------- DESCRIPTION -------
# Main class with input and output processing.


# ------- IMPORTS -------
import os
import os.path

from delphin.codecs import eds

from task1.loaders.DeepBankLoader import DeepBankLoader
from task1.loaders.SemLinkLoader import SemLinkLoader
from task1.loaders.PTBLoader import PTBLoader
from task1.utils.EDSUtils import convert_to_eds, annotate_eds
from task1.utils.GraphUtils import visualise_graph


# ------- FIELDS -------
# Set the seed value to make this reproducible.
seed_val = 42
sem_parser = ["doc", "sent", "token", "stand", "verb", "verbnet", "frame", "PB", "SI", "TAM", "args"]
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


def create_eds_output(graphs, filename):
    text_file = open(filename, "w")
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

    print("[4] Converting DB to EDS graphs...")
    eds_graphs = convert_to_eds(deepbank)
    # Create deepbank_eds.txt file with all DB's EDS graphs.
    create_eds_output(eds_graphs, "../deepbank_eds.txt")

    print("[5] Generate visual for an EDS graph...")
    graph = eds_graphs['0024006']
    visualise_graph(graph, "without_annotations")

    print("[6] Annotate EDS graphs with SemLink data...")
    eds_graphs, complete, incomplete = annotate_eds(eds_graphs, semlink)
    print("Number of EDS graphs that are complete: {}, incomplete: {}".format(len(complete), len(incomplete)))
    create_eds_output(eds_graphs, "../final_eds.txt")

    print("[7] Generate visual for an annotated EDS graph...")
    graph = eds_graphs['0024006']
    visualise_graph(graph, "with_annotations")

    print("Main Process Complete.")
    print("========================End Main Process=========================")