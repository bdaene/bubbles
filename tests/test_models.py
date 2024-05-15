from math import isclose

import pytest

from bubbles.models import Bubble, Node


@pytest.mark.parametrize("bubble, expected_area", [
    (Bubble.from_nodes(
        nodes=[Node(-4 - 3j), Node(3.78 - 3.11j), Node(3.34 + 2.59j), Node(-5.14 + 3.47j), Node(-10.26 + 0.87j)],
        angles=[0] * 5
    ),
     67.1252
    ),
    (Bubble.from_nodes(
        nodes=[Node(-4 - 3j), Node(3.78 - 3.11j), Node(3.34 + 2.59j), Node(-5.14 + 3.47j)],
        angles=[0.3, -0.7, 0, 2.1]
    ),
     84.7833361091657
    )
])
def test_bubble_area(bubble, expected_area):
    assert isclose(bubble.area(), expected_area)
