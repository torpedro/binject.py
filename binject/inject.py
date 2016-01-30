
import os
import sys

from binject.objdump import Objdump
from binject.edit import BinaryEditor
from binject.gdb import GDBWrapper
from binject.x86 import *

class Injector(object):
    """docstring for Injector"""
    def __init__(self, binaryPath, pid):
        super(Injector, self).__init__()
        self._binaryPath = binaryPath
        self._pid = pid

    def hasRootPrivileges(self):
        return os.geteuid() == 0

    def analyze(self, objdumpBin="objdump"):
        path = self._binaryPath

        print "Analyzing the binary... (%s)" % (path)
        self._objdump = Objdump(objdumpBin)
        self._objdump.analyze(path)
        
    def inject(self, outputPath=None):
        objdump = self._objdump
        editor = None
            
        if self._pid:
            editor = GDBWrapper(self._pid)
            isFileEditor = False
            if not self.hasRootPrivileges():
                print "Error: Need root permissions."
                sys.exit(-1)
        else:
            editor = BinaryEditor(self._binaryPath)
            isFileEditor = True

        print "Opening the editor..."
        editor.open()

        for line in objdump._sourceLines:
            # skip injection: replaces the instructions with nops
            if "<inject-skip>" in line["line"]:
                print "Skipping instructions of line... (%s)" % (line["line"])

                instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

                for i, inst in enumerate(instructions):
                    intaddr = inst["intaddr"]
                    if isFileEditor:
                        intaddr = objdump.getFileAddressOfInstruction(inst)

                    bytes = inst["bytes"]

                    if inst["opcode"] != "lea":
                        print " * %s:\t%s\t%s\t%s" % (inst["hexaddr"], inst["opcode"], inst["params"], ' '.join(inst["bytes"]))
                        for j in range(len(bytes)):
                            editor.setByteInt(intaddr + j, NOP)


            # inject faults into every instruction of line
            if "<inject-fault>" in line["line"]:
                print "Injecting faults in instructions of line... (%s)" % (line["line"])

                instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])
                for i, inst in enumerate(instructions):
                    intaddr = inst["intaddr"]
                    if isFileEditor:
                        intaddr = objdump.getFileAddressOfInstruction(inst)

                    print " * %s:\t%s\t%s\t%s" % (inst["hexaddr"], inst["opcode"], inst["params"], ' '.join(inst["bytes"]))
                    for j, byte in enumerate(inst["bytes"]):
                        editor.setByteInt(intaddr + j, HLT)


        if isFileEditor and outputPath:
            editor.write(outputPath)

        editor.close()
