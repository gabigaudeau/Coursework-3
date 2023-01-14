# ------- DESCRIPTION -------
# Method to match Penn Treebank and SemLink sentences to DeepBank filenames.
# Add zeros (and plus 1) before a num.
# Imported in PTBLoader and SemLinkLoader.
# Source: https://github.com/wehos/DeepLink


# ------- METHOD ------------
def add_zeros(num):
    s = str(int(num) + 1)
    return "0" * (3 - len(s)) + s
