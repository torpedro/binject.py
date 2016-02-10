# binject.py (Binary/Assembly Injector)

This tool is used to mark specific lines in C or C++ source code
at which faults will be injected into the compiled binary.

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
(binject) setEditMode binary
(binject) analyzeBinary cpp-example/example
(binject) setTarget cpp-example/example
(binject) setSourcesPath cpp-example/
(binject) extractHooks

# inspect
(binject) hooks           # list hooks
(binject) hook 1          # look at the instructions of hook #1
(binject) hook 2          # look at the instructions of hook #2

# inject
(binject) open
(binject) injectSkipAt hook 1
(binject) injectFaultAt hook 2
(binject) saveBinary cpp-example/injected
```

