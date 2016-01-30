#!/usr/bin/python
import sys
from optparse import OptionParser

from binject.objdump import Objdump
from binject.edit import BinaryEditor
from binject.gdb import GDBWrapper


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-p", "--pid", dest="pid")
    parser.add_option("-b", "--binary", dest="binary")
    parser.add_option("-o", "--output", dest="output")
    (options, args) = parser.parse_args()


    if len(args) == 0:
        parser.print_help()
        sys.exit(-1)

    editor = None
    isFileEditor = False
    binaryPath = args[0]

    if options.pid:
        editor = GDBWrapper(options.pid)
        isFileEditor = False
    else:
        editor = BinaryEditor(binaryPath)
        isFileEditor = True


    NOP = int("90", 16)

    print "Analyzing the binary... (%s)" % (binaryPath)

    objdump = Objdump("objdump")
    objdump.analyze(binaryPath)

    print "Opening the editor..."
    editor.open()

    for line in objdump._sourceLines:

        # skip injection: replaces the instructions with nops
        if "<inject-skip>" in line["line"]:
            print "\nSkip line: %s\n" % (line["line"])

            instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

            for i, inst in enumerate(instructions):
                intaddr = inst["intaddr"]
                if isFileEditor:
                    intaddr = objdump.getFileAddressOfInstruction(inst)

                bytes = inst["bytes"]

                if inst["opcode"] != "lea":
                    print "[SKIP] %s:\t%s\t%s\t%s" % (inst["hexaddr"], inst["opcode"], inst["params"], ' '.join(inst["bytes"]))
                    for j in range(len(bytes)):
                        editor.setByteInt(intaddr + j, NOP)


        # inject faults into every instruction of line
        if "<inject-fault>" in line["line"]:
            print "\nFault line: %s\n" % (line["line"])

            instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

            for i, inst in enumerate(instructions):
                intaddr = inst["intaddr"]
                if isFileEditor:
                    intaddr = objdump.getFileAddressOfInstruction(inst)

                print "[FAULT] %s:\t%s\t%s\t%s" % (inst["hexaddr"], inst["opcode"], inst["params"], ' '.join(inst["bytes"]))

                for j, byte in enumerate(inst["bytes"]):
                    if j == 0: continue # skip the opcode byte

                    editor.setByteInt(intaddr + j, 255)

    # editor.write("cpp-example/injected")
    # editor.write(binaryPath)
    editor.close()
    
