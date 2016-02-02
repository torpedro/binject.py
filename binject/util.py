
import os

def weHaveRootPrivileges(self):
    return os.geteuid() == 0