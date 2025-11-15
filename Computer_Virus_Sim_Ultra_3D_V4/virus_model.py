# virus_model.py

import random

class VirusState:
    HEALTHY = 0
    INFECTED = 1
    RECOVERED = 2  # Optional: you can implement recovery/immunity if desired

class Node:
    def __init__(self, id):
        self.id = id
        self.state = VirusState.HEALTHY
        self.strain_id = None  # Track which strain infected this node

class VirusModel:
    def __init__(self, mutation_rate=1.00):
        self.mutation_rate = mutation_rate

    def infect(self, node, source_strain):
        """
        Infect the given node.
        There's a chance the virus mutates into a new strain.
        """
        if node.state == VirusState.HEALTHY:
            if random.random() < self.mutation_rate:
                new_strain = source_strain + 1  # new strain id is +1 from source
                node.strain_id = new_strain
            else:
                node.strain_id = source_strain
            node.state = VirusState.INFECTED
