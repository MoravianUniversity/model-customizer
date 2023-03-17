from tokenizer import Tokenizer
import _io
import struct
from typing import List, Tuple, Dict
import numpy as np
from itertools import chain

# Constants for STL files
BINARY_HEADER_SIZE = 80
SOLID = b'solid '


def write_raw_file(vertices, indices):
    with open('moravian_star_2.vao', 'wb') as f:
        f.write(struct.pack('>I', len(vertices)))  # number of vertices
        f.write(struct.pack('>I', len(indices)))  # number of indices

        # Gets the
        np_vertices = np.fromiter(chain.from_iterable(vertices.keys()), '>f4', len(vertices) * 3)

        f.write(np_vertices.tobytes())
        f.write(np.array(indices, '>u2').tobytes())


def stl2raw(path: str) -> (Dict, List):
    """
    Takes a path to an STL file, either ascii or binary, and create a vao file
    :param path: the path to a stl file
    :return: a numpy array of vertices
    """
    with open(path, 'rb') as file:
        header, header_pos, is_binary = process_header(file)

        if is_binary:
            vertices, indices = read_binary_stl(file, header_pos)  # Raw File with a binary STL doesn't need the header
        else:
            vertices, indices = read_ascii_stl(file, header, header_pos)

        write_raw_file(vertices, indices)

        return vertices, indices


def read_binary_stl(file: _io.BufferedReader, header_pos: int) -> (Dict, List):
    """
    Makes an array of vertices from a binary STL file
    :param file: the binary STL file
    :param header_pos: The length of the header
    :return: a dict of vertices to their index and a list of indices
    """
    # Read the rest of the header
    to_read = BINARY_HEADER_SIZE - header_pos
    if len(file.read(to_read)) != to_read:
        raise Exception("Binary STL file too short")

    # Starts the numpy array with enough space for all the files
    num_tris = struct.unpack('<I', file.read(4))[0]  # index because the float comes in a tuple by itself
    vertices = {}
    indices = []
    for _ in range(num_tris):
        # Read a triangle (3 floats for normal, 3*3 floats for vertices, two extras that we don't use)
        floats = struct.unpack('<12fxx', file.read(4 * 3 * 4 + 2))

        # First 3 are (possibly negative) normal for the entire face
        indices.extend(
            # Linter error because python doesn't know this slice is the correct type
            add_vertex_to_ibo(vertices, floats[3 + i * 3:6 + i * 3])
            for i in range(3)
        )

    return vertices, indices


def read_ascii_stl(file: _io.BufferedReader, header: bytearray, header_pos: int) -> (Dict, List):
    """
    Makes an array of vertices from an ASCII STL file
    :param file: a ASCII STL file
    :param header: the header of the file
    :param header_pos: the length of the header
    :return: a dict of vertices to their index and a list of indices
    """

    # Deal with header
    solid_line = header[len(SOLID):header_pos]
    is_space = solid_line.find(b' ')
    solid_name = solid_line if is_space == -1 else solid_line[0:is_space]

    # Commented out because we might need it later
    # val solid_metadata = "" if space == -1 else solid_line[space + 1:]

    indices = []
    vertices = {}
    tokenizer = Tokenizer(file)
    while True:
        current_token = tokenizer.next_token()
        if current_token == b'facet':
            check_next_token(tokenizer, b'normal')
            normal = read_3_floats(tokenizer)  # read but throw away

            check_next_token(tokenizer, b'outer')
            check_next_token(tokenizer, b'loop')

            read_vertex(tokenizer, indices, vertices)
            read_vertex(tokenizer, indices, vertices)
            read_vertex(tokenizer, indices, vertices)

            check_next_token(tokenizer, b'endloop')
            check_next_token(tokenizer, b'endfacet')
        elif current_token == b'endsolid':
            check_next_token(tokenizer, solid_name)
            break
        else:
            raise Exception('Stl file has an incorrect format')

    return vertices, indices


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


def add_vertex_to_ibo(indices: dict, vertex: Tuple[float, float, float]) -> int:
    """
    Adds a vertex to the ibo if it doesn't already exist
    :param indices: a dict of vertices to index numbers
    :param vertex: a tuple of 3 floats
    :return: the index to be added to the list of indices
    """
    index = indices.get(vertex)
    if index is None:
        indices[vertex] = index = len(indices)
    return index


# HELPER FUNCTIONS

def check_next_token(tokenizer: Tokenizer, correct_token: bytes):
    """
    checks a token against what it should be, if the token is bad, throw an error
    :param tokenizer: our tokenizer for the file
    :param correct_token: the token that should be next
    """
    current_token = tokenizer.next_token()
    if current_token != correct_token:
        raise Exception(f"Incorrect word in stl: {current_token}")


def read_vertex(tokenizer: Tokenizer, indices: List, vertices: Dict):
    """
    Reads a vertex line in an ASCII STL file and adds to the ibo
    :param vertices: a dict of vertices to indices
    :param tokenizer: our tokenizer for the file
    :param indices: the array of indices
    """
    check_next_token(tokenizer, b'vertex')
    vertex = read_3_floats(tokenizer)
    indices.append(add_vertex_to_ibo(vertices, vertex))


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


def gen_bounding_box(vertices):
    # all_vertices = vertices.keys
    # first_vertex = all_vertices.pop()
    #
    # x_min = first_vertex[0]; x_max = first_vertex[0]
    # y_min = first_vertex[1]; y_max = first_vertex[1]
    # z_min = first_vertex[2]; z_max = first_vertex[2]
    #
    # for vertex in all_vertices
    #     x_min = max

    x, y, z = next(iter(vertices))
    max_x = min_x = x
    max_y = min_y = y
    max_z = min_z = z

    for x, y, z in vertices:
        if x < min_x:
            min_x = x
        elif x > max_x:
            max_x = x

        if y < min_y:
            min_y = y
        elif y > max_y:
            max_y = y

        if z < min_z:
            min_z = z
        elif z > max_z:
            max_z = z

    return max_x - min_x, max_y - min_y, max_z - min_z


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
    # indices, vertices = stl2raw('/Users/colemans/Courses/3d Printing/model-customizer/tests/stl_files/example_binary.stl')
    # print(indices)
    # print(vertices)

    # test ascii
    # indices, vertices = stl2raw(
    #     '/Users/colemans/Courses/3d Printing/model-customizer/tests/stl_files/example_ascii.stl')
    # print(indices)
    # print(vertices)

    vertices, _ = stl2raw('/Users/colemans/Courses/3d Printing/model-customizer/tests/stl_files/MoCo Star 2.stl')
    print(gen_bounding_box(vertices))


if __name__ == '__main__':
    main()
