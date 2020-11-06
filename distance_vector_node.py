from simulator.node import Node


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        self.routing_table = RoutingTable(id)

    def __str__(self):
        return 'LS node: %s\nRT: %s\n' % (self.id, self.RT)

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        try:
            hops = self.self.routing_table.hops[destination]
        except:
            return -1
        else:
            return hops[0]

class RoutingTable:

    def __init__(self, id: int):
        self.cost = {id: 0}
        self.hops = {id: None}

    def __repr__(self):
        return '%s~%s' % (json.dumps(self.cost), json.dumps(self.hops))

    def update(self, id: int, total_latency: int, path: list):
        self.hops[id] = path
        self.cost[id] = total_latency

    def delete(self, id: int):
        del self.hops[id]
        del self.cost[id]
