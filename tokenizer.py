import io


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
