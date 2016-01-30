
import struct
import os
import stat

class AbstractByteEditor(object):
    """docstring for AbstractByteEditor"""
    def __init__(self):
        super(AbstractByteEditor, self).__init__()

    def open(self):
        raise Exception("Should be implemented by subclass")

    def close(self):
        raise Exception("Should be implemented by subclass")

    def setByteInt(self, address, intvalue):
        raise Exception("Should be implemented by subclass")

    def setByteHex(self, address, hexvalue):
        raise Exception("Should be implemented by subclass")




class BinaryEditor(AbstractByteEditor):
    """docstring for BinaryEditor"""
    def __init__(self, path):
        super(BinaryEditor, self).__init__()
        self._path = path


    def open(self):
        self._fh = open(self._path, "rb")

        self._content = list(self._fh.read())

        # for byte in self._content:
        #   uint, = struct.unpack("<B", byte)
        #   byte = self._fh.read(1)

        self._fh.close()

    def write(self, path):
        with open(path, "wb") as fh:
            fh.write(''.join(self._content))
        
        os.chmod(path, stat.S_IRWXU | stat.S_IROTH | stat.S_IXOTH)

    def close(self):
        pass

    def setByteInt(self, address, value):
        self._content[address] = struct.pack("<B", value)

    def getByteInt(self, address):
        uint, = struct.unpack("<B", self._content[address])
        return uint

    def size(self):
        return len(self._content)
        