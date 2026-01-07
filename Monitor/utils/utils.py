class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = clamp(r, 0, 255)
        self.g = clamp(g, 0, 255)
        self.b = clamp(b, 0, 255)


    @staticmethod
    def from_hex(hex: str):
        hex = hex.lstrip("#")
        t = tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))
        return Color(t[0], t[1], t[2])
    
    def as_tuple(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)

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
    def __init__(self, ledsCount: int, line: int = 0):
        """
        Initializes LED strip and handles sub strips based on number of indicators
        """
        self.ledsCount = ledsCount
        # Init main strip
        self.strip: list[Color] = list()

        self.line = line
        
        black = Color(0, 0, 0)

        # Fill the strip with empty pixels
        for i in range(ledsCount):
            self.strip.append(black)

    def show(self) -> bytearray:
        payload = bytearray()

        for color in self.strip:
            payload.extend([color.r, color.g, color.b])

        packet = bytearray([0xA5, 0x5A, 0xA5, self.line, len(self.strip)]) + payload

        print("Packet hex:", packet.hex(" "))
        return packet

    def setPixel(self, i: int, color: Color):
        self.strip[i] = color

    def clear(self):
        # Fill the strip with empty pixels
        for i in range(self.ledsCount):
            self.strip[i] = Color(0, 0, 0)

    def fill(self, color: Color):
        for i in range(self.ledsCount):
            self.strip[i] = color
