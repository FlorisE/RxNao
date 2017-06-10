from math import sqrt

class Position6D():
    def __init__(self, values, similarity_threshold=0.2):
        self.robot_pos = values[0]
        self.time = values[2][1]
        self.x, self.y, self.z = self.robot_pos[0:3]
        self.similarity_threshold = similarity_threshold

    def distance(self, x_p=0, y_p=0, z_p=0):
        def sqrdiff(a, b): return pow(abs(a-b), 2)

        x, y, z = self.x, self.y, self.z
        return sqrt(sqrdiff(x, x_p) + sqrdiff(y, y_p) + sqrdiff(z, z_p))

    def __eq__(self, other):
        return self.distance(other.x, other.y, other.z) <= self.similarity_threshold

    def merge_from(self, other):
        def avg(a, b): return (a + b) / 2

        self.x = avg(self.x, other.x)
        self.y = avg(self.y, other.y)
        self.z = avg(self.z, other.z)
        self.time = max(self.time, other.time)


class Blob():
    def __init__(self, values):
        self.robot_pos = Position6D(values)

    def distance(self):
        return self.robot_pos.distance()

    def __eq__(self, other):
        return self.robot_pos == other.robot_pos