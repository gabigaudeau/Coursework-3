# ------- DESCRIPTION -------
# Loader used for extracting tokens from Deepbank file (deepbank1.1 style).
# Automatically convert deepbank-style word position labels (based on characters) to Penn TreeBank-style.
# Penn Treebank is based on extended tokens (and includes some -NONE- token).
# Imported in FileIO.
# Source: https://github.com/wehos/DeepLink


# ------- IMPORTS -----------
import re
import gzip


# ------- CLASS  ------------
class DeepBankLoader:
    punctuation_list = [",", ".", "\"", "'", ":", "-", "$", "{", "}", ")", "(", "-NONE-"]

    def set_src(src):
        DeepBankLoader.wsj = src

    # Convert token location tags in deepbank resource to semlink
    # Return True when success, else False
    def convert(sentence):
        starts = {}
        if (sentence["doc"] + sentence["sent"]) in DeepBankLoader.wsj.keys():
            wsj = DeepBankLoader.wsj[sentence["doc"] + sentence["sent"]]
            ends = {}
            ender = 0
            src = sentence['src']

            for tag in range(len(wsj)):
                token = wsj[tag]
                token[1] = token[1].replace(r"\/", r"/")
                if token[0] != "-NONE-":
                    if token[1] == "...":
                        token[1] = ". . ."
                    starter = src.find(token[1], ender)

                    # detect missing word
                    if starter == -1:
                        print("Error: Token Missing in sent." + sentence["doc"] + sentence["sent"])
                        # print("searching token:", tag, token[1], ";  missing after:", ender)
                        return False

                    # detect skip word
                    if starter - ender > 1:
                        print("Error: Token Skipping in sent." + sentence["doc"] + sentence["sent"])
                        # print(sentence["src"])
                        # print(tag, token[1], starter, ender)
                        return False

                    ender = starter + len(token[1])
                    starts[str(starter)] = tag
                    ends[str(ender)] = tag

            for node in sentence["nodes"]:
                try:
                    node[2] = starts[node[2]]
                    node[3] = ends[node[3]]

                    while wsj[node[3]][0] in DeepBankLoader.punctuation_list and node[2] < node[3]:
                        node[3] -= 1

                    while wsj[node[2]][0] in DeepBankLoader.punctuation_list and node[2] < node[3]:
                        node[2] += 1

                    node[3] += 1  # End Pos should add one for sliding

                except Exception as arg:
                    print("Error: Deepbank Word-Seg Mistake in sent." + sentence["doc"] + sentence["sent"],
                          "at token." + arg.args[0])
                    # print(sentence["src"])
                    # print("At the node: ", node)
                    return False

            return True

    def load(path):
        sentence_set = {}
        with gzip.open(path, 'r') as pf:
            sentence = {}
            nodes = []
            string = ""
            flag = False
            for line in pf:
                line = line.decode('utf-8')
                if line[0] == "}":
                    string = "{" + string + "\n}"
                    sentence["string"] = string
                    sentence["nodes"] = nodes
                    break

                matcher = re.match(r"\[\d*\] \(\d* of \d*\) \{\d\} `(.*)'", line)
                if matcher is not None:
                    sentence["src"] = matcher.groups()[0]

                    # special rules
                    if sentence["src"][-4:] == "U.S.":
                        sentence["src"] += "."
                    if sentence["src"][-5:] == 'U.S."':
                        sentence["src"] = sentence["src"][:-1] + '."'

                if flag:
                    string = string + "\n" + re.match(r"(.*):(.*)<(\d*):(\d*)>(.*)", line).group()
                    node = list(re.search(r"(.*):(.*)<(\d*):(\d*)>(.*)", line.strip()).groups())
                    nodes.append(node)

                matcher = re.search(r"^{", line)
                if matcher:
                    string = line[1:-2] + ":" + string
                    sentence["head"] = line[1:-2]
                    flag = True

            matcher = re.search(r"/2(\d{4})(\d{3}).gz", path).groups()
            sentence["doc"] = matcher[0]
            sentence["sent"] = matcher[1]

            if DeepBankLoader.convert(sentence):
                sentence_set[matcher[0] + matcher[1]] = sentence
        return sentence_set
