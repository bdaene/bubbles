import cmath
import math
from itertools import count
from threading import Lock
from time import sleep, perf_counter
from typing import Iterable

from attrs import define

from bubbles.models import Bubble, Arc, Node


@define
class BubbleInfo:
    bubble: Bubble
    border: bool = False

    def __attrs_post_init__(self):
        if self.border:
            if self.bubble.area() >= 0:
                raise ValueError(
                    "The border (first bubble) should be defined clockwise (its a bubble around infinity).")
        else:
            if self.bubble.area() < 0:
                raise ValueError("Interior bubbles should be defined counter-clockwise.")


@define
class ArcInfo:
    arc: Arc
    bubble: Bubble
    border: bool = False


@define
class NodeInfo:
    node: Node
    arcs: tuple[Arc, Arc, Arc]
    border: bool

    def __attrs_post_init__(self):
        if len(self.arcs) != 3:
            raise ValueError("Each node should be at the intersection of exactly 3 arcs (and 3 bubbles).")
        for arc in self.arcs:
            if arc.start is not self.node:
                raise ValueError("Each arc should start at the node.")


def _extract_info(bubbles: Iterable[Bubble]) -> tuple[
    dict[int, BubbleInfo],  # Bubbles
    dict[int, ArcInfo],  # Arcs
    dict[int, ArcInfo],  # Reversed arcs
    dict[int, NodeInfo],  # Nodes
]:
    bubbles = iter(bubbles)
    border = next(bubbles)
    bubbles_info = {id(border): BubbleInfo(border, True)} | {id(bubble): BubbleInfo(bubble) for bubble in bubbles}

    arcs = {(id(arc.start), id(arc.end), arc.angle): ArcInfo(arc, bubble_info.bubble, bubble_info.border)
            for bubble_info in bubbles_info.values() for arc in bubble_info.bubble.arcs}
    arcs_info = {id(arc_info.arc): arc_info for arc_info in arcs.values()}
    r_arcs_info = {id(arc_info.arc): arcs[(id(arc_info.arc.end), id(arc_info.arc.start), - arc_info.arc.angle)]
                   for arc_info in arcs.values()}

    nodes = {}
    for arc_info in arcs_info.values():
        node = arc_info.arc.start
        value = nodes.setdefault(id(node), [False, node, []])
        value[0] |= arc_info.border
        value[2].append(arc_info.arc)
    nodes_info = {node_id: NodeInfo(node, tuple[Arc, Arc, Arc](arcs), node_border)
                  for node_id, (node_border, node, arcs) in nodes.items()}
    return bubbles_info, arcs_info, r_arcs_info, nodes_info


class Simulation:

    def __init__(self, bubbles: Iterable[Bubble], interval=0.01, arc_speed=1., node_speed=1., split_size=0.2):
        self.interval = interval
        self.running = False
        self.lock = Lock()

        self.arc_speed = arc_speed
        self.node_speed = node_speed
        self.split_size = split_size

        self.bubbles, self.arcs, self.r_arcs, self.nodes = _extract_info(bubbles)

    def get_bubbles(self) -> list[Bubble]:
        with self.lock:
            return [bubble_info.bubble for bubble_info in self.bubbles.values() if not bubble_info.border]

    def update(self, frame: int, delta_time: float):
        with self.lock:
            self.update_arcs(frame, delta_time)
        with self.lock:
            self.update_nodes(frame, delta_time)

    def update_arcs(self, frame: int, delta_time: float):
        areas = {id(bubble_info.bubble): bubble_info.bubble.area() for bubble_info in self.bubbles.values()}

        visited = set()
        for arc_info in self.arcs.values():
            if id(arc_info.arc) in visited:
                continue

            r_arc_info = self.r_arcs[id(arc_info.arc)]
            d2 = abs(arc_info.arc.end.position - arc_info.arc.start.position)
            if arc_info.border or r_arc_info.border:
                angle = math.asin(d2 / 2)
                if arc_info.border:
                    angle = -angle
                arc_info.arc.angle = angle
            else:
                area, r_area = areas[id(arc_info.bubble)], areas[id(r_arc_info.bubble)]
                delta_angle = (area - r_area) / d2 ** 2 * 6
                delta_angle *= delta_time * self.arc_speed
                arc_info.arc.angle -= delta_angle
            r_arc_info.arc.angle = -arc_info.arc.angle

            visited.add(id(arc_info.arc))
            visited.add(id(r_arc_info.arc))

    def update_nodes(self, frame: int, delta_time: float):
        for node_info in self.nodes.values():
            offset = 0
            for arc in node_info.arcs:
                arc_pull = (arc.end.position - arc.start.position) * cmath.rect(1, -arc.angle)
                arc_pull /= abs(arc_pull)
                offset += arc_pull
            node_info.node.position += offset * self.node_speed * delta_time
            if node_info.border:
                node_info.node.position /= abs(node_info.node.position)

    def split(self, arc: Arc):
        if id(arc) not in self.arcs:
            return
        print(f"Splitting {arc}")
        with self.lock:
            arc_info = self.arcs.pop(id(arc))
            node_a = Node(arc.get_position((1 - self.split_size) / 2))
            node_b = Node(arc.get_position((1 + self.split_size) / 2))
            arc_start, arc_middle, arc_end = self._split(arc_info, node_a, node_b)

            r_arc_info = self.r_arcs.pop(id(arc))
            self.arcs.pop(id(r_arc_info.arc))
            self.r_arcs.pop(id(r_arc_info.arc))
            r_arc_start, r_arc_middle, r_arc_end = self._split(r_arc_info, node_b, node_a)

            self.r_arcs[id(arc_start)] = self.arcs[id(r_arc_end)]
            self.r_arcs[id(arc_end)] = self.arcs[id(r_arc_start)]
            self.r_arcs[id(r_arc_start)] = self.arcs[id(arc_end)]
            self.r_arcs[id(r_arc_end)] = self.arcs[id(arc_start)]

            arc_middle.angle = -math.pi / 2
            r_arc_middle.angle = -math.pi / 2
            arc_middle_r = arc_middle.reverse()
            r_arc_middle_r = r_arc_middle.reverse()
            bubble = Bubble([arc_middle_r, r_arc_middle_r])
            self.bubbles[id(bubble)] = BubbleInfo(bubble)
            self.arcs[id(arc_middle_r)] = ArcInfo(arc_middle_r, bubble)
            self.arcs[id(r_arc_middle_r)] = ArcInfo(r_arc_middle_r, bubble)
            self.r_arcs[id(arc_middle_r)] = self.arcs[id(arc_middle)]
            self.r_arcs[id(r_arc_middle_r)] = self.arcs[id(r_arc_middle)]
            self.r_arcs[id(arc_middle)] = self.arcs[id(arc_middle_r)]
            self.r_arcs[id(r_arc_middle)] = self.arcs[id(r_arc_middle_r)]

            start_node_info = self.nodes[id(arc_info.arc.start)]
            index = start_node_info.arcs.index(arc_info.arc)
            start_node_info.arcs = start_node_info.arcs[:index] + (arc_start,) + start_node_info.arcs[index + 1:]
            end_node_info = self.nodes[id(arc_info.arc.end)]
            index = end_node_info.arcs.index(r_arc_info.arc)
            end_node_info.arcs = end_node_info.arcs[:index] + (r_arc_start,) + end_node_info.arcs[index + 1:]

            border = arc_info.border | r_arc_info.border
            self.nodes[id(node_a)] = NodeInfo(node_a, (arc_middle, r_arc_middle_r, r_arc_end), border)
            self.nodes[id(node_b)] = NodeInfo(node_b, (r_arc_middle, arc_middle_r, arc_end), border)

    def _split(self, arc_info: ArcInfo, node_a: Node, node_b: Node):
        arc_start = Arc(arc_info.arc.start, node_a)
        arc_middle = Arc(node_a, node_b)
        arc_end = Arc(node_b, arc_info.arc.end)

        index = arc_info.bubble.arcs.index(arc_info.arc)
        arc_info.bubble.arcs = (arc_info.bubble.arcs[:index] + [arc_start, arc_middle, arc_end]
                                + arc_info.bubble.arcs[index + 1:])

        self.arcs[id(arc_start)] = ArcInfo(arc_start, arc_info.bubble, arc_info.border)
        self.arcs[id(arc_middle)] = ArcInfo(arc_middle, arc_info.bubble, arc_info.border)
        self.arcs[id(arc_end)] = ArcInfo(arc_end, arc_info.bubble, arc_info.border)

        return arc_start, arc_middle, arc_end

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
                print(*[f'{bubble_info.bubble.area():.3f}' for bubble_info in self.bubbles.values()])
                timestamp = new_timestamp

            self.update(frame, delta_time)
            sleep(self.interval)

    def stop(self):
        self.running = False
