from BPlus import BPTree, BPnode, BPleaf
from nltk.tree import Tree
from nltk.draw.tree import TreeView

class BetterTreeView(TreeView):
    def _init_menubar(self): pass

def draw_a_tree(tree):
    if isinstance(tree, BPTree):
        BP_tree_to_nltk_tree(tree.root).draw()

def get_tree_view(tree):
    if isinstance(tree, BPTree):
        return BetterTreeView(BP_tree_to_nltk_tree(tree.root))

def BP_tree_to_nltk_tree(tree):
    root = Tree(str(tree.keys), children = [])
    if isinstance(tree, BPnode):
        for child in tree.children:
            root.append(BP_tree_to_nltk_tree(child))

    return root
