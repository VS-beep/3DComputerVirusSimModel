# network.py
import random

def create_network(num_nodes=150, connection_prob=0.1):
    """
    Create an undirected graph represented as adjacency list:
    Keys = node IDs, values = list of connected nodes.
    """
    network = {i: [] for i in range(num_nodes)}
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < connection_prob:
                network[i].append(j)
                network[j].append(i)
    return network
