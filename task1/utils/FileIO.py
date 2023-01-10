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
#  (Framenet Frame) (PB grouping) (SI grouping) (tense/aspect/mood info)
#  (ArgPointer)-ARGX=(VN Role);(FN Role/Optional Extra Fn Roles)
sem_parser = ["doc", "sent", "token", "stand", "verb", "verbnet", "frame", "PB", "SI", "TAM", "args"]

# nodes is a list of node, node is list of
# [hanlde, class, startpoint(token ord), endpoint(token ord, not include), extra information] (all elements are strings)
deepbank_parser = ["doc", "sent", "src", "nodes", "head"]

def traverse_dir(path, operator):
    sentenceSet = {}
    parents = os.listdir(path)
    for parent in parents:
        child = os.path.join(path, parent)
        if os.path.isdir(child):
            sentenceSet.update(traverse_dir(child, operator))
        else:
            sentenceSet.update(operator.load(child))
    return sentenceSet

#  sem_parser=["doc","sent","token","stand","verb","verbnet","frame","PB","SI","TAM","args"]
#  deepbank_parser=["doc","sent","src","nodes","head"]

if __name__ == "__main__":

    print("File location using os.getcwd():", os.getcwd())

    print("========================Start Basic Checking=========================")

    wsj = dict()
    print("[1] Processing PennTreebank...")
    for i in range(25):
        if i < 10:
            string = "0" + str(i)
        else:
            string = str(i)
        wsj.update(traverse_dir("../data/wsj/" + string, ptb_loader))

    deep_loader.set_src(wsj)

    deepbank = dict()
    print("[2] Processing DeepBank...")
    for j in range(22):

        if j < 10:
            string = string = "0" + str(j)
        else:
            string = str(i)

        for letter in ['a', 'b', 'c', 'd', 'e']:
            directory = "../data/deepbank/wsj" + string + letter
            if os.path.exists(directory):
                deepbank.update(traverse_dir(directory, deep_loader))

    semlink = dict()
    print("[3] Processing SemLink...")
    for k in range(25):
        print("SemLink folder: " + str(k))
        if k < 10:
            string = "0" + str(k)
        else:
            string = str(k)
        semlink.update(traverse_dir("../data/semlink/" + string, sem_loader))

    text_file = open("../output.txt", "w")
    for key in deepbank.keys():
        string = deepbank.get(key)["string"]
        # graph = eds.loads(string)[0]
        text_file.write(string)

    text_file.close()

    print("Basic Checking Complete.")
    print("SemLink size: {}, Deepbank size: {}".format(len(semlink), len(deepbank)))

    print("{} of {} verbs in all Semlink lacked FN link, in {} sentences totally.".format(sem_loader.framemiss, sem_loader.total_verb, sem_loader.framemiss_sentence))
    # DB_SL_matcher(deepbank, semlink, wsj, False)
    # DB_PM_converter(deepbank)
