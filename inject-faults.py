#!/usr/bin/python
import sys
from optparse import OptionParser

from binject.inject import Injector

if __name__ == '__main__':
    parser = OptionParser(usage="./inject-faults [OPTIONS] binaryPath   ")
    parser.add_option("-p", "--pid", dest="pid")
    parser.add_option("-o", "--output", dest="output", default="injected")
    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.print_help()
        sys.exit(-1)

    binaryPath = args[0]

    injector = Injector()

    injector.analyze(binaryPath)

    if options.pid:
        injector.setEditMode("process")
        injector.setTarget(options.pid)

    else:
        injector.setEditMode("binary")
        injector.setTarget(binaryPath)

    injector.openEditor()

    injector.injectSourceHooks()

    if injector.editMode == "binary" and options.output:
        injector.writeBinary(options.output)

    injector.closeEditor()
