# Binary Fault Injector (C, C++)

This tool is used to mark specific lines in C or C++ source code
at which faults will be injected into the compiled binary.

## Injection Shell


### Inject into a running process

```
python shell.py

(binject) help

(binject) analyze binaryPath       # load the memory information for the executable
(binject) setEditMode process      # we want to edit a living process
(binject) setTarget 4242           # process id

(binject) showLines                # print the source lines of the application, that have hooks

(binject) injectFaultAtLine 17     # inject fault at the line (index is shown in showLines)
(binject) injectSkipAtLine 20      # skip this line

(binject) closeEditor
```


### Inject and save into a binary file

