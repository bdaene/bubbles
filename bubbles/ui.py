import cmath
import math
from time import sleep

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

    def __init__(self, simulation: Simulation, size=1.5):
        self.simulation = simulation

        figure, axes = pyplot.subplots(num="Bubbles")
        axes.set_aspect('equal')
        axes.set_xlim(-size, size)
        axes.set_ylim(-size, size)
        axes.set_axis_off()

        self.figure = figure
        self.axes: Axes = axes
        self.artists = []
        self.cord_style = dict(alpha=0.1, linewidth=1, zorder=1)
        self.arc_style = dict(linewidth=2, zorder=2)

        self.interval = 0

    def update(self, _frame) -> list[Artist]:
        for artist in self.artists:
            artist.remove()
        self.artists.clear()

        for bubble in self.simulation.get_bubbles():
            for simulation_arc in bubble.arcs:
                cord = get_cord(simulation_arc, self.cord_style)
                arc = get_arc(simulation_arc, self.arc_style)
                arc.arc = simulation_arc
                arc.set_picker(True)

                self.artists.append(self.axes.add_patch(cord))
                self.artists.append(self.axes.add_patch(arc))

        sleep(self.interval)

        return self.artists

    def on_pick(self, event):
        if hasattr(event.artist, 'arc'):
            self.simulation.split(event.artist.arc)

    def run(self, fps: int, save_duration: float | None = None):
        if save_duration is None:
            self.figure.canvas.mpl_connect('pick_event', self.on_pick)
            movie = animation.FuncAnimation(self.figure, self.update, interval=1000 / fps, cache_frame_data=False)
            pyplot.show()
        else:
            self.interval = 1 / fps
            movie = animation.FuncAnimation(self.figure, self.update, frames=round(fps * save_duration))
            writer = animation.PillowWriter(fps=fps)
            movie.save('bubbles.gif', writer=writer)
