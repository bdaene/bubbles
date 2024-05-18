from itertools import count
from random import Random
from time import sleep, perf_counter
from typing import Iterable

from bubbles.models import Bubble


class Simulation:

    def __init__(self, bubbles: Iterable[Bubble], interval=0.01):
        self.interval = interval
        self.random = Random()
        self.running = False

        bubbles = tuple(bubbles)
        self.border = bubbles[0]
        assert self.border.area() < 0.

        self.bubbles = {id(bubble): (bubble, False) for bubble in bubbles}
        self.bubbles[id(self.border)] = (self.border, True)

        arcs = {(id(arc.start), id(arc.end), arc.angle): (arc, bubble, border)
                for bubble, border in self.bubbles.values() for arc in bubble.arcs}

        self.arcs = {}
        for arc, bubble, border in arcs.values():
            reverse_arc, *_ = arcs[(id(arc.end), id(arc.start), -arc.angle)]
            self.arcs[id(arc)] = (arc, reverse_arc, bubble, border, reverse_arc)

        nodes = {}
        for arc, _, border in arcs.values():
            node = arc.start
            nodes.setdefault(id(node), (node, []))[1].append(arc)
        self.nodes = {node_id: (node, tuple(node_arcs)) for node_id, (node, node_arcs) in nodes.items()}
        for node, node_arcs in self.nodes.values():
            assert len(node_arcs) == 3

    def get_arcs(self):
        return [arc for arc, *_ in self.arcs.values()]

    def update(self, frame: int, delta_time: float):
        self.update_arcs(frame, delta_time)
        self.update_nodes(frame, delta_time)

    def update_arcs(self, frame: int, delta_time: float):
        ...

    def update_nodes(self, frame: int, delta_time: float):
        ...

    def run(self):
        self.running = True
        timestamp = perf_counter()
        refresh = 100
        delta_time = 0

        for frame in count(1):
            if not self.running:
                break

            if frame % refresh == 0:
                new_timestamp = perf_counter()
                delta_time = (new_timestamp - timestamp) / refresh
                print(f'UPS: {1 / delta_time:.0f}')
                timestamp = new_timestamp

            self.update(frame, delta_time)
            sleep(self.interval)

    def stop(self):
        self.running = False
