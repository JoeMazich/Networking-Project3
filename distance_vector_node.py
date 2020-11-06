from simulator.node import Node
import json

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        self.routing_table = RoutingTable(id)

    def __str__(self):
        return 'LS node: %s\nRT: %s\n' % (self.id, self.routing_table)

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
            hops = self.routing_table.hops(destination)
        except:
            return -1
        else:
            return hops[0]

class RoutingTable:
    def __init__(self, id: int):
        self.table = {id: (0, [None])}

    def __repr__(self):
        return '%s~%s' % (json.dumps(self.cost), json.dumps(self.hops))

    def update(self, id: int, cost: int, hops: list):
        self.table[id] = (cost, hops)

    def delete(self, id: int):
        del self.table[id]

    def cost(self, id: int) -> int:
        return self.table[id][0]

    def hops(self, id: int) -> list:
        return self.table[id][1]

    def get_info(self, id: int) -> tuple:
        return self.table[id]
