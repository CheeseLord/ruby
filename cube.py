import numpy as np

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
        self.u = np.ones((3, 3), dtype=int) * C_W
        self.l = np.ones((3, 3), dtype=int) * C_O
        self.f = np.ones((3, 3), dtype=int) * C_G
        self.r = np.ones((3, 3), dtype=int) * C_R
        self.b = np.ones((3, 3), dtype=int) * C_B
        self.d = np.ones((3, 3), dtype=int) * C_Y

    def __repr__(self):
        # FIXME: Do this without 6*3*3 local variables.
        [[utl, utm, utr], [uml, umm, umr], [ubl, ubm, ubr]] = cube.u
        [[ltl, ltm, ltr], [lml, lmm, lmr], [lbl, lbm, lbr]] = cube.l
        [[ftl, ftm, ftr], [fml, fmm, fmr], [fbl, fbm, fbr]] = cube.f
        [[rtl, rtm, rtr], [rml, rmm, rmr], [rbl, rbm, rbr]] = cube.r
        [[btl, btm, btr], [bml, bmm, bmr], [bbl, bbm, bbr]] = cube.b
        [[dtl, dtm, dtr], [dml, dmm, dmr], [dbl, dbm, dbr]] = cube.d
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

    def rotateU(self):
        self.u = np.rot90(self.u)
        _cyclicallyRotate(
            self.f[0, :], self.l[0, :], self.b[0, :], self.r[0, :]
        )

    def rotateL(self):
        self.l = np.rot90(self.l)
        _cyclicallyRotate(
            self.u[:, 0], self.f[:, 0], self.d[:, 0], self.b[::-1, -1]
        )

    def rotateF(self):
        self.f = np.rot90(self.f)
        _cyclicallyRotate(
            self.l[::-1, -1], self.u[-1, :], self.r[:, 0], self.d[0, ::-1]
        )

    def rotateR(self):
        self.r = np.rot90(self.r)
        _cyclicallyRotate(
            self.d[::-1, -1], self.f[::-1, -1], self.u[::-1, -1], self.b[:, 0]
        )

    def rotateB(self):
        self.b = np.rot90(self.b)
        _cyclicallyRotate(
            self.r[::-1, -1], self.u[0, ::-1], self.l[0, :], self.d[::-1, -1]
        )

    def rotateD(self):
        self.d = np.rot90(self.d)
        _cyclicallyRotate(
            self.b[-1, :], self.l[-1, :], self.f[-1, :], self.r[-1, :]
        )


def _cyclicallyRotate(a, b, c, d):
    a[:], b[:], c[:], d[:] = d.copy(), a.copy(), b.copy(), c.copy()


if __name__ == '__main__':
    cube = Cube()
    cube.rotateF()
    print(cube)

