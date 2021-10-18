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
Describe your design for client workload generation, and mention which file(s)
contain the implementation.

Our client workloads and validator count are set in the file `modules/objects.py`.
An example specification is listed below, taken from the objects.py file.
```
// For the first run, use 4 validators and 10 clients
n_validators = [4, 10]
n_clients = [10, 2]
```

We can also specify failures to be induced in these workloads
in the `failure_cases` object of `modules/objects.py`

Example failure:
```
{
    // Failure description
    "msg": "Majority fail: Validator vote delay",
    // Failures that will apply
    "rules": FailureConfig(
        failures=[
            Failure(
                src="_",
                dest="leader",
                msg_type=MsgType.Vote,
                round=1,
                prob=1,
                fail_type=FailType.Delay,
                val=7,
                attr=None,
            )
        ],
        seed=0
    )
}
```
## Timeouts.
- We tested our consensus system over multiple successful runs using different number of transactions (1 - 1000) to commit in every run, and with varying block sizes. We found all round times to be in the range of 10 - 750ms, with the median round time to be around 100ms. We have therefore assumed a configurable GST of 500ms, and set the round timeout time to be 10 * GST in the get_round_timer() to avoid unnecessary timeouts, unless induced by our fault injection testing.

## Bugs and Limitations.

### Group activity
 - a list of all known bugs in and limitations of your code.

## Main files.
- The starting point of the code to instantiate validators and client and run test cases is present in `wrapper.da`.
- The definition of a validator is present in `validator.da`
- The definition of a client is present in `client.da`
- The definition of a validator to which faults can be injected is present in `modules/fault_injection/fault_injection.da`

## Code size. 
- Code size: Overall
    - ```bash
        cloc <project_folder> --md
       ```
    | -   cloc | github.com/AlDanial/cloc v 1.81  T=0.01 s (1964.7 files/s, 192127.4 lines/s) |
    | -------- | ---------------------------------------------------------------------------- |

        | Language     |    files |    blank |  comment |     code |
        | :----------- | -------: | -------: | -------: | -------: |
        | Python       |       14 |      226 |      164 |     1251 |
        | DAL          |        4 |       59 |        1 |      503 |
        | Markdown     |        2 |       22 |        0 |       79 |
        | TOML         |        1 |        1 |        1 |       17 |
        | JSON         |        1 |        0 |        0 |       14 |
        | Bourne Shell |        1 |        0 |        0 |        6 |
        | Dockerfile   |        1 |        0 |        0 |        3 |
        | --------     | -------- | -------- | -------- | -------- |
        | SUM:         |       24 |      308 |      166 |     1873 |
- Code size: Algorithm
    - ```bash
        cloc <project_folder>/modules --md
       ```
    | - cloc | github.com/AlDanial/cloc v 1.81  T=0.01 s (1438.0 files/s, 165610.4 lines/s) |
    | ------ | ---------------------------------------------------------------------------- |

        | Language |    files |    blank |  comment |     code |
        | :------- | -------: | -------: | -------: | -------: |
        | Python   |       11 |      196 |      161 |      932 |
        | DAL      |        1 |        8 |        0 |       85 |
        | -------- | -------- | -------- | -------- | -------- |
        | SUM:     |       12 |      204 |      161 |     1017 |
- Code size: Others
    - ```bash
        cloc <project_folder>/modules --md
       ```
    | - cloc | github.com/AlDanial/cloc v 1.81  T=0.01 s (1303.4 files/s, 168300.0 lines/s) |
    | ------ | ---------------------------------------------------------------------------- |

        | Language     |    files |    blank |  comment |     code |
        | :----------- | -------: | -------: | -------: | -------: |
        | DAL          |        3 |       51 |        1 |      418 |
        | Python       |        2 |       84 |      128 |      323 |
        | TOML         |        1 |        1 |        1 |       17 |
        | Bourne Shell |        1 |        0 |        0 |        6 |
        | Dockerfile   |        1 |        0 |        0 |        3 |
        | --------     | -------- | -------- | -------- | -------- |
        | SUM:         |        8 |      136 |      130 |      767 |

## Language feature usage
 - These are computed using simple searches in the IDE. Hence they provide only approximations.
 - Python features
    - List comprehensions: ~8
    - Dict comprehensions: ~8
    - Set comprehensions: 0
 - DistAlgo features:
    - Aggregations: 0
    - Quantifications: 0
    - Await statements: 3
    - Receive statements: 2
    - Receive handlers: 8

## Contributors
- Akshay Somayaji(SBU ID: 113322316)
- Rakshith Raj(SBU ID: 113167737)
- Binoy Chitale(SBU ID: 113140721)

## Contributions.

| Module          |                                      Authors |
| :-------------- | -------------------------------------------: |
| Mempool         |                              Akshay Somayaji |
| Leader Election |                              Akshay Somayaji |
| Client          |                              Akshay Somayaji |
| Dockerfile      |                              Akshay Somayaji |
| Block Tree      |                                Binoy Chitale |
| Ledger          |                                Binoy Chitale |
| Pacemaker       |                                Binoy Chitale |
| Fault Injection |                                Binoy Chitale |
| Main            |                                 Rakshith Raj |
| Safety          |                                 Rakshith Raj |
| Objects         |                                 Rakshith Raj |
| Wrapper         |                                 Rakshith Raj |
| Validator       | Akshay Somayaji, Binoy Chitale, Rakshith Raj |

## Other comments (optional).
 
- <anything else you want us to know.>
