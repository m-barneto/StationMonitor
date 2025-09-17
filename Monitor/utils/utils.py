from rpi_ws281x import Adafruit_NeoPixel, Color, ws  # type: ignore


def clamp(n, min, max):
    """ Clamp n between min and max.
    n is the number we would like to clip. 
    min and max specify the range to be used for clipping the number.
    """
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n


def hex_to_rgb(hex: str, scalar: float = 1.0) -> Color:
    """Convert hex code to color tuple with rgb ranges from 0-255
    Examples
    --------
        (255, 0, 255) == hex_to_rgb("#FF00FF")
        (255, 26, 255) == hex_to_rgb("FF1AFF")
    """
    hex = hex.lstrip("#")
    t = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
    return Color(int(t[0] * scalar), int(t[1] * scalar), int(t[2] * scalar))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b


def inv_lerp(a: float, b: float, v: float) -> float:
    """Inverse Linar Interpolation, get the fraction between a and b on which v resides.
    Examples
    --------
        0.5 == inv_lerp(0, 100, 50)
        0.8 == inv_lerp(1, 5, 4.2)
    """
    return (v - a) / (b - a)


class PixelStrip:
    def __init__(self, ledsCount: int, gpio: int = 18, channel: int = 0, brightness: int = 255, hz=800000, dma: int = 10, invert: bool = False):
        """
        Initializes LED strip and handles sub strips based on number of indicators
        """
        self.ledsCount = ledsCount
        # Init main strip
        self.strip = Adafruit_NeoPixel(
            self.ledsCount, gpio, hz, dma, invert, brightness, channel)
        self.strip.begin()

        # Clear entire main strip
        self.clear()

        # Show cleared main strip
        self.show()

    def show(self):
        self.strip.show()

    def setPixel(self, i: int, color: Color):
        self.strip.setPixelColor(int(i), color)

    def clear(self):
        self.fill(Color(0, 0, 0))

    def fill(self, color: Color):
        for i in range(self.ledsCount):
            self.setPixel(i, color)
