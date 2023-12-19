import numpy as np

class Cubie:
    def __init__(self, faces='rgbwoy'):
        self.faces=faces
        self.orientation=0

def rot2cubie(rot :int):
    # 6*TOP + Front
    rot = int(rot)
    colors = 'roybgw'
    top = rot // 6
    bot = (top + 3)%6
    rest = [color for color in colors if color not in (colors[top],colors[bot])]
    start = rot % 6
    return ''.join([colors[top]] + \
            [color for color in (rest[start:] + rest[0:start])] + \
            [colors[bot]])


class Cube:
    def __init__(self):
        self.cube = np.zeros(shape=(3,3,3))

    def __repr__(self):
        rep = ''
        # Top
        for row in self.cube[:, :,0]:
            rep+=' '*7
            for cubie in row:
                rep += rot2cubie(cubie)[0]
            rep +='\n'

        rep +='\n'

        # Left Front Right Back
        a = (np.reshape(list(zip(self.cube[:, 0, :], self.cube[0, :, :],
                        self.cube[:, -1, :], self.cube[-1, :, :])), newshape=(3,4,3)))
        for rows in a:
            for (i,row) in enumerate(rows):
                for cubie in row:
                    rep += rot2cubie(cubie)[i+1]
                rep += ' '*4
            rep += '\n'

        rep +='\n'
        #Bottom
        for row in self.cube[:, :,0]:
            rep+=' '*7
            for cubie in row:
                rep += rot2cubie(cubie)[5]
            rep +='\n'

        return rep


    def front_rotate(self):
        self.cube[0,:,:] = np.rot90(self.cube[0,:,:])


if __name__=='__main__':
    print(rot2cubie(0))
    print(Cube())
