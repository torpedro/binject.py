#!/usr/bin/python
import sys
import cmd
import time
from optparse import OptionParser

from binject.inject import AutoInjector

class InjectShell(cmd.Cmd):
    prompt = "(binject) "

    def __init__(self):
        cmd.Cmd.__init__(self)

        self.injector = AutoInjector()

    def convert(self, arg, typ):
        try:
            if typ == "int":
                return int(arg)
            if typ == "hex":
                return int(arg, 16)
            if typ == "str":
                return arg
        except Exception, e:
            return None
        return arg

    def parseArgs(self, arg, types):
        args = arg.split(" ")
        conv = []
        for j, typ in enumerate(types):
            if j < len(args):
                conv.append(self.convert(args[j], typ))
            else:
                conv.append(None)
        return conv

    #
    # Objdump Analysis
    #
    def do_loadAnalysis(self, arg):
        [path] = self.parseArgs(arg, ["str"])
        return self.injector.loadAnalysis(path)

    def do_analyzeBinary(self, arg):
        [path] = self.parseArgs(arg, ["str"])
        return self.injector.analyze(path)

    def do_saveAnalysis(self, arg):
        [path] = self.parseArgs(arg, ["str"])
        return self.injector.saveAnalysis(path)

    def do_instruction(self, arg):
        [address] = self.parseArgs(arg, ["hex"])
        inst = self.injector.objdump.getInstruction(address)
        print inst
        return inst is not None

    #
    # Source Code Hooks
    #
    def do_setSourcePath(self, arg):
        [path] = self.parseArgs(arg, ["str"])
        
        return self.injector.setSourcePath(path)

    def do_extractHooks(self, arg):
        self.hooks = self.injector.extractHooks()
        self.do_hooks("")
        return True

    def do_hooks(self, arg):
        for i, hook in enumerate(self.hooks):
            lineObj, typ, lineText = hook
            self.stdout.write("%.2d: %s\n" % (i+1, lineText))
        return True


    def do_hook(self, arg):
        [hookIndex] = self.parseArgs(arg, ["int"])

        hook = self.hooks[hookIndex-1]
        line = hook[0]
        instructions = self.injector.objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])
        for i, inst in enumerate(instructions):
            print inst

        return True
        
    #
    # Editor
    #
    def do_setEditMode(self, arg):
        [path] = self.parseArgs(arg, ["str"])
        return self.injector.setEditMode(path)

    def do_setTarget(self, arg):
        [path] = self.parseArgs(arg, ["str"])
        return self.injector.setTarget(path)

    def do_injectFaultAt(self, arg):
        "injects a fault at the given instruction or hook"
        [typ, address] = self.parseArgs(arg, ["str", "hex"])

        if typ == "inst":
            inst = self.injector.objdump.getInstruction(address)
            if inst:
                self.injector.injectFaultAtInstruction(inst)
                return True

        elif typ == "hook":
            hook = self.hooks[address-1]
            line = hook[0]
            self.injector.injectFaultAtLine(line)
            return True

        return False

    def do_injectSkipAt(self, arg):
        "injects a skip at the given instruction or hook"
        [typ, address] = self.parseArgs(arg, ["str", "hex"])

        if typ == "inst":
            inst = self.injector.objdump.getInstruction(address)
            if inst:
                self.injector.injectSkipAtInstruction(inst)
                return True

        elif typ == "hook":
            hook = self.hooks[address-1]
            line = hook[0]
            self.injector.injectSkipAtLine(line)
            return True

        return False

    def do_openEditor(self, arg):
        return self.injector.openEditor()

    def do_closeEditor(self, arg):
        return self.injector.closeEditor()




    "Customization of the Shell"
    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
        cmd, arg, line = self.parseline(line)
        if not line:
            return self.emptyline()
        if cmd is None:
            return self.default(line)
        self.lastcmd = line
        if line == 'EOF' :
            self.lastcmd = ''
        if cmd == '':
            return self.default(line)
        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)

            t1 = time.time()
            try:
                success = func(arg)
            except Exception, e:
                success = False
                self.stdout.write("An error occurred: %s\n" % (e))
            t2 = time.time()

            if success:
                self.stdout.write("done (%.2fms)\n" % (1000*(t2-t1)))
            else:
                self.stdout.write("failed (%.2fms)\n" % (1000*(t2-t1)))
            return False
        




if __name__ == '__main__':
    parser = OptionParser()
    (options, args) = parser.parse_args()

    shell = InjectShell()

    for arg in args:
        shell.onecmd(arg)

    shell.cmdloop()
