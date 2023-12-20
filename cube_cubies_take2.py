import numpy as np


########################################
# Driver code / self-tests

def main():
    selfTest()
    cube = Cube()
    print(cube)
    print("\n" + "-"*29 + "\n")
    cube.rotateFace(F_R)
    print(cube)

def selfTest():
    assert oppositeColor(C_R) == C_O
    assert oppositeColor(C_O) == C_R
    assert oppositeColor(C_W) == C_Y
    assert oppositeColor(C_Y) == C_W
    assert oppositeColor(C_G) == C_B
    assert oppositeColor(C_B) == C_G

    assert getCubieFDR(makeCubie(C_R, C_W)) == (C_R, C_W, C_G)
    assert getCubieFDR(makeCubie(C_Y, C_R)) == (C_Y, C_R, C_G)
    assert getCubieFDR(makeCubie(C_O, C_B)) == (C_O, C_B, C_Y)
    assert getCubieFDR(makeCubie(C_G, C_Y)) == (C_G, C_Y, C_R)


########################################
# The cube

# Constants for the 6 faces
F_U = 0
F_L = 1
F_F = 2
F_R = 3
F_B = 4
F_D = 5

# Coordinate axes are (in order): front-ness, down-ness, right-ness. That is:
#   - (0, 0, 0) is the BUL corner
#   - (2, 0, 0) is the FUL corner
#   - (0, 2, 0) is the BDL corner
#   - (0, 0, 2) is the BUR corner
# This means that numpy's pretty-print order matches the layout of the cube:
#   - Pages go back-to-front
#   - Rows go up-to-down
#   - Columns go left-to-right

_axesForClockwiseRotation = {
    F_R : (1, 0), # down  to front
    F_L : (0, 1), # front to down
    F_U : (2, 0), # right to front
    F_D : (0, 2), # front to right
    F_F : (2, 1), # right to down
    F_B : (1, 2), # down  to right
}

class Cube:
    def __init__(self):
        self.cubies = np.full((3, 3, 3), CANONICAL_CUBIE)

    # FIXME/BOOKMARK: This and rotateWholeCube don't actually change the
    # orientations of the cubies. How to specify the axis of rotation for
    # rotateCubie? Need a clearer understanding of the relationship between
    # "cube coordinates" and "cubie coordinates". Which probably mostly means a
    # clearer intuition for which axis is which when indexing numpy arrays...
    #   - Idea: can we just pass a face, and have rotateCubie use
    #     _axesForClockwiseRotation? Something like:
    #         fdr = getCubieFDR(cubie)
    #         rotAxes = _axesForClockwiseRotation[face]
    #         newFdr = fdr[:]
    #         newFdr[rotAxes[1]] = fdr[rotAxes[0]]
    #         newFdr[rotAxes[0]] = fdr[oppositeColor(rotAxes[1])]
    #     Though this feels like I'm reimplementing np.rot90... can we express
    #     this somehow as a 3D array so that rot90 just does the right thing?
    #       - Or a 4D array consisting of 2 slices for the 2 3D vectors we need
    #         to rotate?
    #           - No, that's too complicated
    def rotateFace(self, aboutFace, numQuarterTurns=1):
        '''
        Rotate just one face of the cube.
        '''

        # Note this is not the most efficient implementation, but it's
        # relatively easy to conceptualize.

        # First, rotate the cube so the face in question is in front.
        toFrontAbout, toFrontNum = self._getRotationFaceToFront(aboutFace)
        self.rotateWholeCube(toFrontAbout, toFrontNum)

        # Next, rotate the front face by the requested amount.
        self.cubies[0] = np.rot90(self.cubies[0], k=numQuarterTurns)

        # Finally, undo the original rotation.
        self.rotateWholeCube(toFrontAbout, -toFrontNum)

    def _getRotationFaceToFront(self, face):
        '''
        Return (aboutFace, numQuarterTurns) that, when passed to
        rotateWholeCube, would move 'face' to the front of the cube. For F_B,
        do this in such a way that the orientation comes out correctly for
        drawing the net for the cube (that is, rotate about the U/D axis, not
        the L/R axis).
        '''

        return {
            F_F : (F_U, 0), # No rotation needed
            F_R : (F_U, 1),
            F_B : (F_U, 2), # Use U/D axis so orientation is correct for net
            F_L : (F_U, 3),
            F_D : (F_R, 1),
            F_U : (F_R, 3),
        }[face]

    def rotateWholeCube(self, aboutFace, numQuarterTurns=1):
        '''
        Rotate the entire cube clockwise about aboutFace by
        numQuarterTurns * 90 degrees.
        '''
        self.cubies = self._getRotatedCubies(aboutFace, numQuarterTurns)

    # TODO should this change the orientations of the cubies?
    #   - If not, then rotateWholeCube is no longer a trivial wrapper around it
    #   - If so, then it becomes kind of expensive for __repr__ to use given
    #     that __repr__ already knows which face to access
    #       - On the other hand, maybe getCubieFaces becomes obsolete if we
    #         always rotate the cube so we're accessing only front faces of
    #         cubies.
    #           - But if we're going to take advantage of this, probably the
    #             front face of the cubie should be one of the two actually
    #             stored in the cubie's number form (so we don't have to do a
    #             cross-product to reconstruct it every time).
    def _getRotatedCubies(self, aboutFace, numQuarterTurns=1):
        '''
        Return the new cubies array that would result from a cube rotation
        (as with rotateWholeCube), but don't modify the cube.
        '''

        return np.rot90(self.cubies, axes=_axesForClockwiseRotation[aboutFace],
                k=numQuarterTurns)

    def __repr__(self):
        front = self.faceToString(F_F, self.cubies[0, :, :])

        # TODO use _getRotationFaceToFront here?

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
# third (perpendicular) face given two faces in known positions. The coordinate
# axes here are the same as for the cube: front-ness, down-ness, right-ness.
#
# Since we're going to put these into numpy arrays which want to have single
# numbers, pack triples of (-1, 0, 1) into 6-bit numbers: bits 0,1 represent
# the page axis (blue->green), 2,3 the row axis (white->yellow), 4,5 the column
# axis (orange->red). Store -1 as 2 (i.e., take the coordinates mod 3) so that
# the 6 colors all pack to powers of 2.
C_G = 0b000001 # ( 1,  0,  0)
C_B = 0b000010 # (-1,  0,  0)
C_Y = 0b000100 # ( 0,  1,  0)
C_W = 0b001000 # ( 0, -1,  0)
C_R = 0b010000 # ( 0,  0,  1)
C_O = 0b100000 # ( 0,  0, -1)
C_SHIFT = 6
C_MASK  = (1 << C_SHIFT) - 1

_colorToLetter = {
    C_G: 'G',
    C_B: 'B',
    C_Y: 'Y',
    C_W: 'W',
    C_R: 'R',
    C_O: 'O',
}

def makeCubie(front, down):
    return (down << C_SHIFT) | front

CANONICAL_CUBIE = makeCubie(C_G, C_Y)

# TODO:
# def rotateCubie(cubie, ...how to specify axis?):

def getCubieFaces(cubie):
    """
    Return the list of face colors for a cubie, in ULFRBD order
    """

    fdr = getCubieFDR(cubie)
    front, down, right = fdr
    back, up, left = [oppositeColor(c) for c in fdr]
    return (up, left, front, right, back, down)

def getCubieFDR(cubie):
    """
    Return, in order, the sticker colors for the F, D, and R sides of a cubie.
    (That is, the 3 positive axes in order.)
    """
    front = cubie & C_MASK
    down  = cubie >> C_SHIFT
    right = packColor(np.cross(unpackColor(front), unpackColor(down)))
    # If front and down are either the same color or opposite colors, then
    # their cross product will be (0, 0, 0), which packs to 0. This indicates
    # an invalid cubie.
    assert right != 0
    return (front, down, right)

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

