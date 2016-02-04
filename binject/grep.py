

import re
import os
import sys

def grep(path, regexString):
    regex = re.compile(regexString)
    matches = []

    for root, dirs, files in os.walk(path):

        for f in files:
            p = os.path.join(root, f)
            with open(p) as fh:
                i = 0
                for line in fh.readlines():
                    i += 1
                    match = regex.search(line)
                    if match:
                        matches.append((p, i, match))

    return matches



if __name__ == '__main__':
    print(grep(sys.argv[1], sys.argv[2]))