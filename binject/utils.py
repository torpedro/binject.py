
import os

def userHasRoot():
    return os.geteuid() == 0


