class XAxisCylinderPosition:
    def __init__(self, x_min: float, x_max: float, y: float, z: float) -> None:
        if x_min > x_max:
            msg = "x_min must be less than or equal to x_max."
            raise ValueError(msg)

        self.x_min = x_min
        self.x_max = x_max
        self.y = y
        self.z = z

    @property
    def x_center(self) -> float:
        return (self.x_min + self.x_max) / 2
