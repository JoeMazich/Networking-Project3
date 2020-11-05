from simulator.node import Node


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.full_graph = [] #every edge in the graph represented as a list of tuples in the form (node1, node2, cost)

        self.hops = {id: None}
        self.costs = {id: 0}

    # Return a string
    def __str__(self):
        return "A Link-state Node: " + str(self.id) + "\n"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link

        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
            del self.hops[neighbor]
            del self.costs[neighbor]

        elif neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            self.hops[neighbor] = [neighbor]
            self.costs[neighbor] = latency

        # self.send_to_neighbors all of the updates recieved


    # Fill in this function
    def process_incoming_routing_message(self, m):
        # parse out the recieved updates
        print(self.id, ' recieved: ', m)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination): 
        if self.id == destination.id:
            return self #Not actually sure what to do in this case
        distances = {self: 0}
        previous = {self: None}
        known_nodes = [self]
        current = self

        while destination not in known_nodes:
            for neighbor in current.neighbors:
                if neighbor not in known_nodes: #prevents loops
                    distance = distances[current] + get_latency(current, neighbor, self.full_graph)
                    if neighbor not in distances or distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current
            min_node = None
            min_dist = float('inf')
            for found_node in distances:
                if found_node not in known_nodes and distances[found_node] < min_dist:
                    min_node = found_node
                    min_dist = distances[found_node]
            if min_node == None: #no path to the destination exists
                break
            known_nodes.append(min_node)
            current = min_node

        if destination in known_nodes:
            current = destination
            while previous[current].id != self.id:
                current = previous[current]
            return current
        return -1


def get_latency(node1, node2, graph):
    for edge in graph:
        if edge[0].id == node1.id and edge[1].id == node2.id:
            return edge[2]
        if edge[0].id == node2.id and edge[1].id == node1.id:
            return edge[2]
    raise ValueError("Should never see this")

