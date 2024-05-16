import cmath
import math
from typing import Iterable

import matplotlib.pyplot
import numpy
from matplotlib import patches, pyplot

from bubbles.models import Arc, Bubble, Node


def get_cord(arc: Arc) -> patches.Polygon:
    start, end = arc.start.position, arc.end.position
    return patches.Polygon(numpy.array([[start.real, start.imag], [end.real, end.imag]]), closed=False, fill=False)


def get_patch(arc: Arc) -> patches.Patch:
    if arc.is_flat:
        return get_cord(arc)
    if arc.is_circle:
        return patches.Circle((0, 0), abs(arc.start.position), fill=False)
    d = abs(arc.end.position - arc.start.position)
    c, s = math.cos(arc.angle), math.sin(arc.angle)
    h = c / s
    center = (arc.start.position + arc.end.position + h * 1j * (arc.end.position - arc.start.position)) / 2
    radius = d / s
    theta1 = math.degrees(cmath.phase(arc.start.position - center))
    theta2 = math.degrees(cmath.phase(arc.end.position - center))
    if arc.angle < 0:
        theta1, theta2 = 180 + theta2, 180+theta1
    return patches.Arc((center.real, center.imag), radius, radius, theta1=theta1, theta2=theta2)


def draw(arcs: Iterable[Arc], axes: matplotlib.pyplot.Axes):
    for arc in arcs:
        cord = get_cord(arc)
        cord.set_alpha(0.1)
        cord.set_linewidth(1)
        cord.set_zorder(2)
        axes.add_patch(cord)

        patch = get_patch(arc)
        patch.set_linewidth(2)
        patch.set_zorder(2)
        axes.add_patch(patch)


def main():
    bubble = Bubble.from_nodes(
        nodes=[Node(-4 - 3j), Node(3.78 - 3.11j), Node(3.34 + 2.59j), Node(-5.14 + 3.47j)],
        angles=[0.3, -0.7, 0, 2.1])

    figure, axes = pyplot.subplots(num="Bubbles")
    draw(bubble.arcs, axes)
    draw([Arc.circle()], axes)

    axes.set_aspect('equal')
    axes.set_xlim(-15, 15)
    axes.set_ylim(-10, 10)
    axes.set_axis_off()

    pyplot.show()


if __name__ == '__main__':
    main()
