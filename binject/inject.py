
import os
import sys
import re

from utils import userHasRoot
from objdump import Objdump
from edit import BinaryEditor
from gdb import GDBWrapper
from x86 import *
from grep import grep


class Injector(object):
    """docstring for Injector"""
    def __init__(self):
        super(Injector, self).__init__()

        self.editMode = None # process|binary
        self.editor = None
        self.objdump = None

    #
    # Objdump
    #

    def analyze(self, binaryPath, objdumpBin="objdump"):
        self.info("Analyzing the binary... (%s)" % (binaryPath))

        self.objdump = Objdump(objdumpBin)
        self.objdump.analyze(binaryPath)
        return True

    def loadAnalysis(self, pathToDump):
        self.objdump = Objdump()
        self.objdump.loadFromFile(pathToDump)
        return True

    def saveAnalysis(self, pathToDump):
        self.objdump.cacheStdout(pathToDump)
        return True

    #
    # Editor
    #

    def setEditMode(self, mode, target=None):
        if mode not in ["binary", "process"]:
            self.error("Invalid edit mode!")
            return False

        self.editMode = mode
        
        if self.editMode == "process":
            if not userHasRoot():
                self.error("Needs to be root!")
                return False

        if target:
            self.target = target
        return True

    def setTarget(self, target):
        self.target = target
        return True

    def openEditor(self):
        if self.editMode == "process":
            if not userHasRoot():
                self.error("Needs to be root!")
                return False

            self.editor = GDBWrapper(self.target)
            self._isFileEditor = False
        elif self.editMode == "binary":
            self.editor = BinaryEditor(self.target)
            self._isFileEditor = True
        else:
            self.error("Edit mode not set correctly!")
            return False

        self.editor.open()
        return self.editor is not None

    def closeEditor(self):
        if not self.checkEditor(): return False

        self.editor.close()
        self.editor = None
        return True

    def writeBinary(self, path):
        if not self.checkEditor(): return False

        self.editor.write(path)
        return True


    #
    # Injection
    #
    def checkEditor(self):
        if not self.editor or not self.editor.isOpen():
            self.error("Editor is not open!")
            return False
        return True


    def resetInstruction(self, inst):
        if not self.checkEditor(): return False

        self.info("Reset: %s: %s\t%s\t%s" % (inst.hexaddr, ' '.join(inst.bytes), inst.opcode, inst.params))
        
        addr = inst.addr
        if self._isFileEditor:
            addr = self.objdump.getFileAddressOfInstruction(inst)

        for j, byte in enumerate(inst.bytes):
            self.editor.setByteHex(addr + j, byte)

    def resetInstructionsAtLine(self, line):
        instructions = self.objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

        for i, inst in enumerate(instructions):
            self.resetInstruction(inst)



    def injectSkipAtLine(self, line):
        self.info("Skipping instructions of line... (%s:%d)" % (line["file"], line["lineno"]))

        instructions = self.objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

        for i, inst in enumerate(instructions):
            if inst.opcode != "lea":
                self.injectSkipAtInstruction(inst)
        
    def injectSkipAtInstruction(self, inst):
        "replaces all bytes in the instruction with NOP"
        if not self.checkEditor(): return False

        addr = inst.addr
        if self._isFileEditor:
            addr = self.objdump.getFileAddressOfInstruction(inst)

        self.info(" * %s: %s\t%s\t%s" % (inst.hexaddr, ' '.join(inst.bytes), inst.opcode, inst.params))
        for j, byte in enumerate(inst.bytes):
            self.editor.setByteInt(addr + j, NOP)



    def injectFaultAtLine(self, line):
        self.info("Injecting faults in instructions of line... (%s:%d)" % (line["file"], line["lineno"]))

        instructions = self.objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])
        first = instructions[0]
        self.injectFaultAtInstruction(first)

    def injectFaultAtInstruction(self, inst):
        "replaces all bytes in the instruction with HLT"
        if not self.checkEditor(): return False

        addr = inst.addr
        if self._isFileEditor:
            addr = self.objdump.getFileAddressOfInstruction(inst)

        self.info(" * %s: %s\t%s\t%s" % (inst.hexaddr, ' '.join(inst.bytes), inst.opcode, inst.params))
        for j, byte in enumerate(inst.bytes):
            self.editor.setByteInt(addr + j, HLT)


    def info(self, string):
        print "[INFO] %s" % (string)

    def error(self, string):
        print "[ERROR] %s" % (string)



class AutoInjector(Injector):

    def __init__(self):
        super(AutoInjector, self).__init__()

    def setSourcePath(self, path):
        self._path = path
        return True

    def extractHooks(self):
        matches = grep(self._path, "^.*<(inject-(.*))>.*$")

        hooks = []

        sources = self.objdump.getSources()
        for path, lineno, match in matches:
            fname = os.path.basename(path)
            line = None

            for other in sources:
                if fname == os.path.basename(other):
                    line = sources[other][lineno]
                    break  

            if line:
                hooks.append((line, match.group(2), match.group(0)))
            else:
                print "Couldn't match hook (%s)" % (matches.group(0))

        self._hooks = hooks
        return hooks


    def injectHook(self, hook):
        line, hookType = hook

        if hookType == "fault":
            self.injectFaultAtLine(line)
        elif hookType == "skip":
            self.injectSkipAtLine(line)
        else:
            print "Unknown hook type (%s)" % (hookType)

    def resetHook(self, hook):
        line, hookType = hook
        self.resetInstructionsAtLine(line)





if __name__ == '__main__':

    inj = AutoInjector()

    # init
    inj.analyze("../cpp-example/example")
    inj.setSourcePath("../cpp-example/")
    inj.setTarget("../cpp-example/example")
    inj.setEditMode("binary")

    # edit
    inj.openEditor()

    hooks = inj.extractHooks()
    for hook in hooks:
        inj.injectHook(hook)

    inj.writeBinary("injected")    
    inj.closeEditor()


