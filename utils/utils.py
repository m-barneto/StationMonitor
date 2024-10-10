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
    def __init__(self, stripLength, edgeCount, brightness=255, gpio=18, hz=800000, dma=10, invert=False, channel=0):
        self.pixelCount = stripLength * edgeCount
        self.strip = Adafruit_NeoPixel(
            self.pixelCount, gpio, hz, dma, invert, brightness, channel)
        self.strip.begin()
        self.stripLength = stripLength
        self.edgeCount = edgeCount
        self.edgeLength = self.stripLength / self.edgeCount
        self.blankColor = Color(0, 0, 0)
        self.edgeHalfBuffer = []
        for i in range(int(self.edgeLength / 2)):
            self.edgeHalfBuffer.append(self.blankColor)
        self.edge = []
        for i in range(self.edgeLength):
            self.edge.append(self.blankColor)

    def show(self):
        self.strip.show()

    def setPixel(self, n, color):
        self.strip.setPixelColor(n, color.getBits())

    def fill(self, color=Color(0, 0, 0)):
        for i in range(int(self.edgeLength / 2)):
            self.edgeHalfBuffer[i] = color
        self.writeEdges(self.edgeHalfBuffer)
        self.show()

    def writeEdges(self, colors):
        for i in range(self.edgeCount):
            for p in range(self.edgeLength / 2):
                self.setPixel(i * self.edgeLength + p, colors[p])
                # might need to -1 after "- p"
                self.setPixel(i * self.edgeLength +
                              self.edgeLength - p - 1, colors[p])
