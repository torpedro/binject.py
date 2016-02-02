
import re
from subprocess import Popen, PIPE
from asm import Section, Symbol, Instruction


class Objdump(object):
    """docstring for Objdump"""
    def __init__(self, command="objdump"):
        super(Objdump, self).__init__()
        self._command = command

        # -d disassemble
        # -S include source
        # -F include section file offset
        # -x print all headers
        self._flags = "-dSFx"


    def loadFromFile(self, path):
        "Load the stdout that was cached into a file"

        with open(path, "r") as fh:
            self._stdout = fh.read()
            self._parseResult(self._stdout)


    def analyze(self, path, cacheFile=None):
        "Run objdump and analyze the stdout"

        proc = Popen([self._command, self._flags, path], stdout=PIPE, stderr=PIPE)
        proc.wait()
        self._stdout = proc.stdout.read()

        if cacheFile:
            self.cacheStdout(cacheFile)

        self._parseResult(self._stdout)

    def cacheStdout(self, cacheFile):
        with open(cacheFile, "w") as fh:
            fh.write(self._stdout)



    def _parseResult(self, stdout):
        lines = stdout.split("\n")
        lines = [line.strip() for line in lines]

        self._sections = {}
        self._symbols = {}
        self._instructions = {}
        self._sourceLines = []

        self._curSection = None
        self._curSymbol = None
        self._curLine = None

        for line in lines:
            if len(line.strip()) == 0: continue
            result = self._parseLine(line)

            if not result and self._curSection:
                print "[DEBUG] Unmatched: %s" % (line)


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
            self._curLine = {
                "text": line,
                "instruction_first": None,
                "instruction_last": None
            }
            self._sourceLines.append(self._curLine)
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


    def getSection(self, id):
        return self._sections[id]


    def getSymbol(self, id):
        return self._symbols[id]


    def getInstruction(self, address):
        return self._instructions[address]


    def getSourceLines(self):
        return self._sourceLines


    def getFileAddressOfInstruction(self, instruction):
        symbol = self.getSymbol(instruction.symbol)
        offset = symbol.fileOffset - symbol.startAddr

        return instruction.addr + offset






if __name__ == '__main__':
    binary = "../cpp-example/example"

    dump1 = Objdump()
    dump1.analyze(binary)
    print dump1._sections
    dump1.cacheStdout("cache.objdump")

    dump2 = Objdump()
    dump2.loadFromFile("cache.objdump")
    print dump2._sections