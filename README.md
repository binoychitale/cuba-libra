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
### Akshay fill this
- discuss your choice of timeout formulas and timeout values for clients and servers (e.g., in
function get_round_timer).

## Bugs and Limitations.
- QC validation is currently not supported. (The system does not
currently support validating each voters signature in the QC)
- Retransmission of requests from the client is not supported
- Syncing up of lagging replicas is not supported
- Re-transmission of timeout(and other) lost messages is not supported.
The system simply times out and moves to the next round (which is still correct behaviour)


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
    -   cloc|github.com/AlDanial/cloc v 1.81  T=0.01 s (1746.5 files/s, 251291.5 lines/s)
        --- | ---

        Language|files|blank|comment|code
        :-------|-------:|-------:|-------:|-------:
        Python|14|437|766|1245
        DAL|4|76|0|571
        Markdown|4|115|0|489
        TOML|1|1|1|17
        JSON|1|0|0|14
        Bourne Shell|1|0|0|6
        Dockerfile|1|0|0|3
        SUM:|26|629|767|2345
- Code size: Algorithm
    - ```bash
        find modules/ ! -name 'fault_injection.da' -type f -exec cloc --md {} +
       ```
    - cloc|github.com/AlDanial/cloc v 1.81  T=0.01 s (1158.4 files/s, 219882.7 lines/s)
        --- | ---

        Language|files|blank|comment|code
        :-------|-------:|-------:|-------:|-------:
        Python|11|408|763|917
        SUM:|11|408|763|917
- Code size: Others
    - ```bash
         cloc --md wrapper.da validator.da modules/fault_injection/fault_injection.da client.da modules/objects.py
       ```
    - cloc|github.com/AlDanial/cloc v 1.81  T=0.01 s (801.4 files/s, 225358.9 lines/s)
        --- | ---

        Language|files|blank|comment|code
        :-------|-------:|-------:|-------:|-------:
        DAL|4|76|0|571
        Python|1|140|304|315
        SUM:|5|216|304|886

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
- Akshay Somaiyaji(SBU ID: 113322316)
- Rakshith Raj(SBU ID: 113167737)
- Binoy Chitale(SBU ID: 113140721)

## Contributions.

|   Module              |   Authors     
|   :-------            |   -------:    
|   Mempool             |   Akshay Somayaji
|   Leader Election     |   Akshay Somayaji
|   Client              |   Akshay Somayaji
|   Dockerfile          |   Akshay Somayaji
|   Block Tree          |   Binoy Chitale           
|   Ledger              |   Binoy Chitale
|   Pacemaker           |   Binoy Chiltale
|   Fault Injection     |   Binoy Chitale           
|   Main                |   Rakshith Raj
|   Safety              |   Rakshith Raj
|   Objects             |   Rakshith Raj 
|   Wrapper             |   Rakshith Raj
|   Validator           |   Akshay Somayaji, Binoy Chiltale, Rakshith Raj

