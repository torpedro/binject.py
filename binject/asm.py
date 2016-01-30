
import re

class Section(object):
    regex = re.compile(r"Disassembly of section (.*):")

    def __init__(self):
        super(Section, self).__init__()
        
    @staticmethod
    def parseObjdumpString(line):
        match = Section.regex.match(line)
        if match:
            section = Section()
            section.id = match.group(1)
            section.symbols = []
            return section
        return None


class Symbol(object):
    regex = re.compile(r"([0-9a-f]+) \<(.*)\> (\(File Offset\: 0x([0-9a-f]+)\))?")

    def __init__(self):
        super(Symbol, self).__init__()

    @staticmethod
    def parseObjdumpString(line, section):
        match = Symbol.regex.match(line)
        if match:
            symbol = Symbol()
            symbol.id = match.group(2)
            symbol.vma = match.group(1)
            symbol.section = section.id
            symbol.startAddr = None
            symbol.endAddr = None
            symbol.fileOffsetHex = match.group(4)
            symbol.fileOffset = int(match.group(4), 16)
            return symbol
        return None



class Instruction(object):
    regex = re.compile(r"([0-9a-f]+):\t([0-9a-f][0-9a-f]( [0-9a-f][0-9a-f])*)([ ]*\t([a-z0-9]+)([ ]+(.*))?)?$")

    def __init__(self):
        super(Instruction, self).__init__()
        
    @staticmethod
    def parseObjdumpString(line, section, symbol):
        match = Instruction.regex.match(line)
        if match:
            hexaddr = match.group(1)
            addr = int(match.group(1), 16)
            bytestring = match.group(2).strip()
            opcode = match.group(5)
            params = match.group(7)

            instruction = Instruction()
            instruction.section = section.id
            instruction.symbol = symbol.id
            instruction.addr = addr
            instruction.hexaddr = hexaddr # string
            instruction.bytes = bytestring.split(" ")
            instruction.opcode = opcode
            instruction.params = params

            # add the instruction to the function that's currently looked at
            symbol.endAddr = addr
            if symbol.startAddr is None:
                symbol.startAddr = addr

            return instruction
        return None