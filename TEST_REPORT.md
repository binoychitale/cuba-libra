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