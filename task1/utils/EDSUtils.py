# ------- DESCRIPTION -------
# Util for annotated EDS graphs.
# Imported in FileIO.


# ------- IMPORTS -----------
import re
from delphin.codecs import eds


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

# ------- METHODS -----------
def convert_to_eds(deepbank):
    graphs = {}
    for key in deepbank.keys():
        entry = deepbank.get(key)
        try:
            graphs[entry["doc"] + entry["sent"]] = eds.loads(entry["string"])[0]
        except eds.EDSSyntaxError:
            # Deal with numbers with commas, for e.g. 238,000.
            for match in re.findall(r"_[1-9]*,[1-9]*", entry["string"]):
                entry["string"] = entry["string"].replace(match, re.sub(',', '', match))
                try:
                    graphs[entry["doc"] + entry["sent"]] = eds.loads(entry["string"])[0]
                except eds.EDSSyntaxError:
                    print("Error: EDS Parsing Syntax Error in sent." + entry["doc"] + entry["sent"])
    return graphs


def annotate_eds(graphs, semlink):
    incomplete = []
    complete = []
    for key in graphs.keys():

        # Check if corresponding SemLink entry exists, if not skip.
        if key in semlink.keys():
            is_incomplete = False
            sml = semlink.get(key)
            graph = graphs.get(key)

            for node in graph.nodes:
                # Check if predicate is verb, and if it is match it to SemLink verb.
                if re.match(r"_[a-z]*_v_[1-9]", node.predicate):
                    verb = node.predicate.split('_')[1]
                    verb = verb + "-v"

                    for fn_entry in sml:
                        if fn_entry['verb'] == verb:
                            # [a] Add frame to predicate. Currently adding IN and NF.
                            # Avoid duplicates.
                            if fn_entry["frame"] not in ["IN", "NF"]:
                                if "-fn." not in node.predicate:
                                    node.predicate = node.predicate + "-fn." + fn_entry["frame"]
                            else:
                                is_incomplete = True

                            # [b] Add argument labels to eds arguments. Currently adding all after (=).
                            # Extract argument number and add +1 to match EDS graph
                            for argument in fn_entry["args"]:
                                if 'rel' not in argument:
                                    argument_number = ''
                                    argument_label = ''
                                    if '=' in argument:
                                        split = argument.split('=')
                                        roles = split[1]
                                        if ';' in roles:
                                            argument_number = split[0].split('-')[1]
                                            # The first label is the VerbNet role, the second is the FrameNet role.
                                            argument_label = split[1].split(';')[1]
                                    elif '-' in argument:
                                        split = argument.split('-')
                                        # For e.g. 11:1-ARGM-PRD
                                        if len(split) > 2:
                                            argument_number = split[1]
                                            argument_label = split[2]
                                        # For e.g. 12:2-ARG0
                                        else:
                                            argument_number = split[1]
                                            argument_label = ''
                                    else:
                                        print(argument)

                                    # Check that the argument is in the EDS graph and that the label is nonempty.
                                    if argument_number in node.edges.keys():
                                        if argument_label != '':
                                            node.edges[argument_number + "-fn." + argument_label] = node.edges[
                                                argument_number]
                                            del node.edges[argument_number]
                                        # is_incomplete = True
            if is_incomplete:
                incomplete.append(key)
            else:
                complete.append(key)

    return graphs, set(complete), set(incomplete)
