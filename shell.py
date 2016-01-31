#!/usr/bin/python
import sys
import cmd
from optparse import OptionParser

from binject.inject import Injector
from binject.objdump import Objdump
from binject.gdb import GDBWrapper

class InjectShell(cmd.Cmd):
    prompt = "(inject) "

    def setObjdump(self, objdump):
        self.objdump = objdump

    def setEditor(self, editor):
        self.editor = editor

    def do_lines(self, arg):
        for j, line in enumerate(self.objdump.getSourceLines()):
            print "%.3d: %s" % (j, line["text"])

    def do_line(self, arg):
        try:
            line = objdump.getSourceLines()[int(arg)]
            instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])
            print line["text"]
            for inst in instructions:
                print inst
        except Exception, e:
            print e

    def do_set(self, arg):
        args = arg.split(" ")
        try:
            address = int(args[0], 16)
            byte = int(args[1], 16)
            self.editor.open()
            self.editor.setByteInt(address, byte)
            self.editor.close()
        except Exception, e:
            print e

    def do_setr(self, arg):
        args = arg.split(" ")
        try:
            addrstart = int(args[0], 16)
            addrend = int(args[1], 16)
            byte = int(args[2], 16)
            self.editor.open()

            while addrstart <= addrend:
                self.editor.setByteInt(addrstart, byte)
                addrstart += 1

            self.editor.close()
        except Exception, e:
            print e



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--pid", dest="pid")
    parser.add_option("-b", "--binary", dest="binary")
    parser.add_option("-o", "--output", dest="output", default="injected")
    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(-1)

    binaryPath = args[0]

    objdump = Objdump()
    objdump.analyze(binaryPath)


    editor = None
    if options.pid:
        editor = GDBWrapper(options.pid)
    else:
        editor = BinaryEditor(binaryPath)


    shell = InjectShell()
    shell.setObjdump(objdump)
    shell.setEditor(editor)
    shell.cmdloop()
