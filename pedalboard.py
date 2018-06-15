from collections import OrderedDict


class Plugin:
    """
    Effects plugin/stompbox. Loads a LV2 plugin as per URI but could
    support other plugin frameworks as well.
    """
    def __init__(self, uri, i):
        self._uri = uri
        self._index = i

    def __str__(self):
        return '[{}] "{}"'.format(self._index, self._uri)

    def get_parameter(self, symbol):
        return "Not implemented"

    def set_parameter(self, symbol, value):
        return "Not implemented"

    def set_bypass(self, enable):
        return "bypass set: %d" % enable


class Graph:
    """
    Organises and represents the pedal board as a directional graph.
    The nodes are effects plugins ("stompboxes") and the edges are the
    arbitrary connections between them. The first node in the chain won't
    have a connection to it: this implies connection from system_capture, and
    the last node won't have any outgoing connections: this implies connection
    to system_playback.

    >>> g = Graph(['a', 'b', 'c'])
    >>> g.add_edges('a', [1, 2])
    >>> g.add_edges('b', [2])
    >>> g.add_edges('c', [3])
    >>> g.get_outgoing_edges('a')
    [1, 2]
    >>> g.get_incoming_edges('c')
    [0, 1]
    >>> g.get_index('a')
    0
    >>> g.get_index('c')
    2
    """
    def __init__(self, nodes):
        self._graph = OrderedDict.fromkeys(nodes, value=[])

    def draw(self):
        lines = []
        cur_node_index = 0

        # Start at node 0
        cur_node = list(self._graph.keys())[cur_node_index]
        lines.append(str(cur_node))

        cur_edges = self.get_outgoing_edges(cur_node)

        while cur_edges:
            # Draw vertical lines according to number of edges
            lines.append('    '.join(' | ' * len(cur_edges)))

            # Draw next node
            lines.append(' '.join(str(self.get_node_from_index(i)) for i in cur_edges))

            cur_node_index +=1
            cur_node = list(self._graph.keys())[cur_node_index]
            cur_edges = self.get_outgoing_edges(cur_node)

        return '\n'.join(lines)

    def __str__(self):
        return '\n'.join(['{} -> {}'.format(str(n), str(e)) for n, e in self._graph.items()])

    @property
    def nodes(self):
        return self._graph.keys()

    def add_edges(self, node, edges):
        self._graph[node] = edges

    def add_edges_to_index(self, node_index, edges):
        self._graph[self.get_node_from_index(node_index)] = edges

    def get_outgoing_edges(self, node):
        return self._graph[node]

    def get_incoming_edges(self, node):
        r = []
        for n, edges in self._graph.items():
            for e in edges:
                if e == self.get_index(node):
                    r.append(self.get_index(n))
        return sorted(set(r))

    def get_index(self, node):
        return list(self._graph.keys()).index(node)

    def get_node_from_index(self, node_index):
        for i, node in enumerate(self._graph.keys()):
            if i == node_index:
                return node
        return None
