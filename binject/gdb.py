
from time import sleep
from subprocess import Popen, PIPE, STDOUT
from threading import Thread

from edit import AbstractByteEditor


def logStdoutThread(p, gdb):
    for c in iter(lambda: p.stdout.read(1), ''):
        gdb.onStdout(c)

        

class GDBWrapper(AbstractByteEditor):
    """docstring for GDBWrapper"""
    def __init__(self, pid, gdb="gdb"):
        super(GDBWrapper, self).__init__()
        self._gdb = gdb
        self._pid = pid
        self._lines = [""]

    def onStdout(self, c):
        if len(c) > 1:
            for d in c:
                self.onStdout(d)
        else:
            if c == "\n":
                # print self._lines[-1]
                self._lines.append("")
            else:
                self._lines[-1] += c

    def writeToStdin(self, line):
        line = "%s\n" % (line)

        self.onStdout(line)
        self._p.stdin.write(line)
        self._p.stdin.flush()

    def open(self):
        p = Popen([self._gdb, "-p", str(self._pid)], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        self._p = p

        t = Thread(target=logStdoutThread, args=(p, self))
        t.start()    

        # wait for prompt
        while self._lines[-1].startswith("(gdb)") is False:
            sleep(0.1)

    def quit(self):
        self.writeToStdin("quit\n")

        self.writeToStdin("y")

    def getByte(self, address):
        self.writeToStdin("x/ubfx %s" % (address))
        # self.writeToStdin("p *(char*)%s" % (address))
        sleep(0.2)
        res = self._lines[-2]
        print "[Result] ", res
        # TODO handle

    def setByteInt(self, address, intvalue):
        self.writeToStdin("set (*(char*)%s) = %d" % (address, intvalue))

        sleep(0.2)
        res = self._lines[-2]
        print res

    def setByteHex(self, address, hexvalue):
        return self.setByteInt(address, int(hexvalue, 16))

    def wait(self):
        self._p.wait()

    def close(self):
        self.quit()
        self.wait()
