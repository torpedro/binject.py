
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


    def injectLineSkip(self, editor, line):
        print "Skipping instructions of line... (%s)" % (line["text"])
        objdump = self._objdump
        instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

        for i, inst in enumerate(instructions):
            addr = inst.addr
            if self._isFileEditor:
                addr = objdump.getFileAddressOfInstruction(inst)

            if inst.opcode != "lea":
                print " * %s: %s\t%s\t%s" % (inst.hexaddr, ' '.join(inst.bytes), inst.opcode, inst.params)
                for j, byte in enumerate(inst.bytes):
                    editor.setByteInt(addr + j, NOP)
        

    def injectLineFault(self, editor, line):
        print "Injecting faults in instructions of line... (%s)" % (line["text"])
        objdump = self._objdump
        instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

        for i, inst in enumerate(instructions):
            addr = inst.addr
            if self._isFileEditor:
                addr = objdump.getFileAddressOfInstruction(inst)

            print " * %s: %s\t%s\t%s" % (inst.hexaddr, ' '.join(inst.bytes), inst.opcode, inst.params)
            for j, byte in enumerate(inst.bytes):
                editor.setByteInt(addr + j, HLT)


    def inject(self, outputPath=None):
        objdump = self._objdump
        editor = None

            
        if self._pid:
            editor = GDBWrapper(self._pid)
            self._isFileEditor = False
            if not self.hasRootPrivileges():
                print "Error: Need root permissions."
                sys.exit(-1)
        else:
            editor = BinaryEditor(self._binaryPath)
            self._isFileEditor = True

        print "Opening the editor..."
        editor.open()

        for line in objdump.getSourceLines():
            # skip injection: replaces the instructions with nops
            if "<inject-skip>" in line["text"]:
                self.injectLineSkip(editor, line)

            # inject faults into every instruction of line
            if "<inject-fault>" in line["text"]:
                self.injectLineFault(editor, line)


        if self._isFileEditor and outputPath:
            editor.write(outputPath)

        editor.close()
