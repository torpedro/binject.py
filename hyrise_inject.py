#!/usr/bin/python

from sys import argv

from binject.inject import AutoInjector

def injectHyriseDemo(objdump_path, hyrise_binary, hyrise_src_path):

    inj = AutoInjector()

    # init
    inj.loadAnalysis(objdump_path)
    inj.setSourcePath(hyrise_src_path)
    inj.setTarget(hyrise_binary)
    inj.setEditMode("binary")

    # edit
    inj.openEditor()

    hooks = inj.extractHooks()
    for i, hook in enumerate(hooks):    
        inj.injectHook(hook)
        print "%.2d at %s:%d" % (i, hook[0]["file"], hook[0]["lineno"])
        inj.writeBinary("injected-%d" % (i))
        inj.resetHook(hook)

    
    inj.closeEditor()



if __name__ == '__main__':
    # ./hyrise_inject.py ../hyrise.git/src ../hyrise.git/hyrise-objdump-dlFx ../hyrise.git/build/hyrise-server_debug

    # dump created with -dlFx
    
    hyrise_src_path = argv[1]
    objdump_path = argv[2]
    hyrise_binary = argv[3]

    injectHyriseDemo(objdump_path, hyrise_binary, hyrise_src_path)







