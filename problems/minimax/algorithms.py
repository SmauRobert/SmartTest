import random

class Node:
    def __init__(self, name, children=None, value=None):
        self.name = name
        self.children = children if children is not None else []
        self.value = value
        
def evaluate(node):
    return node.value

def is_terminal(node):
    return node.value is not None

def get_children(node):
    return node.children

def alpha_beta_pruning(node, depth, alpha, beta, maximizing_player, visited):
    if depth == 0 or is_terminal(node):
        visited.append(node.value)
        return evaluate(node), visited
    
    if maximizing_player:
        max_eval = float('-inf')
        for child in get_children(node):
            eval, visited = alpha_beta_pruning(child, depth-1, alpha, beta, False, visited)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cut-off
        return max_eval, visited
    else:
        min_eval = float('inf')
        for child in get_children(node):
            eval, visited = alpha_beta_pruning(child, depth-1, alpha, beta, True, visited)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cut-off
        return min_eval, visited

def generate_tree(max_depth=4, balanced=False):
    """
    Generate a random tree with depth between 3-max_depth levels.
    Non-leaf nodes have 2-4 children.
    Only leaf nodes have values.
    """
    node_counter = [0]
    target_depth = random.randint(3, max_depth)
    
    def build_node(current_depth):
        node_counter[0] += 1
        node_name = f"Node_{node_counter[0]}"
        
        terminal = random.randint(0, 1) and current_depth >= 3
        if current_depth == target_depth or (balanced == False and terminal):
            return Node(node_name, value=random.randint(1, 20))
        if current_depth<target_depth - 1:
            num_children = random.randint(2, 3)
        else:
            num_children = random.randint(2, 4)
        children = [build_node(current_depth + 1) for _ in range(num_children)]
        return Node(node_name, children=children)
    
    return build_node(1),target_depth

def tree_to_dict(node):
    if is_terminal(node):
        return {node.name.lower() : node.value}
    return {node.name.lower() : [tree_to_dict(child) for child in get_children(node)]}

def tree_to_list(node):
    if is_terminal(node):
        return node.value
    return [tree_to_list(child) for child in get_children(node)]
