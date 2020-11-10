from simulator.node import Node
import json, math

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        self.DV = DistanceVector(id=str(id))

        self.neighbors_DVs = {}
        self.directly_to = {}

        self.my_last_updated = 0
        self.their_last_updated = {}
        # send it with the amount of times it has been updated and only care about  those times after it

    def __str__(self):
        return '\nDistance-vector node: %s\nDV: %s\n' % (self.id, self.DV)

    def link_has_been_updated(self, neighbor, latency):
        passing = False

        if latency != -1 and neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
            self.directly_to[neighbor] = latency
            self.neighbors_DVs[neighbor] = DistanceVector(dict={str(neighbor): (float(0), [None])})
            self.their_last_updated[neighbor] = 0
        elif latency != -1 and neighbor in self.neighbors:
            old_latency = self.directly_to[neighbor]
            self.directly_to[neighbor] = latency
        elif latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
            del self.directly_to[neighbor]
            del self.neighbors_DVs[neighbor]
            del self.their_last_updated[neighbor]
        else:
            passing = True

        if not passing:

            old_DV = DistanceVector(dict=self.DV.table)
            self.DV.dump(str(self.id))

            known_nodes = [self.id]

            for id in self.neighbors:
                for node in self.neighbors_DVs[id].table:
                    if node not in known_nodes:
                        known_nodes.append(node)

            for known_node in known_nodes:
                known_node = str(known_node)

                if int(known_node) == self.id:
                    min_cost, min_hops = float(0), [None]
                else:
                    min_cost, min_hops = math.inf, [-1]

                for neighbor_id, neighbor_DV in self.neighbors_DVs.items():
                    if known_node in neighbor_DV.table and self.id not in neighbor_DV.hops(known_node):
                        new_cost = self.directly_to[neighbor_id] + neighbor_DV.cost(known_node)

                        if new_cost <= min_cost:
                            min_cost = new_cost
                            min_hops = [neighbor_id] + neighbor_DV.hops(known_node)

                self.DV.update(known_node, min_cost, min_hops)

            if old_DV.table != self.DV.table:
                self.my_last_updated += 1
                message = '%s~%s~%s' % (self.my_last_updated, self.id, self.DV)
                self.send_to_neighbors(message)

    def process_incoming_routing_message(self, m):

        last_updated, recieved_from, their_DV = m.split('~')
        recieved_from = int(recieved_from)
        last_updated = int(last_updated)


        if recieved_from in self.their_last_updated and last_updated > self.their_last_updated[recieved_from]:
            self.neighbors_DVs[recieved_from] = DistanceVector(dict=json.loads(their_DV))
            self.their_last_updated[recieved_from] = last_updated

            old_DV = DistanceVector(dict=self.DV.table)
            self.DV.dump(str(self.id))

            known_nodes = [self.id]

            for id in self.neighbors:
                for node in self.neighbors_DVs[id].table:
                    if node not in known_nodes:
                        known_nodes.append(node)

            for known_node in known_nodes:
                known_node = str(known_node)

                if int(known_node) == self.id:
                    min_cost, min_hops = float(0), [None]
                else:
                    min_cost, min_hops = math.inf, [-1]

                    for neighbor_id, neighbor_DV in self.neighbors_DVs.items():
                        if known_node in neighbor_DV.table and neighbor_id in self.directly_to and self.id not in neighbor_DV.hops(known_node):
                            new_cost = self.directly_to[neighbor_id] + neighbor_DV.cost(known_node)

                            if new_cost < min_cost:
                                min_cost = new_cost
                                min_hops = [neighbor_id] + neighbor_DV.hops(known_node)

                self.DV.update(known_node, min_cost, min_hops)

            if old_DV.table != self.DV.table:
                self.my_last_updated += 1
                message = '%s~%s~%s' % (self.my_last_updated, self.id, self.DV)
                self.send_to_neighbors(message)

    def get_next_hop(self, destination):
        try:
            hops = self.DV.hops(str(destination))
            return int(hops[0])
        except:
            return -1


class DistanceVector:
    def __init__(self, id=None, dict={}):
        self.table = {}

        if id:
            self.table[id] = (float(0), [None])

        for id, cost_hops in dict.items():
            self.update(id, float(cost_hops[0]), cost_hops[1])

    def __repr__(self):
        return json.dumps(self.table)

    def dump(self, id):
        self.table = {}
        self.table[id] = (float(0), [None])

    def update(self, id, cost, hops):
        self.table[id] = (float(cost), hops)

    def cost(self, id):
        return float(self.table[id][0])

    def hops(self, id):
        return self.table[id][1]

    def info(self, id):
        return float(self.table[id][0]), self.table[id][1]
