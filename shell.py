#!/usr/bin/python
import sys
import cmd
from optparse import OptionParser

from binject.inject import Injector
from binject.objdump import Objdump
from binject.gdb import GDBWrapper
from binject.edit import BinaryEditor

class InjectShell(cmd.Cmd):
    prompt = "(inject) "

    def setObjdump(self, objdump):
        self.objdump = objdump

    def setEditor(self, editor):
        self.editor = editor

    def convert(self, arg, typ):
        try:
            if typ == "int":
                return int(arg)
            if typ == "hex":
                return int(arg, 16)
        except Exception, e:
            return None
        return arg

    def parseArg(self, arg, types):
        args = arg.split(" ")
        conv = []
        for j, typ in enumerate(types):
            if j < len(args):
                conv.append(self.convert(args[j], typ))
            else:
                conv.append(None)
        return conv

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

    def do_open(self, arg):
        self.editor.open()

    def do_close(self, arg):
        self.editor.close()

    def do_set(self, arg):
        [address, byte] = self.parseArg(arg, ["hex", "hex"])
        if address is not None and byte is not None:
            if self.editor.isOpen():
                self.editor.setByteInt(address, byte)
            else:
                print "Editor not open!"
        else:
            print "Wrong arguments!"

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

    def do_get(self, arg):
        [address] = self.parseArg(arg, ["hex"])
        




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
