import cmath
import math

from attrs import define


@define
class Node:
    position: complex


@define
class Arc:
    start: Node
    end: Node
    angle: float  # Angle between the arc and the vector start->end. Clockwise. In [-pi, pi].

    @classmethod
    def circle(cls, node: Node = Node(1)):
        return cls(node, node, math.pi)

    @property
    def is_flat(self) -> bool:
        return abs(self.angle) < 1e-3

    @property
    def is_circle(self) -> bool:
        return self.start is self.end

    @property
    def length(self) -> float:
        if self.is_circle:
            return math.tau * abs(self.start.position)
        d = abs(self.end.position - self.start.position)
        if self.is_flat:
            return d
        return d * self.angle / math.sin(self.angle)

    @property
    def area(self) -> float:
        if self.is_circle:
            return self.angle * abs(self.start.position) / 2
        d = abs(self.end.position - self.start.position) / 2
        if self.is_flat:
            return d ** 2 * self.angle * 2 / 3
        complex_angle = cmath.rect(1, self.angle)
        return d ** 2 * (self.angle / complex_angle.imag - complex_angle.real) / complex_angle.imag

    @property
    def center(self) -> complex:
        if self.is_circle:
            return 0
        # Note: no meaning if self.is_flat
        return (self.start.position + self.end.position
                + 1j * (self.end.position - self.start.position) / math.tan(self.angle)) / 2

    def get_position(self, t: float) -> complex:
        if self.is_circle:
            return self.start.position * cmath.rect(1, t * math.tau)
        if self.is_flat:
            return self.start.position * (1 - t) + self.end.position * t
        center = self.center
        return center + (self.start.position - center) * cmath.rect(1, 2 * self.angle * t)

    def reverse(self) -> 'Arc':
        return ReversedArc(self)


class ReversedArc(Arc):

    def __init__(self, arc: Arc):
        self.arc = arc

    @property
    def start(self):
        return self.arc.end

    @property
    def end(self):
        return self.arc.start

    @property
    def angle(self):
        return -self.arc.angle

    def reverse(self) -> Arc:
        return self.arc


@define
class Bubble:
    arcs: list[Arc]  # Arcs around the bubble in trigonometric order.

    @classmethod
    def from_nodes(cls, nodes, angles):
        arcs = [Arc(node, nodes[(i + 1) % len(nodes)], angle)
                for i, (node, angle) in enumerate(zip(nodes, angles))]
        return cls(arcs)

    def area(self) -> float:
        origin = self.arcs[0].start.position
        interior_area = sum(
            ((arc.end.position - origin) * (arc.start.position - origin).conjugate()).imag
            for arc in self.arcs[1:-1]
        ) / 2
        return interior_area + sum(arc.area for arc in self.arcs)
