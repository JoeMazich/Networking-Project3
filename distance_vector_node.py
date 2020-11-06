from simulator.node import Node
import json, math

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        self.DV = DistanceVector(id=str(id))

    def __str__(self):
        return 'LS node: %s\nRT: %s\n' % (self.id, self.routing_table)

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        neighbor = str(neighbor)

        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
            self.DV.delete(neighbor)
        elif latency == -1 and neighbor not in self.neighbors:
            pass
        elif neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            self.DV.add(neighbor, latency, [neighbor])
        else:
            self.DV.update(neighbor, latency)

        # Send the messages to neighbors
        message = '%s~%s' % (self.id, self.DV)
        self.send_to_neighbors(message)
        print(self.DV)

    # Fill in this function
    def process_incoming_routing_message(self, m):
        recieved_from, their_DV = m.split('~')
        their_DV = DistanceVector(dict=json.loads(their_DV))

        updated_flag = False

        for id in their_DV.table:
            if id not in self.DV.table:
                updated_flag = True
                hops = [recieved_from] + their_DV.hops(id)
                cost = self.DV.cost(recieved_from) + their_DV.cost(id)
                self.DV.add(id, cost, hops)
            # Figure out costs 

        if updated_flag:
            message = '%s~%s' % (self.id, self.DV)
            self.send_to_neighbors(message)

        print(self.DV)

    def get_next_hop(self, destination):
        try:
            hops = self.DV.hops(str(destination))
        except:
            return -1
        else:
            return int(hops[0])

class DistanceVector:
    def __init__(self, id: str=None, dict={}):
        self.table = {}

        if id:
            self.table[id] = (0, [None])

        for id, cost_hops in dict.items():
            self.add(id, int(cost_hops[0]), cost_hops[1])

    def __repr__(self):
        return json.dumps(self.table)

    def delete(self, id: str):

        for other_id in self.table:
            if id in self.hops(other_id):
                old_cost, hops = self.table[other_id]
                self.table[other_id] = (math.inf, hops[0:hops.index(id)] + [-1])

        del self.table[id]

    def update(self, id: str, cost: int):
        old_neighbor_cost = self.cost(id)

        for other_id in self.table:
            if id in self.hops(other_id):
                old_cost, hops = self.table[other_id]
                self.table[other_id] = (old_cost - old_neighbor_cost + cost, hops)

    def add(self, id: str, cost: int, hops: list):
        self.table[id] = (cost, hops)

    def cost(self, id: str) -> int:
        return self.table[id][0]

    def hops(self, id: str) -> list:
        return self.table[id][1]

    def get_info(self, id: str) -> tuple:
        return self.table[id]
