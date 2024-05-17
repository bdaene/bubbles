import math
from itertools import count
from random import Random
from time import sleep, perf_counter

from bubbles.models import Node, Arc, Bubble


class Simulation:

    def __init__(self, interval=0.01):
        self.interval = interval

        bubble = Bubble.from_nodes(
            nodes=[Node(-4 - 3j), Node(3.78 - 3.11j), Node(3.34 + 2.59j), Node(-5.14 + 3.47j)],
            angles=[0.3, -0.7, 0, 2.1])
        border = Arc.circle(Node(1))
        border = Arc(Node(-1), Node(1), 0)

        self.nodes = {}
        self.arcs = {id(border): border for border in bubble.arcs}
        self.bubbles = {id(border): (Bubble([border]), Bubble([border.reverse()]))}

        self.random = Random()
        self.running = False

    def update(self, delta_time):
        for arc in self.arcs.values():
            arc.start.position += complex(self.random.gauss(0, 1), self.random.gauss(0, 1)) * delta_time
            arc.end.position += complex(self.random.gauss(0, 1), self.random.gauss(0, 1)) * delta_time
            arc.angle += self.random.gauss(0, 1) * delta_time
            arc.angle = min(math.pi - 0.001, max(-math.pi + 0.001, arc.angle))

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

            self.update(delta_time)
            sleep(self.interval)

    def stop(self):
        self.running = False
