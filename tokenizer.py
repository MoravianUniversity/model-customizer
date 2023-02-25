import _io
import io
import struct
from typing import List
import numpy as np


class Tokenizer:
    """
    splits any binary ascii file into token based on whitespace
    """

    def __init__(self, file: io.BufferedReader):
        self.partial = b''
        self.file = file
        self.buffer = bytearray(4096)
        self.tokens = []
        self.end = False

    def __load_more_tokens(self):
        """
        Loads more tokens when the list of tokens is empty
        """
        size = self.file.readinto(self.buffer)
        self.end = size == 0
        self.tokens = (self.partial + self.buffer[:size]).strip().split()
        # handle final token
        self.partial = b'' if self.end or self.buffer[size - 1:size].isspace() else self.tokens.pop()

    def next_token(self) -> bytes:
        """
        Returns the next token as a byte string
        :return: a byte string
        """
        if not self.tokens:
            self.__load_more_tokens()

        return self.tokens.pop(0)

    @property
    def has_next_token(self) -> bool:
        """
        Loads more tokens and returns false if the file has ended
        :return: True if there are more tokens, false otherwise
        """
        if self.tokens: return True
        self.__load_more_tokens()
        return not self.end


# Constants for STL files
SOLID = b'solid '
BINARY_HEADER_SIZE = 80


def stl2raw(path: str) -> np.ndarray:
    """
    Takes a path to an STL file, either ascii or binary, and outputs an array of vertexes
    :param path: the path to a stl file
    :return: a numpy array of vertices
    """
    with open(path, 'rb') as file:
        header, header_pos, is_binary = process_header(file)

        if is_binary:
            data = read_binary_stl(file, header_pos)  # Raw File with a binary STL doesn't need the header
        else:
            data = np.array(read_ascii_stl(file, header, header_pos))

        return data


def read_binary_stl(file: _io.BufferedReader, header_pos: int) -> np.ndarray:
    """
    Makes an array of vertices from a binary STL file
    :param file: the binary STL file
    :param header_pos: The length of the header
    :return: a numpy array of vertices
    """
    # Read the rest of the header
    to_read = BINARY_HEADER_SIZE - header_pos
    if len(file.read(to_read)) != to_read:
        raise Exception("Binary STL file too short")

    # Starts the numpy array with enough space for all the files
    num_tris = struct.unpack('<I', file.read(4))[0]  # index because the float comes in a tuple by itself
    data = np.empty(num_tris * 3 * 3)

    offset = 0
    for _ in range(num_tris):
        # Read a triangle (3 floats for normal, 3*3 floats for vertices, two extras that we don't use)
        floats = struct.unpack('<12fxx', file.read(4 * 3 * 4 + 2))

        # First 3 are (possibly negative) normal for the entire face
        data[offset:offset + 9] = floats[3:]
        offset += 9

    return data


def read_ascii_stl(file: _io.BufferedReader, header: bytearray, header_pos: int) -> np.ndarray:
    """
    Makes an array of vertices from an ASCII STL file
    :param file: a ASCII STL file
    :param header: the header of the file
    :param header_pos: the length of the header
    :return: a numpy array of vertices
    """

    # Deal with header
    solid_line = header[len(SOLID):header_pos]
    is_space = solid_line.find(b' ')
    solid_name = solid_line if is_space == -1 else solid_line[0:is_space]

    # Commented out because we might need it later
    # val solid_metadata = "" if space == -1 else solid_line[space + 1:]

    data = []
    tokenizer = Tokenizer(file)
    while True:
        current_token = tokenizer.next_token()
        if current_token == b'facet':
            check_next_token(tokenizer, b'normal')
            normal = read_3_floats(tokenizer)  # read but throw away

            check_next_token(tokenizer, b'outer')
            check_next_token(tokenizer, b'loop')

            read_vertex(tokenizer, data)
            read_vertex(tokenizer, data)
            read_vertex(tokenizer, data)

            check_next_token(tokenizer, b'endloop')
            check_next_token(tokenizer, b'endfacet')
        elif current_token == b'endsolid':
            print(solid_name)
            check_next_token(tokenizer, solid_name)
            break
        else:
            raise Exception('Stl file has an incorrect format')

    return np.array(data)


def process_header(file: _io.BufferedReader) -> tuple[bytearray, int, bool]:
    """
    Figures out if a STL file is ASCII or Binary by reading the header
    :param file: an STL file
    :return: the length of the header, negative if the STL file is ASCII
    """
    # Get header
    header = bytearray(BINARY_HEADER_SIZE)
    num_bytes_read = file.readinto(memoryview(header)[:len(SOLID)])

    # Test if file is shorter than a stl should be
    if num_bytes_read != len(SOLID):
        raise Exception("STL file too short")

    # Read the header if it exists, otherwise move the header_pos forward
    is_start_solid = header.startswith(SOLID)
    header_pos, is_binary = read_solid_line(file, header) if is_start_solid else (len(SOLID), True)
    return header, header_pos, is_binary


# HELPER FUNCTIONS

def read_solid_line(file: _io.BufferedReader, header: bytearray) -> tuple[int, bool]:
    """
    Checks the solid line in the heading for ascii or binary characters
    :param file: a STL file
    :param header: the header in a byte array
    :return: the length of the header, negative if the STL file is ASCII
    """
    header_pos = len(SOLID)
    is_binary = True
    while header_pos < BINARY_HEADER_SIZE:
        next_byte = file.read(1)
        if not next_byte:
            raise Exception('STL file too short')

        if next_byte in b'\n\r':
            is_binary = False
            return header_pos, is_binary  # finished reading first line of an ASCII file

        header[header_pos:header_pos + 1] = next_byte
        header_pos += 1
        if next_byte > b'~' or next_byte < b' ':
            # this means it's actually a binary file
            # NOTE: this assumes the ASCII file doesn't have Unicode (it REALLY shouldn't...)
            return header_pos, is_binary

    # This has got to be binary at this point...
    return header_pos, is_binary


def check_next_token(tokenizer: Tokenizer, correct_token: bytes):
    """
    checks a token against what it should be, if the token is bad, throw an error
    :param tokenizer: our tokenizer for the file
    :param correct_token: the token that should be next
    """
    current_token = tokenizer.next_token()
    if current_token != correct_token:
        raise Exception(f"Incorrect word in stl: {current_token}")


def read_vertex(tokenizer: Tokenizer, data: List):
    """
    Reads a vertex line in an ASCII STL file
    :param tokenizer: our tokenizer for the file
    :param data: the numpy array of vertices
    """
    check_next_token(tokenizer, b'vertex')
    data.extend(read_3_floats(tokenizer))


def read_3_floats(tokenizer: Tokenizer) -> tuple[float, float, float]:
    """
    Reads three floats from the tokenizer
    :param tokenizer: our tokenizer for the file
    :return: a tuple of the three floats read
    """
    return read_number(tokenizer), read_number(tokenizer), read_number(tokenizer)


def read_number(tokenizer: Tokenizer) -> float:
    """
    Checks if a float token is actually a float.
    :param tokenizer: our tokenizer for the file
    :return: the final float
    """
    token = tokenizer.next_token()
    try:
        return float(token)
    except ValueError:
        raise Exception(f"Incorrect number in STL: {token}")


def main():
    # with open('/Users/colemans/Courses/3d Printing/model-customizer/tests/stl_files/example_ascii.stl', 'rb') as file:
    # Tokenizer Testing
    # t = Tokenizer(file)
    #
    # while t.has_next_token:
    #     x = t.next_token()
    #     try:
    #         print(float(x))
    #     except:
    #         print(x)

    # test binary
    data = stl2raw('/Users/colemans/Courses/3d Printing/model-customizer/tests/stl_files/example_binary.stl')
    print(data.size // 9)
    print(data)

    # # test ascii
    data = stl2raw('/Users/colemans/Courses/3d Printing/model-customizer/tests/stl_files/example_ascii.stl')
    print(data.size // 9)
    print(data)


if __name__ == '__main__':
    main()
