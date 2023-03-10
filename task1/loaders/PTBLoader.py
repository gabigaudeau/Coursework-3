# ------- DESCRIPTION -------
# Loader used for extracting tokens from Penn TreeBank files (PTB3 style).
# Imported in FileIO.
# Source: https://github.com/wehos/DeepLink


# ------- IMPORTS -----------
from task1.loaders.SpecialCases import special_transform
from task1.loaders.AddZeros import add_zeros
from task1.utils.TreeUtils import Node
import re


# ------- CLASS  ------------
class PTBLoader:
    token_pattern = re.compile(r"[ \(]]")

    def load(path):
        ptb = open(path, "r")
        doc = re.search(r"/wsj_(\d*)", path).groups()[0]
        index = -1
        sentence_set = {}
        stack = []

        for line in ptb:
            if line[0] == "(":
                if index != -1:
                    sentence_set[doc + add_zeros(index)] = sent
                    sentence_set["t" + doc + add_zeros(index)] = tsent
                sent = []
                tsent = []
                index += 1
                ord = 0

            line = line.lstrip()[:-1]
            loc = 0

            while loc < len(line):
                if line[loc] == "(":
                    space = line.find(" ", loc + 1)
                    pos = line[loc + 1:space]
                    stack.append(Node(pos))
                    loc = space + 1
                elif line[loc] == ")":
                    last = stack.pop()
                    if len(stack) > 0:
                        stack[-1].set_child(last)
                        last.set_father(stack[-1])
                    loc += 1
                elif line[loc] == " ":
                    loc += 1
                else:
                    next = line.find(")", loc + 1)
                    token = line[loc:next]
                    stack[-1].set_token(token)
                    stack[-1].set_ord(ord)  # Set order number
                    ord += 1
                    loc = next

                    # special cases
                    pos, token = special_transform(pos, token)

                    sent.append([pos, token])
                    tsent.append(stack[-1])

        sentence_set[doc + add_zeros(index)] = sent
        sentence_set["t" + doc + add_zeros(index)] = tsent
        return sentence_set
