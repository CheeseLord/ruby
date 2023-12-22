import logging
import numpy as np
import re  # Now we have two problems


########################################
# Driver code / self-tests

def main():
    #logging.basicConfig(level=logging.DEBUG)

    selfTest()
    cube = Cube()
    print(cube)
    print('\n' + '-'*29 + '\n')
    cube.rotateFace(F_R)
    print(cube)
    print('\n' + '-'*29 + '\n')
    # T perm (minus the initial R that we already did)
    cube.doMoves("U R' U' R' F R2 U' R' U' R U R' F'")
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

_oppositeFace = {
    F_R: F_L,
    F_L: F_R,
    F_U: F_D,
    F_D: F_U,
    F_F: F_B,
    F_B: F_F,
}

_faceToLetter = {
    F_U: 'U',
    F_L: 'L',
    F_F: 'F',
    F_R: 'R',
    F_B: 'B',
    F_D: 'D',
}

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

# TODO compute _faceToLetter automatically from this
_notationFaceTurns = {
    'R': F_R,
    'L': F_L,
    'U': F_U,
    'D': F_D,
    'F': F_F,
    'B': F_B,
}

_notationWholeCube = {
    'x': F_R,
    'y': F_U,
    'z': F_F,
}

_notationMiddleSlice = {
    'M': F_L, # NOTE! Opposite direction from 'x'
    'E': F_D, # NOTE! Opposite direction from 'y'
    'S': F_F, # Same direction as 'z'
}

def frontSlice(cubies):
    return cubies[2]

# When parsing a cube algorithm like "R U R'", primarily split on whitespace.
# However, sometimes for longer algorithms, people also add parentheses to show
# portions of the algorithm that are easier to remember together, as in this
# version of the Ra perm:
#     (R U' R' U') (R U R D) (R' U' R D') (R' U2' R')
# When parsing an algorithm, don't enforce that the parentheses group sensibly;
# just split on any whitespace or parentheses.
#
# Note that we have to use non-capturing parentheses here, else the matched
# groups would be included in the output of re.split(). See:
#     https://stackoverflow.com/a/10974950
_algSplitRe = re.compile(r'(?:\s|\(|\))+')

class Cube:
    def __init__(self):
        self.cubies = np.full((3, 3, 3), CANONICAL_CUBIE)

    def doMoves(self, moves):
        # If moves is given as a string, split it using _algSplitRe before we
        # start parsing it. Note that this means you have to put spaces between
        # all the moves in your algorithms; you can't just write "RUR'U'" and
        # expect the Cube class to sort it out. For a 3x3 cube it would be
        # possible to parse the moves without this pre-splitting logic:
        # [RLUDFBrludfbxyzMES] always introduce a new move, [w2'] never do, and
        # no other characters are used. But for larger cubes, there is an
        # ambiguity in the notation, so it would be bad precedent to allow
        # this. For wide and slice moves on larger cubes, the number of layers
        # or the slice is specified by prepending a number to the move: e.g.,
        # 3Rw turns the rightmost 3 layers, and 3R turns the third layer from
        # the right. So the string "R2U" could mean either "R2 U" or "R 2U".
        if type(moves) == str:
            moves = _algSplitRe.split(moves)
        for move in moves:
            logging.debug("\n\n>>> EXECUTE MOVE: %s", move)
            # Skip empty strings in case moves started/ended with a paren.
            if move:
                self.doOneMove(move)
            logging.debug('After executing move: %s\n%s', move, self)

    def doOneMove(self, move):
        face   = None
        isWide = False

        faceLetter = move[0]
        rest       = move[1:]

        # '[RLUDFB]' indicate a normal face turn
        face = _notationFaceTurns.get(faceLetter, None)
        if face is not None:
            # '[RLUDFB]w' indicate a wide face turn (turn 2 layers at once)
            if rest and rest[0] == 'w':
                isWide = True
                rest = rest[1:]
        # '[rludfb]' also indicate a wide face turn
        elif faceLetter.islower():
            face = _notationFaceTurns.get(faceLetter.upper(), None)

        numTurns = 1
        # Note: intentionally allow "2'" since I've seen that used to indicate
        # "rotate twice counterclockwise" (it's functionally equivalent to just
        # "2", but provides a hint about which way you actually turn the face
        # when executing). Probably we should allow "'2" similarly, though I
        # haven't seen it yet.
        if rest and rest[0] == '2':
            numTurns = 2
            rest = rest[1:]
        if rest and rest[0] == "'":
            numTurns = -numTurns
            rest = rest[1:]
        if rest:
            raise ValueError(f'Unexpected characters at end of move: {move!r}')

        # Handle normal face turns first because they're the common case
        if face is not None:
            if not isWide:
                self.rotateFace(face, numTurns)
            else:
                # For a wide turn, rotate the whole cube and then rotate the
                # opposite face back. Note that because the turns are clockwise
                # relative to the face being turned, we do not need to negate
                # numTurns when rotating the opposite face. For example, Rw is
                # equivalent to x L, NOT x L'.
                self.rotateWholeCube(face, numTurns)
                self.rotateFace(_oppositeFace[face], numTurns)
            return

        # Not a normal face turn. Either a whole-cube rotation or a middle
        # slice turn (or an error).
        face = _notationWholeCube.get(faceLetter, None)
        if face is not None:
            self.rotateWholeCube(face, numTurns)
            return

        face = _notationMiddleSlice.get(faceLetter, None)
        if face is not None:
            # For a middle-slice turn, do a wide turn of the corresponding face
            # in the same direction, then a normal turn in the opposite
            # direction. For example, M is equivalent to Lw L'.
            # Wide turn
            self.rotateWholeCube(face, numTurns)
            self.rotateFace(_oppositeFace[face], numTurns)
            # Normal turn in opposite direction
            self.rotateFace(face, -numTurns)
            return

        raise ValueError(f'Unrecognized face letter in move: {move!r}')

    # TODO rename numQuarterTurns to numTurns, or maybe just turns, in a few
    # functions? Maybe also aboutFace -> face.
    def rotateFace(self, aboutFace, numQuarterTurns=1):
        '''
        Rotate just one face of the cube.
        '''

        # Note this is not the most efficient implementation, but it's
        # relatively easy to conceptualize.

        self._debugCube("rotateFace start (%s)" % _faceToLetter[aboutFace])

        # First, rotate the cube so the face in question is in front.
        toFrontAbout, toFrontNum = self._getRotationFaceToFront(aboutFace)
        self.rotateWholeCube(toFrontAbout, toFrontNum)

        self._debugCube("=> rotateFace after rotate to front")

        # Next, rotate the front face by the requested amount. Note that rot90
        # defaults to the axes in counterclockwise order, so negate
        # numQuarterTurns for a clockwise rotation.
        # TODO factor out 2, as with frontSlice.
        self.cubies[2] = np.rot90(self.cubies[2], k=-numQuarterTurns)
        self.cubies[2] = self._rotateCubies(self.cubies[2], F_F,
                numQuarterTurns)

        self._debugCube("=> rotateFace after rotate front face")

        # Finally, undo the original rotation.
        self.rotateWholeCube(toFrontAbout, -toFrontNum)

        self._debugCube("=> rotateFace after rotate back to orig face")

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
        self._debugCube("rotateWholeCube(%s, %d), start" %
                (_faceToLetter[aboutFace], numQuarterTurns))

        self.cubies = self._getRotatedCubies(aboutFace, numQuarterTurns)
        self._debugCube("=> rotateWholeCube after permute")

        self.cubies = self._rotateCubies(self.cubies, aboutFace,
                numQuarterTurns)
        self._debugCube("=> rotateWholeCube after orient")

    # FIXME: Name too similar to _getRotatedCubies.
    def _rotateCubies(self, cubies, aboutFace, numQuarterTurns=1):
        doRotate = lambda cubie: rotateCubie(cubie, aboutFace, numQuarterTurns)
        vecRotate = np.vectorize(doRotate)
        return vecRotate(cubies)

    # TODO should this change the orientations of the cubies?
    #   - If not, then rotateWholeCube is no longer a trivial wrapper around it
    #     (current behavior)
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
        self._debugCube("Cube.__repr__")
        front = self.faceToString(F_F, frontSlice(self.cubies))

        # TODO use _getRotationFaceToFront here?

        # clockwise about L maps U to F
        up    = self.faceToString(F_U, frontSlice(np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_L])))
        # clockwise about R maps D to F
        down  = self.faceToString(F_D, frontSlice(np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_R])))

        # clockwise about D maps L to F
        left  = self.faceToString(F_L, frontSlice(np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_D])))
        # clockwise about U maps R to F
        right = self.faceToString(F_R, frontSlice(np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_U])))

        # Twice clockwise about U maps B to F (in the orientation we want)
        back  = self.faceToString(F_B, frontSlice(np.rot90(self.cubies,
                        axes=_axesForClockwiseRotation[F_U], k=2)))

        # TODO refactor with part of faceToString to avoid hardcoding this
        emptyFace = '     \n     \n     '

        return concatFaces([emptyFace, up]) + '\n\n' + \
            concatFaces([left, front, right, back]) + '\n\n' + \
            concatFaces([emptyFace, down])

    def _debugCube(self, msg):
        logging.debug("%s:\n%s", msg,
            np.vectorize(_debugCubieStr)(self.cubies))

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

def rotateCubie(cubie, face, numQuarterTurns=1):
    fdr = list(getCubieFDR(cubie))
    rotAxes = _axesForClockwiseRotation[face]
    #logging.debug("rotateCubie(%s, %s, %d)" %
    #        (_debugCubieStr(cubie), _faceToLetter[face], numQuarterTurns))
    for i in range(numQuarterTurns % 4):
        oldFdr = fdr[:]
        fdr[rotAxes[1]] = oldFdr[rotAxes[0]]
        fdr[rotAxes[0]] = oppositeColor(oldFdr[rotAxes[1]])
        #logging.debug("=> After %d rotations: %s" %
        #        (i + 1, "".join([_colorToLetter[c] for c in fdr])))
    front, down, _ = fdr
    return makeCubie(front, down)

def getCubieFaces(cubie):
    """
    Return the list of face colors for a cubie, in ULFRBD order
    """

    fdr = getCubieFDR(cubie)
    front, down, right = fdr
    back, up, left = [oppositeColor(c) for c in fdr]
    ret = (up, left, front, right, back, down)
    #logging.debug("getCubieFaces(%#x): fdr is %s, returning %s",
    #    cubie, list(map(_colorToLetter.get, fdr)), list(map(_colorToLetter.get, ret)))
    return ret

def _debugCubieStr(cubie):
    return "".join([_colorToLetter[c] for c in getCubieFDR(cubie)])

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

