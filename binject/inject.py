
import os
import sys
import re

from utils import userHasRoot
from objdump import Objdump
from edit import BinaryEditor
from gdb import GDBWrapper
from x86 import *


class Injector(object):
    """docstring for Injector"""
    def __init__(self):
        super(Injector, self).__init__()

        self.editMode = None # process|binary

    #
    # Objdump
    #

    def analyze(self, binaryPath, objdumpBin="objdump"):
        self.info("Analyzing the binary... (%s)" % (binaryPath))

        self.objdump = Objdump(objdumpBin)
        self.objdump.analyze(binaryPath)

    def loadAnalysis(self, pathToDump):
        self.objdump = Objdump()
        self.objdump.loadFromFile(pathToDump)

    def saveAnalysis(self, pathToDump):
        self.objdump.cacheStdout(pathToDump)

    #
    # Editor
    #

    def setEditMode(self, mode, target=None):
        self.editMode = mode
        if target:
            self.target = target

    def setTarget(self, target):
        self.target = target

    def openEditor(self):
        if self.editMode == "process":
            if not userHasRoot():
                self.error("Need to be root")
                return None

            self.editor = GDBWrapper(self.target)
            self._isFileEditor = False
        elif self.editMode == "binary":
            self.editor = BinaryEditor(self.target)
            self._isFileEditor = True
        else:
            self.error("Edit mode not set correctly!")
            return None

        self.editor.open()
        return self.editor

    def closeEditor(self):
        self.editor.close()

    def writeBinary(self, path):
        self.editor.write(path)


    #
    # Injection
    #

    def injectSkipAtLine(self, line):
        self.info("Skipping instructions of line... (%s)" % (line["text"]))

        instructions = self.objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

        for i, inst in enumerate(instructions):
            if inst.opcode != "lea":
                self.injectSkipAtInstruction(inst)
        
    def injectSkipAtInstruction(self, inst):
        "replaces all bytes in the instruction with NOP"

        addr = inst.addr
        if self._isFileEditor:
            addr = self.objdump.getFileAddressOfInstruction(inst)

        self.info(" * %s: %s\t%s\t%s" % (inst.hexaddr, ' '.join(inst.bytes), inst.opcode, inst.params))
        for j, byte in enumerate(inst.bytes):
            self.editor.setByteInt(addr + j, NOP)



    def injectFaultAtLine(self, line):
        self.info("Injecting faults in instructions of line... (%s)" % (line["text"]))

        instructions = self.objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

        for i, inst in enumerate(instructions):
            self.injectFaultAtInstruction(inst)

    def injectFaultAtInstruction(self, inst):
        "replaces all bytes in the instruction with HLT"

        addr = inst.addr
        if self._isFileEditor:
            addr = self.objdump.getFileAddressOfInstruction(inst)

        self.info(" * %s: %s\t%s\t%s" % (inst.hexaddr, ' '.join(inst.bytes), inst.opcode, inst.params))
        for j, byte in enumerate(inst.bytes):
            self.editor.setByteInt(addr + j, HLT)


    def injectSourceHooks(self):
        for line in self.objdump.getSourceLines():
            # skip injection: replaces the instructions with nops
            if "<inject-skip>" in line["text"]:
                self.injectSkipAtLine(line)

            # inject faults into every instruction of line
            if "<inject-fault>" in line["text"]:
                self.injectFaultAtLine(line)

    def info(self, string):
        print "[INFO] %s" % (string)

    def error(self, string):
        print "[ERROR] %s" % (string)


    def getLinesWithHooks(self):
        lines = []

        for line in self.objdump.getSourceLines():
            if "<inject" in line["text"]: # TODO: replace with regex
                lines.append(line)

        return lines












if __name__ == '__main__':
    inj = Injector()


    inj.analyze("../cpp-example/example")
    inj.openEditor()

    inj.setEditMode("binary")
    inj.setTarget("../cpp-example/example")
    inj.openEditor()

    print inj.getLinesWithHooks()

    inj.closeEditor()


