from simulator.node import Node
import json

class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.full_graph = [] #every edge in the graph represented as a list of tuples in the form (node1, node2, cost)

    # Return a string
    def __str__(self):
        return "A Link-state Node: " + str(self.id) + "\n"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        tuple = (self.id, neighbor, latency, self.get_time())
        self.neighbors.append(neighbor) #Might not need this
        for i, edge in enumerate(self.full_graph):
            if (edge[0] == tuple[0] and edge[1] == tuple[1]) or (edge[0] == tuple[1] and edge[1] == tuple[0]):
                del self.full_graph[i]
                break

        #print("Link Has Been Updated Tuple: ", tuple)
        self.full_graph.append(tuple)
        #print("Link Has Been Updated Graph: ", self.full_graph)
        message = json.dumps(self.full_graph)
        self.send_to_neighbors(message)

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # parse out the recieved updates
        #print("M: ", m)
        neighbor_graph = json.loads(m)
        anything_different = False
        for edge in neighbor_graph:
            already_in_graph = False
            for i, eddge in enumerate(self.full_graph):
                if (edge[0] == eddge[0] and edge[1] == eddge[1]) or (edge[0] == eddge[1] and edge[1] == eddge[0]):
                    already_in_graph = True
                    if edge[3] > eddge[3]:
                        anything_different = True
                        del self.full_graph[i]
                        self.full_graph.append(edge)
                        break
                    break
            if not already_in_graph:
                anything_different = True
                self.full_graph.append(edge)
        #print("Process Incoming Routing Messages Graph: ", self.full_graph)
        if anything_different:
            self.send_to_neighbors(m)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        #print(self.full_graph)
        #print(self.neighbors)
        #print("Self: ", self)
        #print("Destination: ", destination)
        if self.id == destination:
            return self.id #Not actually sure what to do in this case
        distances = {self.id: 0}
        previous = {self.id: -1}
        known_nodes = [self.id]
        current = self.id

        while destination not in known_nodes:
            #print("current: ", current)
            #print("distances: ", distances)
            #print("known nodes: ", known_nodes)
            for neighbor in get_neighbors(current, self.full_graph):
                if neighbor not in known_nodes: #prevents loops
                    #print("neighbor1: ", neighbor)
                    distance = distances[current] + get_latency(current, neighbor, self.full_graph)
                    #print("distance: ", distance)
                    #if neighbor in distances:
                        #print("previous_distance: ", distances[neighbor])
                    if neighbor not in distances or distance < distances[neighbor]:
                        #print("neighbor2: ", neighbor)
                        distances[neighbor] = distance
                        previous[neighbor] = current
            min_node = -1
            min_dist = float('inf')
            for found_node in distances:
                if found_node not in known_nodes and distances[found_node] < min_dist:
                    min_node = found_node
                    min_dist = distances[found_node]
            if min_node == -1: #no path to the destination exists
                break
            known_nodes.append(min_node)
            current = min_node

        if destination in known_nodes:
            current = destination
            while previous[current] != self.id:
                current = previous[current]
            return current
        return -1

def get_neighbors(node, graph):
    neighbors = []
    for edge in graph:
        if node == edge[0]:
            neighbors.append(edge[1])
        elif node == edge[1]:
            neighbors.append(edge[0])
    return neighbors

def get_latency(node1, node2, graph):
    for edge in graph:
        if edge[0] == node1 and edge[1] == node2:
            return edge[2]
        if edge[0] == node2 and edge[1] == node1:
            return edge[2]
    raise ValueError("Should never see this")
