from lark import Tree


def tree_to_string(tree):
    """
    Recursively constructs a list form given lark tree.

    :param tree: given lark tree
    :return: list of components
    """
    if type(tree) == Tree:
        return sum(list(map(tree_to_string, tree.children)), [])
    else:
        return [str(tree)]
