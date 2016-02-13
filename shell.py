#!/usr/bin/python
import os
import sys
import cmd
import time
from optparse import OptionParser

from binject.utils import userHasRoot
from binject.inject import AutoInjector

class InjectShell(cmd.Cmd):
    # Color Escape Sequences
    # http://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x329.html
    prompt = "\x1b[1;34m(binject)\x1b[0m " # highlight color

    def __init__(self):
        cmd.Cmd.__init__(self)

        self.injector = AutoInjector()

        if userHasRoot():
            self.stdout.write("Mode: process\n")
            self.injector.setEditMode("process")
        else:
            self.stdout.write("Mode: binary\n")
            self.injector.setEditMode("binary")

        self.doPrintResult = True

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
    def do_extractHooks(self, arg):
        "Usage: extractHooks path/to/src/"
        [path] = self.parseArgs(arg, ["str"])

        if path and os.path.exists(path):
            if self.injector.objdump:
                self.injector.setSourcePath(path)
                self.hooks = self.injector.extractHooks()
                self.do_hooks("")
                return True
            else:
                self.stdout.write("Needs to analyze a binary first\n")
                return False
        else:
            self.do_help("extractHooks")
            return False

    def do_hooks(self, arg):
        for i, hook in enumerate(self.hooks):
            lineObj, typ, lineText = hook
            self.stdout.write("%.2d. %s:%d\t%s\n" % (i+1, lineObj["file"], lineObj["lineno"], lineText.strip()))
        return True

    def do_hook(self, arg):
        [hookIndex] = self.parseArgs(arg, ["int"])

        hook = self.hooks[hookIndex-1]
        line = hook[0]
        instructions = self.injector.objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])
        for i, inst in enumerate(instructions):
            print inst

        return True

    def do_source(self, arg):
        [fname, lineno] = self.parseArgs(arg, ["str", "int"])

        if fname:
            sources = self.injector.objdump.getSources()
            filedata = None
            for path in sources:
                if fname == os.path.basename(path):
                    filedata = sources[path]
                    break

            if lineno:
                if lineno in filedata:
                    for i, inst in enumerate(self.injector.objdump.getInstructionsOfLine(filedata[lineno])):
                        print inst
                else:
                    self.stdout.write("No instructions.\n")
                    return False
            else:
                items = filedata.iteritems()
                items = sorted(items, key=lambda x: x[0])
                for lineno, line in items:
                    print "%s:%d" % (line["file"], line["lineno"])

        return True

        
    #
    # Editor
    #
    def do_setEditMode(self, arg):
        [path] = self.parseArgs(arg, ["str"])
        self.stdout.write("Mode: %s\n" % (path))
        return self.injector.setEditMode(path)

    def do_setTarget(self, arg):
        [path] = self.parseArgs(arg, ["str"])
        return self.injector.setTarget(path)

    def do_injectFaultAt(self, arg):
        """injects a fault at the given instruction or hook
        e.g. injectFaultAt hook 1
        e.g. injectFaultAt inst 4008cf
        """
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
        """injects a skip at the given instruction or hook
        e.g. injectSkipAt hook 1
        e.g. injectSkipAt inst 4008cf
        """
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

    def do_open(self, arg):
        return self.injector.openEditor()

    def do_close(self, arg):
        return self.injector.closeEditor()

    def do_saveBinary(self, arg):
        [path] = self.parseArgs(arg, ["str"])

        return self.injector.writeBinary(path)





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

            if self.doPrintResult:
                if success:
                    # green highlight
                    self.stdout.write("\x1b[1;32mdone\x1b[0m (%.2fms)\n" % (1000*(t2-t1)))
                else:
                    # red highlight
                    self.stdout.write("\x1b[1;31mfailed\x1b[0m (%.2fms)\n" % (1000*(t2-t1)))

            return False
        
    def completenames(self, text, *ignored):
        dotext = 'do_'+text
        options = [a[3:] for a in self.get_names() if a.startswith(dotext)]
        return options

    def get_names(self):
        # This method used to pull in base class attributes
        # at a time dir() didn't do it yet.
        return dir(self.__class__)

    def do_help(self, arg):
        cmd.Cmd.do_help(self, arg)
        return True

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.

        """

        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey+": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro)+"\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = raw_input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')

                cmds = [a.strip() for a in line.split("&")]
                for cmd in cmds:
                    line = self.precmd(cmd)
                    stop = self.onecmd(cmd)
                    stop = self.postcmd(stop, cmd)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass





if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", type="string", dest="file")
    (options, args) = parser.parse_args()

    shell = InjectShell()

    if options.file:
        with open(options.file, "r") as fh:
            cmds = fh.readlines()
            for cmd in [cmd.strip() for cmd in cmds]:
                if len(cmd) > 0:
                    print "%s%s" % (shell.prompt, cmd)
                    shell.onecmd(cmd)


    for cmd in args:
        print "%s%s" % (shell.prompt, cmd)
        shell.onecmd(cmd)

    shell.cmdloop()
