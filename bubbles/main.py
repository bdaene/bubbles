from threading import Thread

from bubbles.simulation import Simulation
from bubbles.ui import UI


def main():
    simulation = Simulation(interval=0.001)
    ui = UI(simulation)

    simulation_thread = Thread(target=simulation.run, daemon=True)
    simulation_thread.start()

    ui.show()
    simulation.stop()


if __name__ == '__main__':
    main()
