# ------- DESCRIPTION -------
# Util for Penn TreeBank constituency trees.
# Imported in PTBLoader.
# Source: https://github.com/wehos/DeepLink


# ------- CLASS -------------
class Node:
    def __init__(self, pos):
        self.token = None
        self.pos = pos
        self.span = [99999999, -1]   # The span of tokens the node covers.
        self.father = None
        self.children = []

    def set_father(self, father):
        self.father = father

    def set_child(self, child):
        self.children.append(child)
        self.span = [min(self.span[0], child.span[0]), max(self.span[1], child.span[1])]

    def set_token(self, token):
        self.token = token

    def set_ord(self, ord):
        self.span = [ord, ord + 1]
