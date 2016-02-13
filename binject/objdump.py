
import re
import os
from subprocess import Popen, PIPE
from asm import Section, Symbol, Instruction

LINE_RE = re.compile(r"^(.*):([0-9]+)$")

class Objdump(object):
    """docstring for Objdump"""
    def __init__(self, command="objdump"):
        super(Objdump, self).__init__()
        self._command = command

        # -d disassemble
        # -S include source
        # -l include file line markers
        # -F include section file offset
        # -x print all headers
        self._flags = "-dlFx"


    def loadFromFile(self, path):
        "Load the stdout that was cached into a file"

        with open(path, "r") as fh:
            self._stdout = fh.read()
            self._parseResult(self._stdout)


    def analyze(self, path, cacheFile=None):
        "Run objdump and analyze the stdout"

        if os.path.exists(path):
            proc = Popen([self._command, self._flags, path], stdout=PIPE, stderr=PIPE)
            proc.wait()
            self._stdout = proc.stdout.read()

            if cacheFile:
                self.cacheStdout(cacheFile)

            self._parseResult(self._stdout)
            return True
        else:
            return False

    def cacheStdout(self, cacheFile):
        with open(cacheFile, "w") as fh:
            fh.write(self._stdout)



    def _parseResult(self, stdout):
        lines = stdout.split("\n")
        lines = [line.strip() for line in lines]

        self._sections = {}
        self._symbols = {}
        self._instructions = {}
        self._sources = {}
        self._unmatchedLines = []

        self._curSection = None
        self._curSymbol = None
        self._curLine = None

        for line in lines:
            if len(line.strip()) == 0: continue
            result = self._parseLine(line)

            if not result:
                self._unmatchedLines.append(line)


    def _parseLine(self, line):
        # check if a new section starts
        section = Section.parseObjdumpString(line)
        if section:
            self._curSection = section
            self._sections[section.id] = section
            # reset source line
            self._curLine = None
            return section

        if self._curSection:
            # check if a new symbol starts
            symbol = Symbol.parseObjdumpString(line, self._curSection)
            if symbol:
                self._curSymbol = symbol
                self._curSection.symbols.append(self._curSymbol)
                self._symbols[self._curSymbol.id] = self._curSymbol
                # reset source line
                self._curLine = None
                return symbol

            # check if this is an instruction
            instruction = Instruction.parseObjdumpString(line, self._curSection, self._curSymbol)
            if instruction:
                self._instructions[instruction.addr] = instruction
                # add the instruction to the source line, if any
                if self._curLine:
                    self._curLine["instruction_last"] = instruction.addr
                    if self._curLine["instruction_first"] is None:
                        self._curLine["instruction_first"] = instruction.addr

                return instruction

            # source code line
            match = LINE_RE.match(line)
            if match:
                path = match.group(1)
                lineno = int(match.group(2))

                self._curLine = {
                    "file": path,
                    "lineno": lineno,
                    "instruction_first": None,
                    "instruction_last": None
                }

                if not path in self._sources:
                    self._sources[path] = {}
                if not lineno in self._sources[path]:
                    self._sources[path][lineno] = {}

                self._sources[path][lineno] = self._curLine
                return self._curLine


    def getFunctionByName(self, name):
        for section in self._sections:
            for symbol in section.symbols:
                if symbol.name == name:
                    return symbol


    def getInstructionsOfRange(self, addrstart, addrend):
        "Parameters are integer numbers (base 10)"

        instructions = []
        for addr in self._instructions:
            if addrstart <= addr and addr <= addrend:
                instructions.append(self._instructions[addr])
        return instructions

    def getInstructionsOfLine(self, line):
        return self.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

    def getSection(self, id):
        return self._sections[id]

    def getSymbol(self, id):
        return self._symbols[id]

    def getInstruction(self, address):
        if address in self._instructions:
            return self._instructions[address]
        else:
            return None

    def getSections(self):
        return self._sections

    def getSymbols(self):
        return self._symbols

    def getInstructions(self):
        return self._instructions

    def getSources(self):
        return self._sources

    def getFileAddressOfInstruction(self, instruction):
        symbol = self.getSymbol(instruction.symbol)
        offset = symbol.fileOffset - symbol.startAddr
        return instruction.addr + offset

    def getFileOffset(self):
        if len(self._symbols) > 0:
            symbol = self._symbols[self._symbols.keys()[0]]
            return symbol.startAddr - symbol.fileOffset





if __name__ == '__main__':
    binary = "../cpp-example/example"

    dump1 = Objdump()
    dump1.analyze(binary)
    print dump1.getSources()
    dump1.cacheStdout("cache.objdump")

    dump2 = Objdump()
    dump2.loadFromFile("cache.objdump")
    print dump2.getSources()

    print dump2.getFileOffset()



