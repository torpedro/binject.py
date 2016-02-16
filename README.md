# binject.py (Binary/Assembly Injector)

This tool is used to mark specific lines in C or C++ source code
at which faults will be injected into the compiled binary.

## Library Components

* `binject.objdump.Objdump`
  * Analyses binary files with objdump
  * Parses sections and instructions from dump
* `binject.edit.BinaryEditor`
  * Reading a binary file, modifying bytes and writing it back to disk
  * Used to inject faults into binary files
* `binject.gdb.GDBWrapper`
  * Attach to a running process using GDB
  * Can execute arbitrary gdb commands
  * Can change bytes in running processes
  * Used to inject faults into running processes

## Example: Source Code Annotated Injections

### Annotate the source code

To inject faults into specific lines of code, you should first annotate them (if possible).
There is also a way how to do it without annotations, but with annotations is recommended.

To annotate a line for fault injection, simply add a comment to the end of the line like this:

```
result += 1; // <inject-fault>
```

You can add as many of these hooks as you want.

### Inject into a binary (using the shell)

```
python shell.py

# setup
(binject) setEditMode binary                # editing a binary file (could also be editing a process)
(binject) analyzeBinary cpp-example/example # get the debug symbols from the binary
(binject) setTarget cpp-example/example     # set the binary file that will be edited
(binject) extractHooks cpp-example/         # extract the hooks from the source files in this dir

# inspect
(binject) hooks                             # list hooks
(binject) hook 1                            # look at the instructions of hook #1
(binject) hook 2                            # look at the instructions of hook #2

# inject
(binject) open                              # open the binary editor
(binject) injectSkipAt hook 1               # skip the instructions in that line
(binject) injectFaultAt hook 2              # inject a fault at the first instruction in that line
(binject) saveBinary cpp-example/injected   # save the changed binary data to a file
```

