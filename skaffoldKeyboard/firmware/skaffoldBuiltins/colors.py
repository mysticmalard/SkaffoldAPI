from ..decos import *

# TODO: Add HSV support
@_op('rgb')
class Color:
    def __init__(self, *args: tuple[int, int, int]) -> None:
        self.args = args
    def __add__(self, other: Color) -> Color:
        return Color(*map(lambda x, y: x + y, zip(self.args, other.args)))
    def __mul__(self, other: float) -> Color:
        return Color(*map(lambda x: x * other, self.args))
    def __rmul__(self, other: float) -> Color:
        return Color(*map(lambda x: x * other, self.args))

BLACK = Color(0, 0, 0)
BLUE = Color(0, 0, 255)
GREEN = Color(0, 255, 0)
CYAN = Color(0, 255, 255)
RED = Color(255, 0, 0)
MAGENTA = Color(255, 0, 255)
YELLOW = Color(255, 255, 0)
WHITE = Color(255, 255, 255)

ORANGE = Color(255, 128, 0)
LIME = Color(128, 255, 0)
PURPLE = Color(128, 0, 255)
PINK = Color(255, 0, 128)
SKY = Color(0, 128, 255)
MINT = Color(0, 255, 128)