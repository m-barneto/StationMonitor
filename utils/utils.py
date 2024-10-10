from rpi_ws281x import Adafruit_NeoPixel, Color  # type: ignore


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
    def __init__(self, ledsCount: int, indicatorCount: int = 2, gpio: int = 18, brightness: int = 10, hz=800000, dma: int = 10, invert: bool = False, channel: int = 0):
        self.ledsCount = ledsCount
        self.indicatorCount = indicatorCount
        self.indicatorNumPixels = int(self.ledsCount / self.indicatorCount)
        self.strip = Adafruit_NeoPixel(
            self.ledsCount, gpio, hz, dma, invert, brightness, channel)
        self.strip.begin()

    def show(self):
        self.strip.show()

    def setPixel(self, indicatorIndex: int, i: int, color: Color):
        self.strip.setPixelColor(
            (indicatorIndex * self.indicatorNumPixels) + i, color)
        print((indicatorIndex * self.indicatorNumPixels) +
              i, color.r, color.g, color.b)

    def clear(self, indicatorIndex):
        self.fill(indicatorIndex, Color(0, 0, 0))

    def fill(self, indicatorIndex: int, color: Color):
        start = indicatorIndex * self.indicatorNumPixels
        end = start + self.indicatorNumPixels
        for i in range(start, end):
            self.setPixel(indicatorIndex, i, color)
        self.show()
