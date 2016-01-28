
import re
from subprocess import Popen, PIPE

class Objdump(object):
    """docstring for Objdump"""
    def __init__(self, command="objdump"):
        super(Objdump, self).__init__()
        self._command = command

        # -d disassemble
        # -S include source
        # -F include section file offset
        self._flags = "-dSF"

    def _exec(self, path):
        proc = Popen([self._command, self._flags, path], stdout=PIPE, stderr=PIPE)
        proc.wait()
        self._stdout = proc.stdout.read()


    def analyze(self, path):
        self._exec(path)

        sectionRe = re.compile(r"Disassembly of section (.*):")
        symbolRe = re.compile(r"([0-9a-f]+) \<(.*)\> (\(File Offset\: 0x([0-9a-f]+)\))?")
        instructionRe = re.compile(r"([0-9a-f]+):\t([0-9a-f][0-9a-f]( [0-9a-f][0-9a-f])*)([ ]*\t([a-z0-9]+)([ ]+(.*))?)?$")

        lines = self._stdout.split("\n")
        lines = [line.strip() for line in lines]

        self._sections = {}
        self._symbols = {}
        self._instructions = {}

        self._sourceLines = []

        curSection = None
        curSymbol = None
        curSourceLine = None

        for line in lines:
            if len(line.strip()) == 0: continue

            m = sectionRe.match(line)
            if m:
                curSection = {
                    "id": m.group(1),
                    "symbols": []
                }
                self._sections[curSection["id"]] = curSection

                # reset source line
                curSourceLine = None
                continue

            if curSection:
                m = symbolRe.match(line)
                if m:
                    curSymbol = {
                        "section": curSection["id"],
                        "id": m.group(2),
                        "vma": m.group(1),
                        "instruction_first": None,
                        "instruction_last": None,
                        "fileoffset_hex": m.group(4),
                        "fileoffset_int": int(m.group(4), 16)
                    }

                    curSection["symbols"].append(curSymbol)
                    self._symbols[curSymbol["id"]] = curSymbol
                    # reset source line
                    curSourceLine = None
                    continue

                m = instructionRe.match(line)
                if m:
                    # parse the instruction line
                    instruction = self.parseInstructionLine(line, m, curSection, curSymbol)

                    # add the instruction to the source line, if any
                    if curSourceLine:
                        curSourceLine["instruction_last"] = instruction["intaddr"]
                        if curSourceLine["instruction_first"] is None:
                            curSourceLine["instruction_first"] = instruction["intaddr"]

                    continue

                # source code line
                curSourceLine = {
                    "line": line,
                    "instruction_first": None,
                    "instruction_last": None
                }
                self._sourceLines.append(curSourceLine)
                continue

            else:
                continue

            print "[DEBUG] Unmatched: %s" % (line)


    def parseInstructionLine(self, line, match, section, symbol):
        hexaddr = match.group(1)
        intaddr = int(match.group(1), 16)
        bytestring = match.group(2).strip()
        opcode = match.group(5)
        params = match.group(7)

        instruction = {
            "section": section["id"],
            "symbol": symbol["id"],

            "hexaddr": hexaddr,
            "intaddr": intaddr,
            "bytes": bytestring.split(" "),
            "opcode": opcode,
            "params": params
        }
        self._instructions[instruction["intaddr"]] = instruction

        # add the instruction to the function that's currently looked at
        if len(section["symbols"]) > 0:
            instruction["symbol"] = section["symbols"][-1]["id"]

            f = section["symbols"][-1]
            f["instruction_last"] = intaddr

            if f["instruction_first"] is None:
                f["instruction_first"] = intaddr

        return instruction


    def getFunctionByName(self, name):
        for section in self._sections:
            for f in section["symbols"]:
                if f["name"] == name:
                    return f

    """
        * parameters are integer number (base 10)
    """
    def getInstructionsOfRange(self, addrstart, addrend):
        instructions = []
        for intaddr in self._instructions:
            if addrstart <= intaddr and intaddr <= addrend:
                instructions.append(self._instructions[intaddr])
        return instructions

    def getSection(self, id):
        return self._sections[id]

    def getSymbol(self, id):
        return self._symbols[id]

    def getFileAddressOfInstruction(self, instruction):
        symbol = self.getSymbol(instruction["symbol"])
        offset = symbol["fileoffset_int"] - symbol["instruction_first"]

        return instruction["intaddr"] + offset

