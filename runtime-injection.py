#!/usr/bin/python


from binject.objdump import Objdump
from binject.edit import BinaryEditor
from binject.gdb import GDBWrapper

if __name__ == '__main__':
    gdb = GDBWrapper(sys.argv[1])
    gdb.open()

    gdb.getByte("0x4008f2")
    gdb.setByteHex("0x4008f2", "00")
    gdb.setByteHex("0x4008f3", "00")
    gdb.setByteHex("0x4008f4", "00")
    gdb.getByte("0x4008f2")

    gdb.close()
    print "GDB dead!"