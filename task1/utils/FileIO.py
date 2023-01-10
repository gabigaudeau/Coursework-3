import os
import os.path
from task1.loaders.PMLoader import PMLoader as pm
from task1.loaders.DeepLoader import deep_loader
from task1.loaders.SemLoader import sem_loader
from task1.loaders.PTBLoader import ptb_loader
from task1.loaders.ONCompleter import on_completer
from task1.utils.Matcher import DB_SL_matcher
from task1.utils.Converter import DB_PM_converter

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

    wsjs = dict()
    for i in range(25):
        print("Penn Treebank folder: " + str(i))
        if i < 10:
            string = "0" + str(i)
        else:
            string = str(i)
        wsj = traverse_dir("../data/wsj/" + string, ptb_loader)
        wsjs.update(wsj)

    deep_loader.set_src(wsjs)

    deepbank = dict()
    for j in range(22):
        print("DeepBank folder: " + str(j))
        if j < 10:
            string = string = "0" + str(j)
        else:
            string = str(i)

        for letter in ['a', 'b', 'c', 'd', 'e']:
            directory = "../data/deepbank/wsj" + string + letter
            if os.path.exists(directory):
                deepbank.update(traverse_dir(directory, deep_loader))

    semlink = traverse_dir("../data/semlink/00", sem_loader)
    print("Basic Checking Complete.")
    print("SemLink size: {}, Deepbank size: {}".format(len(semlink), len(deepbank)))
    print(deepbank.get('0819006'))


    # print("{} of {} verbs in all Semlink lacked FN link, in {} sentences totally.".format(sem_loader.framemiss, sem_loader.total_verb, sem_loader.framemiss_sentence))
    #DB_SL_matcher(deepbank,semlink,wsj, False)
    # DB_PM_converter(deepbank)
    # on_completer(wsj, "../data/ptb3")  # Fix on5.0 missing files with ptb files
    # deepbank = traverse_dir("../data/deepbank/wsj00a", deep_loader)

    # pm.init("../data/pm/PredicateMatrix.v1.3.txt")