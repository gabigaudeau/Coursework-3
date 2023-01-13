# This Procedure is used for extracting tokens from semlink file (semlink 1.2.2 style)
# The file format is like this:
# (document_id) (sentence number) (token number) (standard) (verb-v) (VerbNet class)
# (FrameNet Frame) (PB grouping) (SI grouping) (tense/aspect/mood info)
# (ArgPointer)-ARG X=(VN Role);(FN Role/Optional Extra Fn Roles)

import re
from task1.loaders.AddZeros import add_zeros

sem_parser = ["doc", "sent", "token", "stand", "verb", "verbnet", "frame", "PB", "SI", "TAM", "args"]


class SemLinkLoader:
    missing_frames = 0
    total_verb = 0
    missing_frame_sentences = 0
    token_pattern = re.compile(r"\([^()]*\)")

    def load(path):
        sentence_set = {}
        with open(path, "r") as file:
            doc = re.search(r"\_(.*)\.", path).groups()[0]
            sent = "-1"
            verbs = None
            miss = None
            for line in file:
                SemLinkLoader.total_verb += 1
                args = line.strip().split(" ")
                sentence = {"doc": doc}
                for index in range(10):
                    sentence[sem_parser[index]] = args[index]
                args = args[10:]
                sentence["args"] = args
                if sent == "-1":
                    sent = sentence["sent"]
                    verbs = []
                    miss = False

                if sentence["frame"] in ["IN", "NF"]:
                    SemLinkLoader.missing_frames += 1
                    miss = True

                if sent != sentence["sent"]:
                    if miss:
                        SemLinkLoader.missing_frame_sentences += 1
                    sentence_set[doc + add_zeros(sent)] = verbs
                    sent = sentence["sent"]
                    verbs.append(sentence)
                    miss = False
                else:
                    verbs.append(sentence)

            sentence_set[doc + add_zeros(sent)] = verbs
            if miss:
                SemLinkLoader.missing_frame_sentences += 1

        return sentence_set
