from cube_cubies_take2 import Cube

def main():
    import logging
    #logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)

    cube = Cube()

    print("Enter your scramble:")
    scramble = input("> ")
    cube.doMoves(scramble)

    print("\nYour cube looks like:")
    print(cube)

    print("Edges?")
    edges = input("> ")
    print("Parity? [y/n]")
    parity = input("> ")
    print("Corners?")
    corners = input("> ")

    for letter in edges:
        if not letter.isspace():
            doEdge(cube, letter)
            logging.info("Edge: %s\n%s", letter, cube)

    print("\nCube after edges:")
    print(cube)

    if parity in "yY1":
        # Yes parity
        cube.doMoves(PARITY)
    elif parity in "nN0":
        # No parity
        pass
    else:
        print(f"Unknown parity: {parity}")
        return

    print("\nCube after parity:")
    print(cube)

    for letter in corners:
        if not letter.isspace():
            doCorner(cube, letter)
            logging.info("Corner: %s\n%s", letter, cube)

    print("\nCube after corners:")
    print(cube)

    # Not implemented
    #if cube.isCanonical():
    #    print("\nSuccessfully solved")
    #else:
    #    print("\nNot solved!")

########################################

# See this page for the idea here as well as the lettering scheme:
#     https://jperm.net/bld

EDGE_SWAP = "R U R' U' R' F R2 U' R' U' R U R' F'"
PARITY = "(R U' R' U') (R U R D) (R' U' R D') (R' U2' R') U'"
CORNER_SWAP = "R U' R' U' R U R' F' R U R' U' R' F R"

# Each sticker letter maps to (next sticker, move to get there, move to get
# back).
# TODO function to automatically invert an algorithm.
# The target maps to (None, "")
edgeSetupMoves = {
    # B and M are the buffer piece; you don't swap with it
    #"B" : ___,
    #"M" : ___,

    # D is the target sticker; it needs no setup
    "D" : (None, "", ""),

    # Stickers around the left slice are one L turn to target
    "R" : ("D", "L" , "L'"),
    "X" : ("D", "L2", "L2"),
    "L" : ("D", "L'", "L" ),

    # Stickers on the bottom are one D turn to "X"
    "W" : ("X", "D" , "D'"),
    "V" : ("X", "D2", "D2"),
    "U" : ("X", "D'", "D" ),

    # Stickers on the E slice are one Dw turn from the sides of the left face
    "N" : ("R", "Dw" , "Dw'"),
    "J" : ("R", "Dw2", "Dw2"),
    "F" : ("R", "Dw'", "Dw" ),
    "H" : ("L", "Dw" , "Dw'"),
    "T" : ("L", "Dw2", "Dw2"),
    "P" : ("L", "Dw'", "Dw" ),

    # Stickers on the M slice are one Lw turn from the bottom face
    "K" : ("W", "Lw" , "Lw'"),
    "C" : ("W", "Lw2", "Lw2"),
    "Q" : ("W", "Lw'", "Lw" ),
    "I" : ("U", "Lw" , "Lw'"),
    "A" : ("U", "Lw2", "Lw2"),
    "S" : ("U", "Lw'", "Lw" ),

    # E and G can be moved to the E slice with an L turn
    "E" : ("F", "L", "L'"),
    "G" : ("H", "L", "L'"),

    # O just sucks. It's the only one that needs 4 moves to get to the target.
    "O" : ("S", "D", "D'"),
}

cornerSetupMoves = {
    # Buffer piece
    #"E" : ___,
    #"A" : ___,
    #"R" : ___,

    # Target
    "V" : (None, "", ""),

    # D turn to target
    "U" : ("V", "D" , "D'"),
    "X" : ("V", "D2", "D2"),
    "W" : ("V", "D'", "D" ),

    # R turn
    "T" : ("V", "R" , "R'"),
    "B" : ("V", "R2", "R2"),
    "J" : ("V", "R'", "R" ),

    "Q" : ("W", "R" , "R'"),
    "C" : ("W", "R2", "R2"),
    "K" : ("W", "R'", "R" ),

    # F turn
    "M" : ("V", "F" , "F'"),
    "D" : ("V", "F2", "F2"),
    "G" : ("V", "F'", "F" ),

    "P" : ("U", "F" , "F'"),
    # Could also do C -> U here
    "F" : ("U", "F'", "F" ),

    # D turn to reduce to other layer
    "S" : ("G", "D" , "D'"),
    "O" : ("G", "D2", "D2"),

    "H" : ("T", "D'", "D" ),
    "L" : ("T", "D2", "D2"),

    # FR and RF
    "I" : ("J", "F" , "F'"),
    "N" : ("M", "R'", "R" ),
}

def doEdge(cube, letter):
    setupAlg, cleanupAlg = getSetupAlgs(edgeSetupMoves, letter)
    cube.doMoves(setupAlg)
    cube.doMoves(EDGE_SWAP)
    cube.doMoves(cleanupAlg)

def doCorner(cube, letter):
    setupAlg, cleanupAlg = getSetupAlgs(cornerSetupMoves, letter)
    cube.doMoves(setupAlg)
    cube.doMoves(CORNER_SWAP)
    cube.doMoves(cleanupAlg)

def getSetupAlgs(setupMoveTable, startLetter):
    setupAlg   = []
    cleanupAlg = []
    currLetter = startLetter
    while True:
        currLetter, nextSetup, nextCleanup = setupMoveTable[currLetter]
        if currLetter is None:
            break
        setupAlg.append(nextSetup)
        cleanupAlg = [nextCleanup] + cleanupAlg
    return (setupAlg, cleanupAlg)

########################################

if __name__ == '__main__':
    main()
