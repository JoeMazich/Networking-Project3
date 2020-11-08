from simulator.node import Node
import json, math

class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

        self.DV = DistanceVector(id=str(id))
        self.last_updated = self.get_time()

        self.neighbors_DV = {}

        self.debug = False

    def __str__(self):
        return 'DistanceVector node: %s\nDV: %s\n' % (self.id, self.DV)

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        neighbor = str(neighbor)
        print('Updating Link')
        print(self.DV)

        if latency == -1 and neighbor in self.neighbors:
            self.neighbors.remove(neighbor)
            self.DV.delete(neighbor)
            del self.neighbors_DV[neighbor]
        elif latency == -1 and neighbor not in self.neighbors:
            pass

        elif neighbor not in self.neighbors:
            # if we dont know the neighbor as a neighbor
            self.neighbors.append(neighbor)
            # but we do know of them
            if neighbor in self.DV.table:
                # see if the updated path to them is better
                if latency < self.DV.cost(neighbor):
                    # if it is update it, ptheriwse dont
                    self.DV.add(neighbor, latency, [neighbor])
            else:
                # but if we dont even know them at all add them as a new node
                self.DV.add(neighbor, latency, [neighbor])
        # if we know of this neighbor as being a neighbor
        # and the connection we have to them is direct
        elif self.get_next_hop(neighbor) == int(neighbor):
            # update the cost of this connection
            self.DV.update_cost(neighbor, latency)
        # if we know of this neighbor as being a neighbor
        # but we dont have a direct connection to them
        # check to see if this new connection beats the old
        elif latency < self.DV.cost(neighbor):
            # if it does, update it to the new
            self.DV.add(neighbor, latency, [neighbor])

        for node in self.DV.table:
            min_cost = self.DV.cost(node)
            min_hops = self.DV.hops(node)

            for neighbor_id, neighbor_DV in self.neighbors_DV.items():
                if node in neighbor_DV.table:
                    loop = str(self.id) in neighbor_DV.hops(node)
                else:
                    loop = True
                if not loop:
                    new_cost = self.DV.cost(str(neighbor_id)) + neighbor_DV.cost(node)
                    if new_cost < min_cost:
                        updated = True
                        min_cost = new_cost
                        min_hops = self.DV.hops(neighbor_id) + neighbor_DV.hops(node)
            self.DV.add(node, min_cost, min_hops)

        print(self.DV)
        print()
        # Send the messages to neighbors
        message = '%s~%s' % (self.id, self.DV)
        self.send_to_neighbors(message)


    # Fill in this function
    def process_incoming_routing_message(self, m):

        recieved_from, their_DV = m.split('~')
        their_DV = DistanceVector(dict=json.loads(their_DV))
        self.neighbors_DV[recieved_from] = their_DV

        updated = False

        if self.id == 9:
            print(self.id, ' ', self.DV)
            print(' ', m)

        for node in their_DV.table:

            if node not in self.DV.table:
                updated = True
                hops = [recieved_from] + their_DV.hops(node)
                cost = self.DV.cost(recieved_from) + their_DV.cost(node)
                self.DV.add(node, cost, hops)
            elif recieved_from in self.DV.hops(node):
                old_cost = self.DV.cost(node)
                new_cost = their_DV.cost(node) + self.DV.cost(recieved_from)
                if old_cost != new_cost:
                    updated = True
                    self.DV.update_this_cost(node, new_cost)



        if self.id == 9:
            print(self.id, ' ', self.DV)

        for node in self.DV.table:

            '''if self.id == 1 and node == '17':
                print('HERE', self.DV)'''

            min_cost = self.DV.cost(node)
            min_hops = self.DV.hops(node)

            for neighbor_id, neighbor_DV in self.neighbors_DV.items():
                if node in neighbor_DV.table:
                    loop = str(self.id) in neighbor_DV.hops(node)
                else:
                    loop = True
                if not loop:
                    new_cost = self.DV.cost(str(neighbor_id)) + neighbor_DV.cost(node)

                    '''if self.id == 9 and node == '17':
                        print('HIT1', self.DV.cost(str(neighbor_id)), neighbor_DV.cost(node))
                        print('HIT2', neighbor_id, neighbor_DV)'''

                    if new_cost < min_cost:
                        updated = True
                        min_cost = new_cost
                        min_hops = self.DV.hops(neighbor_id) + neighbor_DV.hops(node)
                        if self.id == 9 and node == '17':
                            print(neighbor_id, new_cost, min_hops, 'HIT')

            self.DV.add(node, min_cost, min_hops)



            if self.id == 9 and node == '17':
                '''print('^ min for ', node)
                print(self.id, ' ', self.DV)
                for id, DV in self.neighbors_DV.items():
                    if id == '17':
                        print('  ', id, DV)'''
                print(self.id, ' ', self.DV)
                print()

        if updated:
            message = '%s~%s' % (self.id, self.DV)
            self.send_to_neighbors(message)

    def get_next_hop(self, destination):
        try:
            hops = self.DV.hops(str(destination))
            cost = self.DV.cost(str(destination))
            return int(hops[0])
        except:
            return -1


class DistanceVector:
    def __init__(self, id=None, dict={}):
        self.table = {}

        if id:
            self.table[id] = (float(0), [None])

        for id, cost_hops in dict.items():
            self.add(id, float(cost_hops[0]), cost_hops[1])

    def __repr__(self):
        return json.dumps(self.table)

    def __len__(self):
        return int(len(self.table))

    def update_cost(self, id: str, cost):
        old_neighbor_cost = self.cost(id)

        for other_id in self.table:
            if id in self.hops(other_id):
                old_cost, hops = self.table[other_id]
                self.table[other_id] = (old_cost - old_neighbor_cost + cost, hops)

    def delete(self, id):
        for other_id in self.table:
            if id in self.hops(other_id):
                old_cost, hops = self.table[other_id]
                self.table[other_id] = (math.inf, [-1])

    def update_this_cost(self, id, cost):
        old_cost, hops = self.table[id]
        self.table[id] = (float(cost), hops)

    def add(self, id, cost, hops):
        self.table[id] = (float(cost), hops)

    def cost(self, id):
        return float(self.table[id][0])

    def hops(self, id):
        return self.table[id][1]
