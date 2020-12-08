from app.algorithms.generator import generate_triangle_field
from app.algorithms.structures import Node, Segment
from app.numberlink import TriangleLink, TriangleField
import itertools


def get_right_path(edge, paths):
    for path in paths:
        if any(v in path for v in edge):
            return path
    return None


def make_field_from_solution(field: TriangleLink, solution):
    result = TriangleField(generate_triangle_field(field.size))

    for pair in field.get_targets()['pairs']:
        start, end = tuple(pair)
        number = field[start]
        while start != end:
            for edge in solution:
                if start in edge:
                    result[start] = number
                    start = get_opposite(start, edge)
        result[end] = number
    return result._field


def make_solutions(root, path=None):
    path = path or []
    if root is Node.link_one:
        yield path
    elif root is not Node.link_zero:
        yield from itertools.chain(
                make_solutions(root.zero_child, path),
                make_solutions(root.one_child, path + [root.edge])
        )


def get_path(path, node):
    return path if node.name == 0 else path + [node.edge]


def solve(instance: TriangleLink):
    graph = instance.make_graph()
    targets = instance.get_targets()
    vertices = Segment(graph.vertices())
    edges = graph.edges()

    root = Node(edges[0], {v: v for v in vertices.active}, 1)

    def get_node(node_edge, mate, arc):
        return Node(node_edge, mate, arc) if node_edge else Node.link_one

    nodes = [root]
    while edges:
        edge = edges.pop(0)
        next_edge = edges[0] if edges else None
        update_vertices(vertices, edge, edges)
        new_nodes = []
        for node in nodes:
            children = []
            if is_zero_incompatible(node, targets, vertices):
                children.append(Node.link_zero)
            else:
                new_mate = update_domain(node.neighbor, vertices.active)
                children.append(get_node(next_edge, new_mate, 0))
            if is_one_incompatible(node, targets, vertices):
                children.append(Node.link_zero)
            else:
                new_mate = update_domain(update_mate(node), vertices.active)
                children.append(get_node(next_edge, new_mate, 1))
            new_nodes.extend(n for n in children if not is_terminal(n))
            node.add_children(*children)
        nodes = new_nodes
    return make_solutions(root)


def is_zero_incompatible(node, targets, vertices):
    filtered = (v for v in node.edge if v not in vertices.active)

    def condition(v):
        return (node.neighbor[v] == v
                or v not in targets["vertices"] and node.neighbor[v] not in [0, v])

    return any(condition(v) for v in filtered)


def is_one_incompatible(node, targets, vertices):
    union = targets["vertices"] | vertices.thrown
    pair = {node.neighbor[v] for v in node.edge}

    def condition(v):
        return (v in targets["vertices"] and node.neighbor[v] != v
                or node.neighbor[v] in [0, get_opposite(v, node.edge)])

    return (pair <= union and pair not in targets["pairs"]
            or any(condition(v) for v in node.edge))


def is_terminal(node):
    return node in [Node.link_zero, Node.link_one]


def is_not_terminal(node):
    return not is_terminal(node)


def update_domain(mate, domain):
    return {v: mate[v] for v in domain}


def update_mate(parent):
    mate = {}

    for vertex in parent.neighbor:
        if vertex in parent.edge and parent.neighbor[vertex] != vertex:
            mate[vertex] = 0
        elif parent.neighbor[vertex] in parent.edge:
            opposite = get_opposite(parent.neighbor[vertex], parent.edge)
            mate[vertex] = parent.neighbor[opposite]
        else:
            mate[vertex] = parent.neighbor[vertex]

    return mate


def update_vertices(vertices, edge, edges):
    vertices_in_edges = set(itertools.chain(*edges))
    for vertex in (v for v in edge if v not in vertices_in_edges):
        vertices.throw(vertex)


def get_opposite(x, pair):
    return pair[0] if x == pair[1] else pair[1] if x == pair[0] else None