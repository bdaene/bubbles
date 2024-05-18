import cmath
import math
from itertools import count
from random import Random
from time import sleep, perf_counter
from typing import Iterable

from bubbles.models import Bubble, Arc, Node


class Simulation:

    def __init__(self, bubbles: Iterable[Bubble], interval=0.01, arc_speed=1., node_speed=1.):
        self.interval = interval
        self.random = Random()
        self.running = False

        self.arc_speed = arc_speed
        self.node_speed = node_speed

        bubbles = tuple(bubbles)
        self.border = bubbles[0]
        assert self.border.area() < 0.

        self.bubbles: dict[int, tuple[bool, Bubble]]
        self.bubbles = {id(bubble): (False, bubble) for bubble in bubbles}
        self.bubbles[id(self.border)] = (True, self.border)
        for border, bubble in self.bubbles.values():
            assert bubble.area() < 0. if border else bubble.area() > 0.

        arcs = {(id(arc.start), id(arc.end), arc.angle): (border, arc, bubble)
                for border, bubble in self.bubbles.values() for arc in bubble.arcs}

        self.arcs: dict[int, tuple[bool, Arc, Bubble]]
        self.reverse_arcs: dict[int, tuple[bool, Arc, Bubble]]
        self.arcs, self.reverse_arcs = {}, {}
        for border, arc, bubble in arcs.values():
            self.arcs[id(arc)] = (border, arc, bubble)
            reverse_border, reverse_arc, reverse_bubble = arcs[(id(arc.end), id(arc.start), -arc.angle)]
            self.reverse_arcs[id(arc)] = (reverse_border, reverse_arc, reverse_bubble)

        nodes = {}
        for border, arc, _ in arcs.values():
            node = arc.start
            value = nodes.setdefault(id(node), [False, node, []])
            value[0] |= border
            value[2].append(arc)

        self.nodes: dict[int, tuple[bool, Node, tuple[Arc, Arc, Arc]]]
        self.nodes = {node_id: (border, node, tuple(node_arcs)) for node_id, (border, node, node_arcs) in nodes.items()}
        for border, node, node_arcs in self.nodes.values():
            assert len(node_arcs) == 3

    def get_arcs(self):
        return [arc for _, arc, *_ in self.arcs.values()]

    def update(self, frame: int, delta_time: float):
        self.update_arcs(frame, delta_time)
        self.update_nodes(frame, delta_time)

    def update_arcs(self, frame: int, delta_time: float):
        areas = {id(bubble): bubble.area() for border, bubble in self.bubbles.values()}

        visited = set()
        for border, arc, bubble in self.arcs.values():
            if id(arc) in visited:
                continue
            reverse_border, reverse_arc, reverse_bubble = self.reverse_arcs[id(arc)]
            if border or reverse_border:
                angle = math.asin(abs(arc.end.position - arc.start.position) / 2)
                if border:
                    angle = -angle
                arc.angle = angle
                reverse_arc.angle = -angle
            else:
                area, reverse_area = areas[id(bubble)], areas[id(reverse_bubble)]
                assert area > 0
                assert reverse_area > 0
                delta_angle = (area - reverse_area) / abs(arc.end.position - arc.start.position) ** 2 * 6
                delta_angle *= delta_time * self.arc_speed
                arc.angle -= delta_angle
                reverse_arc.angle = -arc.angle

            visited.add(id(arc))
            visited.add(id(reverse_arc))

    def update_nodes(self, frame: int, delta_time: float):
        for border, node, arcs in self.nodes.values():
            offset = 0
            for arc in arcs:
                arc_pull = (arc.end.position - arc.start.position) * cmath.rect(1, -arc.angle)
                arc_pull /= abs(arc_pull)
                offset += arc_pull
            node.position += offset * self.node_speed * delta_time
            if border:
                node.position /= abs(node.position)

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
