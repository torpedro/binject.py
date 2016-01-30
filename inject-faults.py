#!/usr/bin/python
import sys
from optparse import OptionParser

from binject.objdump import Objdump
from binject.edit import BinaryEditor


if __name__ == '__main__':

    parser = OptionParser()
    # parser.add_option("-s", "--server", dest="server", default="localhost")
    # parser.add_option("-p", "--port", dest="port", default=5000)
    (options, args) = parser.parse_args()

    if len(args) > 0:
        binaryPath = args[0]
    else:
        parser.print_help()
        sys.exit(-1)

    NOP = int("90", 16)

    print "Analyzing the binary... (%s)" % (binaryPath)

    objdump = Objdump("gobjdump")
    objdump.analyze(binaryPath)

    print "Opening the binary... (%s)" % (binaryPath)
    editor = BinaryEditor(binaryPath)
    editor.read()
    print "Size: %d byte" % (editor.size())

    binidx = 0

    for line in objdump._sourceLines:

        # skip injection: replaces the instructions with nops
        if "<inject-skip>" in line["line"]:
            print "\nSkip line: %s\n" % (line["line"])

            instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

            for i, inst in enumerate(instructions):
                fileaddr = objdump.getFileAddressOfInstruction(inst)
                bytes = inst["bytes"]


                if inst["opcode"] != "lea":
                    print "[SKIP] %s:\t%s\t%s\t%s" % (inst["hexaddr"], inst["opcode"], inst["params"], ' '.join(inst["bytes"]))
                    for j in range(len(bytes)):
                        editor.setByteInt(fileaddr + j, NOP)


        # inject faults into every instruction of line
        if "<inject-fault>" in line["line"]:
            print "\nFault line: %s\n" % (line["line"])

            instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])

            for i, inst in enumerate(instructions):
                fileaddr = objdump.getFileAddressOfInstruction(inst)

                print "[FAULT] %s:\t%s\t%s\t%s" % (inst["hexaddr"], inst["opcode"], inst["params"], ' '.join(inst["bytes"]))

                for j, byte in enumerate(inst["bytes"]):
                    if j == 0: continue # skip the opcode byte

                    editor.setByteInt(fileaddr + j, 255)


    editor.write("cpp-example/injected")
    # editor.write(binaryPath)
    
