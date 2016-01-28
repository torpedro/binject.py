
import struct
import os
import stat

class BinaryEditor(object):
	"""docstring for BinaryEditor"""
	def __init__(self, path):
		super(BinaryEditor, self).__init__()
		self._path = path


	def read(self):
		self._fh = open(self._path, "rb")

		self._content = list(self._fh.read())

		# for byte in self._content:
		# 	uint, = struct.unpack("<B", byte)
		# 	byte = self._fh.read(1)

		self._fh.close()

	def write(self, path):
		with open(path, "wb") as fh:
			fh.write(''.join(self._content))
		
		os.chmod(path, stat.S_IRWXU)

	def setByteInt(self, address, value):
		self._content[address] = struct.pack("<B", value)

	def getByteInt(self, address):
		uint, = struct.unpack("<B", self._content[address])
		return uint

	def size(self):
		return len(self._content)
		