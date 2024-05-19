from threading import Thread

from bubbles.samples import get_sample_bubbles
from bubbles.simulation import Simulation
from bubbles.ui import UI


def main():
    bubbles = get_sample_bubbles(4)
    simulation = Simulation(bubbles, interval=0.01)
    ui = UI(simulation)

    simulation_thread = Thread(target=simulation.run, daemon=True)
    simulation_thread.start()

    ui.run(fps=25)
    simulation.stop()


if __name__ == '__main__':
    main()
