## Platform. 

### Software versions:
- To achieve platform agnostic behavior we make use of containerized platform via Docker.
    - We use a Python 3.6 base image on Debian (python:3.6-buster)
    - We install python libraries in this base image and execute that as a container.
    - The software versions are included in `requirements.txt` and are as follows.
        - pyDistAlgo==1.0.14
        - PyNaCl==1.4.0
        - scipy== 1.5.4
- The host for these containers are the following laptops
    - Windows 10 running on AMD CPU
    - MacOS running on INTEL i5
    - MacOS running on Apple-M1

## Workload generation. 
- describe your design for client workload generation, and mention which file(s)
contain the implementation.

## Timeouts. 
### Akshay fill this
- discuss your choice of timeout formulas and timeout values for clients and servers (e.g., in
function get_round_timer).

## Bugs and Limitations.

### Group activity
 - a list of all known bugs in and limitations of your code.

## Main files.
- The starting point of the code to instantiate validators and client and run test cases is present in `wrapper.da`.
- The definition of a validator is present in `validator.da`
- The definition of a client is present in `client.da`
- The definition of a validator to which faults can be injected is present in `modules/fault_injection/fault_injection.da`

## Code size. 
- (1) report the numbers of non-blank non-comment lines of code (LOC) in your system in
the following categories: algorithm, other, and total. "algorithm" is for the replica algorithm itself and
other functionality interleaved with it (logging, instrumentation, etc.). "other" is for everything that
can easily be separated from the algorithm (clients, configuration, test drivers, etc.). 
- LOC is obtained using [CLOC](https://github.com/AlDanial/cloc). 
- Rough estimate of
how much of the "algorithm" code is for the algorithm itself, and how much is for other functionality
interleaved with it.

## Language feature usage
 (for teams using Python or DistAlgo). report the numbers of list
comprehensions, dictionary comprehensions, set comprehensions, aggregations, quantifications,
await statements, and receive handlers in your code. the first two are Python features; the others are
DistAlgo features.

## Contributions. 
a list of each team member’s contributions to this submission.

## Other comments (optional).
 anything else you want us to know.
