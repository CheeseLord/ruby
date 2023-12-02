import numpy as np


class Cube:
    def __init__(self):
        self.u = np.ones((3, 3), dtype=int) * 0
        self.l = np.ones((3, 3), dtype=int) * 1
        self.f = np.ones((3, 3), dtype=int) * 2
        self.r = np.ones((3, 3), dtype=int) * 3
        self.b = np.ones((3, 3), dtype=int) * 4
        self.d = np.ones((3, 3), dtype=int) * 5

    def __repr__(self):
        # FIXME: Write this.
        pass

    def rotateU(self):
        """ Rotate U face 90 degrees clockwise. """

        self.u = np.rot90(self.u)
        _cyclicallyRotate(
            self.f[0, :], self.l[0, :], self.b[0, :], self.r[0, :]
        )

    def rotateF(self):
        """ Rotate F face 90 degrees clockwise. """

        self.f = np.rot90(self.f)
        _cyclicallyRotate(
            self.l[::-1, -1], self.u[-1, :], self.r[:, 0], self.d[0, ::-1]
        )


def _cyclicallyRotate(a, b, c, d):
    a[:], b[:], c[:], d[:] = d, a, b, c

