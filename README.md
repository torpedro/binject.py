# Binary Fault Injector (C, C++)

This tool is used to mark specific lines in C or C++ source code
at which faults will be injected into the compiled binary.

## Basic Usage

Mark lines at which a fault should be injected.

```
int main() {
    printf("Hello\n");
    printf("World\n"); // <inject-fault>
    printf("!\n");   
}
```

For the injection to work you have to compile your code with the debug flag `-g`.

Run the fault injector tool. This will create a copy of you binary with
seg-faults injected at the locations of the comment.

```
Usage: python inject-faults.py [OPTIONS] input-binary output-binary

python inject-faults.py /path/to/binary /path/to/faulty-binary
```


## Options

There are several options to customize how faults are injected.

### Source Code Hooks

 * `// <inject-fault>`
    
    injects the fault at the first asm instructon of this line
    
 * `// <inject-fault-last>`
    
    injects the fault at the last asm instruction of this line
    
 * `// <inject-fault-each>`
    
    injects the fault at each instruction of this line (makes only sense when using the --each option)
    
### Command Line Options

tbd

