Describe your main test cases

For each test case, report the names of the configuration file, ledger files, and log files,
number of replicas, number of clients, number of client requests, failure scenario, any other important
configuration information, number of rounds executed, and the outcome. In this assignment, it’s sufficient
to run all processes on a single host.
Test Case Guidelines
some (probably most) test cases should involve multiple clients sending requests concurrently. it's fine to
design each client to have at most one pending request at a time, as in PBFT and Raft.
the test cases should involve all of the kinds of failures described in section 2.5 (Fault Injection), in nontrivial patterns and combinations. note that any number of validators may suffer from message loss and
delays, while at most f validators may suffer from SetAttribute failures.
some test cases should involve "chains" of failures; loosely, the idea is that a failure occurs, and then
another failure occurs before "normal operation" (a round that successfully commits a block) resumes. for
example, there should be test cases in which the leaders of multiple consecutive rounds are affected by
failures, causing the rounds to end with timeout certificates (TC) instead of quorum certificates (QC).
it's fine for most test cases to use f=1, N=4 (where N = number of replicas), but there should also be some
test cases with f=2, N=7.


## Test Report

Below we demonstrate the fault tolerance of our system
by introducing multiple kinds of failures

1. __Message Loss__
Here we simulate message loss from 1/4 validators.

The system should be able to successfully time-out the round
elect a new leader.

#### Fault configuration:
```python
FailureConfig(
    failures=[
        Failure(
            src=0,
            dest="_",
            msg_type=MsgType.Wildcard,
            round=1,
            prob=1,
            fail_type=FailType.MsgLoss,
            val=None,
            attr=None,
        )
    ],
    seed=0,
),
```

#### Output:
We end up with a consistent final ledger state:
```
00:39:24,320 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 3
Ledger state: [['hello2', 'hello5', 'hello4', 'hello0'], ['hello9', 'hello7', 'hello1', 'hello3'], ['hello6', 'hello8']]

00:39:24,337 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 2
Ledger state: [['hello2', 'hello5', 'hello4', 'hello0'], ['hello9', 'hello7', 'hello1', 'hello3'], ['hello6', 'hello8']]

00:39:24,330 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 1
Ledger state: [['hello2', 'hello5', 'hello4', 'hello0'], ['hello9', 'hello7', 'hello1', 'hello3'], ['hello6', 'hello8']]

00:39:24,314 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 0
Ledger state: [['hello2', 'hello5', 'hello4', 'hello0'], ['hello9', 'hello7', 'hello1', 'hello3'], ['hello6', 'hello8']]

```

2. __Message Delay__
Here we simulate message delay from 1/4 validators.

The system should be able to successfully time-out the round
elect a new leader (same as in the old case).
In addition, we also need to reject messages that arrive out of turn
This test case demonstrates that


#### Fault configuration:
```python
FailureConfig(
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
    seed=0,
),
```

#### Output:
We end up with a consistent final ledger state:
```
00:53:47,129 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 3
Ledger state: [['hello0', 'hello2', 'hello4', 'hello7'], ['hello1', 'hello6', 'hello3', 'hello5'], ['hello8', 'hello9']]

00:53:47,109 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 2
Ledger state: [['hello0', 'hello2', 'hello4', 'hello7'], ['hello1', 'hello6', 'hello3', 'hello5'], ['hello8', 'hello9']]

00:53:47,99 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 1
Ledger state: [['hello0', 'hello2', 'hello4', 'hello7'], ['hello1', 'hello6', 'hello3', 'hello5'], ['hello8', 'hello9']]

00:53:47,104 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 0
Ledger state: [['hello0', 'hello2', 'hello4', 'hello7'], ['hello1', 'hello6', 'hello3', 'hello5'], ['hello8', 'hello9']]
```

3. __Validator vote delay__
Here we simulate vote delay from 1/4 validators.

The system should be able to successfully time-out the round
elect a new leader .

If we fail to secure enough votes to commit, we need to advance the round
and elect a new leader


#### Fault configuration:
```python
FailureConfig(
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
    seed=0,
),
```

#### Output:
We end up with a consistent final ledger state:
```
01:16:33,110 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 3
Ledger state: [['hello0', 'hello1', 'hello6', 'hello7'], ['hello3', 'hello5', 'hello9', 'hello8'], ['hello4', 'hello2']]
Rounds: [1, 2, 3]

01:16:33,76 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 1
Ledger state: [['hello0', 'hello1', 'hello6', 'hello7'], ['hello3', 'hello5', 'hello9', 'hello8'], ['hello4', 'hello2']]
Rounds: [1, 2, 3]

01:16:33,82 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 0
Ledger state: [['hello0', 'hello1', 'hello6', 'hello7'], ['hello3', 'hello5', 'hello9', 'hello8'], ['hello4', 'hello2']]
Rounds: [1, 2, 3]

01:02:22,40 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 3
Ledger state: [['hello2', 'hello0', 'hello6', 'hello5'], ['hello1', 'hello9', 'hello8', 'hello7'], ['hello4', 'hello3']]
Rounds: [3, 4, 5]

```

4. __Chained falure: Validator proposal loss(round 1) + follower vote loss (ronud 2)__
The system should be able to successfully handle multiple sequential failures.

In order to test this we chain 2 failures together. We induce a proposal message loss
at round k, immediately followed by a vote message loss at round k+1.

The system should be able to make progress after timing out 2 consequent rounds
This test case demonstrates that.


#### Fault configuration:
```python
FailureConfig(
    failures=[
        Failure(
            src="leader",
            dest="_",
            msg_type=MsgType.Proposal,
            round=1,
            prob=1,
            fail_type=FailType.Delay,
            val=None,
            attr=None,
        ),
        Failure(
            src="_",
            dest="leader",
            msg_type=MsgType.Vote,
            round=2,
            prob=1,
            fail_type=FailType.Delay,
            val=None,
            attr=None,
        ),
    ],
    seed=0,
),
```

#### Output:
We end up with a consistent final ledger state:
```
01:02:22,40 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 3
Ledger state: [['hello2', 'hello0', 'hello6', 'hello5'], ['hello1', 'hello9', 'hello8', 'hello7'], ['hello4', 'hello3']]
Rounds: [3, 4, 5]

01:02:22,11 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 2
Ledger state: [['hello2', 'hello0', 'hello6', 'hello5'], ['hello1', 'hello9', 'hello8', 'hello7'], ['hello4', 'hello3']]
Rounds: [3, 4, 5]

01:02:22,13 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 1
Ledger state: [['hello2', 'hello0', 'hello6', 'hello5'], ['hello1', 'hello9', 'hello8', 'hello7'], ['hello4', 'hello3']]
Rounds: [3, 4, 5]

01:02:21,993 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 0
Ledger state: [['hello2', 'hello0', 'hello6', 'hello5'], ['hello1', 'hello9', 'hello8', 'hello7'], ['hello4', 'hello3']]
Rounds: [3, 4, 5]
```

5. __Invalid round number__
The system should be able to handle Byzantine faults. In this case, we
need to be able to handle an incorrect round number being advertised by one
of the validators.
In order to test this we modify the round number in one of the
validators to a large value.

The system should be able to make progress after rejecting state updates for these out-of-order rounds.

This test case demonstrates that.


#### Fault configuration:
```python
FailureConfig(
    failures=[
        Failure(
            src=1,
            dest="_",
            msg_type=MsgType.Wildcard,
            round=3,
            prob=1,
            fail_type=FailType.SetAttr,
            val=1,
            attr="round",
        ),
    ],
    seed=0,
),
```

#### Output:
We end up with a consistent final ledger state:
```
00:35:49,386 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 0
Ledger state: [['hello1', 'hello7', 'hello4', 'hello6'], ['hello3', 'hello0', 'hello8', 'hello2'], ['hello9', 'hello5']]
Rounds: [1, 2, 5]

00:35:49,387 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 1
Ledger state: [['hello1', 'hello7', 'hello4', 'hello6'], ['hello3', 'hello0', 'hello8', 'hello2'], ['hello9', 'hello5']]
Rounds: [1, 2, 5]

00:35:49,388 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 2
Ledger state: [['hello1', 'hello7', 'hello4', 'hello6'], ['hello3', 'hello0', 'hello8', 'hello2'], ['hello9', 'hello5']]
Rounds: [1, 2, 5]

00:35:49,413 - modules.fault_injection.fault_injection.ValidatorFI - OUTPUT - Received exit in Validator: 3
Ledger state: [['hello1', 'hello7', 'hello4', 'hello6'], ['hello3', 'hello0', 'hello8', 'hello2'], ['hello9', 'hello5']]
Rounds: [1, 2, 5]
```
