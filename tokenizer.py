import struct

import numpy as np


class Tokenizer:
    def __init__(self, file):
        self.partial = b''
        self.file = file
        self.buffer = bytearray(4096)
        self.tokens = []
        self.end = False

    def __load_more_tokens(self):
        size = self.file.readinto(self.buffer)
        self.end = size == 0
        self.tokens = (self.partial + self.buffer[:size]).strip().split()
        # handle final token
        self.partial = b'' if self.end or self.buffer[size - 1:size].isspace() else self.tokens.pop()

    def next_token(self):
        if not self.tokens:
            self.__load_more_tokens()

        return self.tokens.pop(0)

    @property
    def has_next_token(self):
        if self.tokens: return True
        self.__load_more_tokens()
        return not self.end


SOLID = b'solid'
BINARY_HEADER_SIZE = 80


def stl2raw(path):
    with open(path, 'rb') as file:
        # Get header
        header = bytearray(BINARY_HEADER_SIZE)
        read = file.read(len(SOLID))

        # Test if file is shorter than a stl should be
        if len(read) != len(SOLID):
            raise Exception("STL file too short")

        # Read the header if it exists, otherwise move the header_pos forward
        is_start_solid = SOLID == header[:len(SOLID)]
        header_pos = readSolidLine(file, header) if is_start_solid else len(SOLID)

        if header_pos < 0:
            # ASCII STL File
            solidLine = header[len(SOLID):-header_pos].decode('utf8')
            space = solidLine.index(' ')
            solidName = solidLine if space == -1 else solidLine[0:space]
            # val solidMetadata = "" if space == -1 else solidLine[space + 1:]
            data = []
            tokenizer = Tokenizer(file)
            ...
        else:
            # Binary STL File

            # Read the rest of the header
            to_read = BINARY_HEADER_SIZE - header_pos
            if len(file.read(to_read)) != to_read:
                raise Exception("Binary STL file too short")

            # Starts the numpy array and adds number of triangles(?)
            num_tris = struct.unpack('<I', file.read(4))
            data = np.array(num_tris * 3 * 3)
            offset = 0

            for _ in range(num_tris):
                # Read a triangle (3 floats for normal, 3*3 floats for vertices)
                # Last two bytes are "attribute byte count" field
                floats = struct.unpack('<12fxx', file.read(4 * 3 * 4 + 2))
            # First 3 are (possibly negative) normal for the entire face
            data[offset:offset + 9] = floats[3:]
            offset += 9
            return data


def main():
    with open('/Users/colemans/Courses/3d Printing/model-customizer/tests/stl_files/example_ascii.stl', 'rb') as file:
        # Tokenizer Testing
        # t = Tokenizer(file)
        #
        # while t.has_next_token:
        #     x = t.next_token()
        #     try:
        #         print(float(x))
        #     except:
        #         print(x)
        #
        # print(t.buffer)
        # print(t.partial)
        # print(t.tokens)
        # print(t.end)

        print(stl2raw('/Users/colemans/Courses/3d Printing/model-customizer/tests/stl_files/example_binary.stl'))


if __name__ == '__main__':
    main()
