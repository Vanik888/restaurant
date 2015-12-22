from astar_grid import AStarGrid, AStarGridNode
from itertools import product


def make_graph(width, height):
    nodes = [[AStarGridNode(x, y) for y in range(height)] for x in range(width)]
    graph = {}
    for x, y in product(range(width), range(height)):
        node = nodes[x][y]
        graph[node] = []
        for i, j in product([-1, 0, 1], [-1, 0, 1]):
            if not (0 <= x + i < width):
                continue
            if not (0 <= y + j < height):
                continue
            graph[nodes[x][y]].append(nodes[x+i][y+j])
    return graph, nodes

graph, nodes = make_graph(8, 8)
paths = AStarGrid(graph)
start, end = nodes[1][1], nodes[5][7]
path = paths.search(start, end)
if path is None:
    print "No path found"
else:
    print "Path found:", path
    for node in path:
        print (node.x, node.y)
