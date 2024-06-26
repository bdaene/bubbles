import math

from bubbles.models import Bubble, Node, Arc


def get_sample_bubbles_2() -> list[Bubble]:
    #  /-\
    # 0---1
    #  \-/

    nodes = [Node(-1), Node(1)]
    arcs = [
        Arc(nodes[0], nodes[1], -math.pi / 2),  # 0
        Arc(nodes[0], nodes[1]),  # 1
        Arc(nodes[0], nodes[1], math.pi / 2),  # 2
    ]
    arcs += [arc.reverse() for arc in arcs]

    bubbles = [
        Bubble([arcs[0], arcs[2 + 3]]),
        Bubble([arcs[1], arcs[0 + 3]]),
        Bubble([arcs[2], arcs[1 + 3]]),
    ]

    return bubbles


def get_sample_bubbles_3() -> list[Bubble]:
    # |-3-|
    # | | |
    # | 0 |
    # |/ \|
    # 1---2

    nodes = [Node(0), Node(-0.5 - 0.5j), Node(+0.5 - 0.5j), Node(1j)]
    arcs = [
        Arc(nodes[0], nodes[1]),  # 0
        Arc(nodes[0], nodes[2]),  # 1
        Arc(nodes[0], nodes[3]),  # 2
        Arc(nodes[1], nodes[2]),  # 3
        Arc(nodes[1], nodes[3]),  # 4
        Arc(nodes[2], nodes[3]),  # 5
    ]
    arcs += [arc.reverse() for arc in arcs]

    bubbles = [
        Bubble([arcs[3 + 6], arcs[4], arcs[5 + 6]]),
        Bubble([arcs[0], arcs[3], arcs[1 + 6]]),
        Bubble([arcs[1], arcs[5], arcs[2 + 6]]),
        Bubble([arcs[2], arcs[4 + 6], arcs[0 + 6]]),
    ]

    return bubbles


def get_sample_bubbles_4() -> list[Bubble]:
    # 2-----5
    # |\   /|
    # | 0-1 |
    # |/   \|
    # 3-----4

    nodes = [Node(-0.5), Node(0.5), Node(-1 + 1j), Node(-1 - 1j), Node(+1 - 1j), Node(+1 + 1j)]
    arcs = [
        Arc(nodes[0], nodes[1]),  # 0
        Arc(nodes[0], nodes[2]),  # 1
        Arc(nodes[0], nodes[3]),  # 2
        Arc(nodes[1], nodes[4]),  # 3
        Arc(nodes[1], nodes[5]),  # 4
        Arc(nodes[2], nodes[3], 0.3),  # 5
        Arc(nodes[2], nodes[5], -0.3),  # 6
        Arc(nodes[3], nodes[4], 0.3),  # 7
        Arc(nodes[4], nodes[5], 0.3),  # 8
    ]
    arcs += [arc.reverse() for arc in arcs]
    bubbles = [
        Bubble([arcs[6], arcs[8 + 9], arcs[7 + 9], arcs[5 + 9]]),
        Bubble([arcs[0], arcs[4], arcs[6 + 9], arcs[1 + 9]]),
        Bubble([arcs[0 + 9], arcs[2], arcs[7], arcs[3 + 9]]),
        Bubble([arcs[1], arcs[5], arcs[2 + 9]]),
        Bubble([arcs[3], arcs[8], arcs[4 + 9]]),
    ]

    return bubbles


def get_sample_bubbles(id: int) -> list[Bubble]:
    return {
        2: get_sample_bubbles_2,
        3: get_sample_bubbles_3,
        4: get_sample_bubbles_4,
    }[id]()
