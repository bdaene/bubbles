import cmath
import math

import numpy
from matplotlib import patches, pyplot, animation
from matplotlib.artist import Artist
from matplotlib.axes import Axes

from bubbles.models import Arc
from bubbles.simulation import Simulation


def get_cord(arc: Arc, style: dict) -> patches.Polygon:
    start, end = arc.start.position, arc.end.position
    return patches.Polygon(numpy.array([[start.real, start.imag], [end.real, end.imag]]), closed=False, fill=False,
                           **style)


def get_arc(arc: Arc, style: dict) -> patches.Patch:
    if arc.is_flat:
        return get_cord(arc, style)
    center = arc.center
    if arc.is_circle:
        return patches.Circle((center.real, center.imag), abs(arc.start.position), fill=False, **style)
    diameter = 2 * abs(arc.start.position - center)
    theta1 = math.degrees(cmath.phase(arc.start.position - center))
    theta2 = math.degrees(cmath.phase(arc.end.position - center))
    if arc.angle < 0:
        theta1, theta2 = theta2, theta1
    return patches.Arc((center.real, center.imag), diameter, diameter, theta1=theta1, theta2=theta2, **style)


class UI:

    def __init__(self, simulation: Simulation):
        self.simulation = simulation

        figure, axes = pyplot.subplots(num="Bubbles")
        axes.set_aspect('equal')
        axes.set_xlim(-15, 15)
        axes.set_ylim(-15, 15)
        axes.set_axis_off()

        self.figure = figure
        self.axes: Axes = axes
        self.artists = []
        self.cord_style = dict(alpha=0.1, linewidth=1, zorder=1)
        self.arc_style = dict(linewidth=2, zorder=2)

        self.animation = animation.FuncAnimation(figure, self.update, interval=1000 / 75, cache_frame_data=False)

    def update(self, _frame) -> list[Artist]:
        for artist in self.artists:
            artist.remove()
        self.artists.clear()

        for simulation_arc in self.simulation.arcs.values():
            cord = get_cord(simulation_arc, self.cord_style)
            arc = get_arc(simulation_arc, self.arc_style)

            self.artists.append(self.axes.add_patch(cord))
            self.artists.append(self.axes.add_patch(arc))

        return self.artists

    @staticmethod
    def show():
        pyplot.show()
