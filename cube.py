import numpy as np

F_U = 0
F_L = 1
F_F = 2
F_R = 3
F_B = 4
F_D = 5

C_W = 0
C_O = 1
C_G = 2
C_R = 3
C_B = 4
C_Y = 5

_colorToLetter = {
    C_W: 'W',
    C_O: 'O',
    C_G: 'G',
    C_R: 'R',
    C_B: 'B',
    C_Y: 'Y',
}

class Cube:
    def __init__(self):
        self.faces = [
            np.ones((3, 3), dtype=int) * C_W,
            np.ones((3, 3), dtype=int) * C_O,
            np.ones((3, 3), dtype=int) * C_G,
            np.ones((3, 3), dtype=int) * C_R,
            np.ones((3, 3), dtype=int) * C_B,
            np.ones((3, 3), dtype=int) * C_Y,
        ]

    def __repr__(self):
        # FIXME: Do this without 6*3*3 local variables.
        [[utl, utm, utr], [uml, umm, umr], [ubl, ubm, ubr]] = self.U
        [[ltl, ltm, ltr], [lml, lmm, lmr], [lbl, lbm, lbr]] = self.L
        [[ftl, ftm, ftr], [fml, fmm, fmr], [fbl, fbm, fbr]] = self.F
        [[rtl, rtm, rtr], [rml, rmm, rmr], [rbl, rbm, rbr]] = self.R
        [[btl, btm, btr], [bml, bmm, bmr], [bbl, bbm, bbr]] = self.B
        [[dtl, dtm, dtr], [dml, dmm, dmr], [dbl, dbm, dbr]] = self.D
        return """\
        {} {} {}
        {} {} {}
        {} {} {}

{} {} {}   {} {} {}   {} {} {}   {} {} {}
{} {} {}   {} {} {}   {} {} {}   {} {} {}
{} {} {}   {} {} {}   {} {} {}   {} {} {}

        {} {} {}
        {} {} {}
        {} {} {}""".format(*[_colorToLetter[x] for x in [
                             utl, utm, utr,
                             uml, umm, umr,
                             ubl, ubm, ubr,

            ltl, ltm, ltr,   ftl, ftm, ftr,   rtl, rtm, rtr,   btl, btm, btr,
            lml, lmm, lmr,   fml, fmm, fmr,   rml, rmm, rmr,   bml, bmm, bmr,
            lbl, lbm, lbr,   fbl, fbm, fbr,   rbl, rbm, rbr,   bbl, bbm, bbr,

                             dtl, dtm, dtr,
                             dml, dmm, dmr,
                             dbl, dbm, dbr]])

    def rotateFace(self, face):
        self.faces[face] = np.rot90(self.faces[face])
        _cyclicallyRotate(self.getSurroundingSlices(face))

    def getSurroundingSlices(self, face):
        # TODO maybe align these?
        if   face == F_U:
            return self.F[0, :], self.L[0, :], self.B[0, :], self.R[0, :]
        elif face == F_L:
            return self.U[:, 0], self.F[:, 0], self.D[:, 0], self.B[::-1, -1]
        elif face == F_F:
            return self.L[::-1, -1], self.U[-1, :], self.R[:, 0], \
                self.D[0, ::-1]
        elif face == F_R:
            return self.D[::-1, -1], self.F[::-1, -1], self.U[::-1, -1], \
                self.B[:, 0]
        elif face == F_B:
            return self.R[::-1, -1], self.U[0, ::-1], self.L[0, :], \
                self.D[::-1, -1]
        elif face == F_D:
            return self.B[-1, :], self.L[-1, :], self.F[-1, :], self.R[-1, :]
        else:
            assert False

    @property
    def U(self):
        return self.faces[F_U]
    @property
    def L(self):
        return self.faces[F_L]
    @property
    def F(self):
        return self.faces[F_F]
    @property
    def R(self):
        return self.faces[F_R]
    @property
    def B(self):
        return self.faces[F_B]
    @property
    def D(self):
        return self.faces[F_D]


def _cyclicallyRotate(l):
    a, b, c, d = [x.copy() for x in l]
    a[:], b[:], c[:], d[:] = d, a, b, c


if __name__ == '__main__':
    cube = Cube()
    cube.rotateFace(F_F)
    print(cube)

