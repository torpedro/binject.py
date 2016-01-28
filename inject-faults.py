
from binpy.objdump import Objdump

if __name__ == '__main__':
    binaryPath = "cpp-example/example"

    objdump = Objdump("gobjdump")

    objdump.analyze(binaryPath)

    # main = objdump.getFunctionByName("main")
    # print main
    # instructions = objdump.getInstructionsOfRange(main["instruction_first"], main["instruction_last"])
    # for i in instructions:
    # 	print i

    for line in objdump._sourceLines:
        if "<inject-fault>" in line["line"]:
            print line["line"]
            instructions = objdump.getInstructionsOfRange(line["instruction_first"], line["instruction_last"])
            # TODO: inject fault now
            for i in instructions:
                print "\t", i["hexaddr"], i["inst"]




