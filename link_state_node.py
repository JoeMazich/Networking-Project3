from simulator.node import Node


class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)

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

        try:
            hops = self.hops[destination]
        except:
            hops = [-1]

        return hops[0]
