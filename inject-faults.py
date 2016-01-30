#!/usr/bin/python
import sys
from optparse import OptionParser

from binject.inject import Injector


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

    injector = Injector(binaryPath, options.pid)
    injector.analyze()
    injector.inject(options.output)
