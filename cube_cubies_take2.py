import numpy as np


########################################
# Driver code / self-tests

def main():
    selfTest()
    cube = Cube()
    print(cube)

def selfTest():
    assert oppositeColor(C_R) == C_O
    assert oppositeColor(C_O) == C_R
    assert oppositeColor(C_W) == C_Y
    assert oppositeColor(C_Y) == C_W
    assert oppositeColor(C_G) == C_B
    assert oppositeColor(C_B) == C_G

    assert getRUF(makeCubie(C_R, C_W)) == (C_R, C_W, C_G)
    assert getRUF(makeCubie(C_Y, C_R)) == (C_Y, C_R, C_G)
    assert getRUF(makeCubie(C_O, C_B)) == (C_O, C_B, C_Y)
    assert getRUF(makeCubie(C_G, C_Y)) == (C_G, C_Y, C_R)


########################################
# The cube

# Constants for the 6 faces
F_U = 0
F_L = 1
F_F = 2
F_R = 3
F_B = 4
F_D = 5

_axesForClockwiseRotation = {
    F_R : (0, 1), # back  to down
    F_L : (1, 0), # down  to back
    F_U : (0, 2), # back  to right
    F_D : (2, 0), # right to back
    F_F : (2, 1), # right to down
    F_B : (1, 2), # down  to right
}

class Cube:
    def __init__(self):
        # Indices are (in order): back-ness, down-ness, right-ness.
        # TODO: This works out reasonably with how the array gets
        # pretty-printed, but isn't it a left-handed coordinate system? Back
        # cross down should be left, not right. Does this matter?
        # TODO make the cubie coords match these... except see above.
        self.cubies = np.full((3, 3, 3), CANONICAL_CUBIE)

    def __repr__(self):
        front = self.faceToString(F_F, self.cubies[0, :, :])

        # clockwise about L maps U to F
        up    = self.faceToString(F_U, np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_L])[0, :, :])
        # clockwise about R maps D to F
        down  = self.faceToString(F_D, np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_R])[0, :, :])

        # clockwise about D maps L to F
        left  = self.faceToString(F_L, np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_D])[0, :, :])
        # clockwise about U maps R to F
        right = self.faceToString(F_R, np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_U])[0, :, :])

        # Twice clockwise about U maps B to F (in the orientation we want)
        back  = self.faceToString(F_B, np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_U], k=2)[0, :, :])

        # TODO refactor with part of faceToString to avoid hardcoding this
        emptyFace = '     \n     \n     '

        return concatFaces([emptyFace, up]) + '\n\n' + \
            concatFaces([left, front, right, back]) + '\n\n' + \
            concatFaces([emptyFace, down])

    def faceToString(self, face, faceGrid):
        """
        Return a string like:
            W W W
            W W W
            W W W
        representing a single face of the cube. The parameter face is one of
        the 6 face constants, F_U through F_D. faceGrid is a 2D array of
        cubies, in the same arrangement as they should be printed. That is,
        it'll be printed like:
            faceGrid[0,0] faceGrid[0,1] ...
            faceGrid[1,0]
            ...
        """
        return '\n'.join(
            ' '.join(
                    _colorToLetter[getCubieFaces(cubie)[face]]
                for cubie in row)
            for row in faceGrid)

def concatFaces(faces):
    splitFaces = [face.split('\n') for face in faces]
    numRows = len(splitFaces[0])
    assert all(len(splitFace) == numRows for splitFace in splitFaces)
    rows = []
    for r in range(numRows):
        rows.append('   '.join(splitFace[r] for splitFace in splitFaces))
    return '\n'.join(rows)


########################################
# Cubies

# Constants for the 6 colors.
#
# Idea: map each color to a (unit) vector representing its direction from the
# cube center when it's in the canonical state and orientation (solved, white
# on top, green in front). Then we can use the cross product to figure out the
# third (perpendicular) face given two faces in known positions. Since we're
# going to put these into numpy arrays which want to have single numbers,
# pack triples of (-1, 0, 1) into 6-bit numbers: bits 0,1 represent the
# red/orange direction (x axis), bits 2,3 the white/yellow (y) axis, bits 4,5
# the green/blue (z) axis. Store -1 as 2 (i.e., take the coordinates mod 3) so
# that every color is a nice power of 2.
C_R = 0b000001 # ( 1,  0,  0)
C_O = 0b000010 # (-1,  0,  0)
C_W = 0b000100 # ( 0,  1,  0)
C_Y = 0b001000 # ( 0, -1,  0)
C_G = 0b010000 # ( 0,  0,  1)
C_B = 0b100000 # ( 0,  0, -1)
C_SHIFT = 6
C_MASK  = (1 << C_SHIFT) - 1

_colorToLetter = {
    C_R: 'R',
    C_O: 'O',
    C_W: 'W',
    C_Y: 'Y',
    C_G: 'G',
    C_B: 'B',
}

def makeCubie(right, up):
    return (up << C_SHIFT) | right

CANONICAL_CUBIE = makeCubie(C_R, C_W)

def getCubieFaces(cubie):
    """
    Return the list of face colors for a cubie, in ULFRBD order
    """

    ruf = getRUF(cubie)
    right, up, front = ruf
    left, down, back = [oppositeColor(c) for c in ruf]
    return (up, left, front, right, back, down)

def getRUF(cubie):
    right = cubie & C_MASK
    up    = cubie >> C_SHIFT
    front = packColor(np.cross(unpackColor(right), unpackColor(up)))
    # If right and up are either the same color or opposite colors, then their
    # cross product will be (0, 0, 0), which packs to 0. This indicates an
    # invalid cubie.
    assert front != 0
    return (right, up, front)

def oppositeColor(color):
    return packColor([-x for x in unpackColor(color)])

def packColor(coords):
    'Convert a coordinate triple to a numerical color'
    # When packing, map -1 to 2 with val % 3.
    x, y, z = [val % 3 for val in coords]
    color =                z
    color = (color << 2) | y
    color = (color << 2) | x
    return color

def unpackColor(color):
    'Return a triple representing the unit vector given a numerical color'
    color = int(color)
    x =  color       & 0b11
    y = (color >> 2) & 0b11
    z = (color >> 4) & 0b11
    # When unpacking, map 2 to -1 with (val + 1) % 3 - 1.
    return tuple((val + 1) % 3 - 1 for val in [x, y, z])


########################################

if __name__ == '__main__':
    main()

