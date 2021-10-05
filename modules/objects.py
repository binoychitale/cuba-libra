class Block:
    pass

class QuorumCertificate:
    pass

class TimeoutCertificate:
    pass

class TimeoutMessage:
    def __init__(self, round_no, high_qc, sender, signature) -> None:
        self.round = round_no
        self.high_qc = high_qc
        self.sender = sender
        self.signature = signature

class VoteInfo:
    id: int
    round: int
    parent_id: int
    parent_round: int
    exec_state_id: int


class VoteMsg:
    vote_info: VoteInfo  # A VoteInfo record
    ledger_commit_info  # Speculated ledger info
    high_commit_qc
    sender ← u; // Added automatically when constructed
    signature ← signu(ledger commit info); // Signed automatically when constructed
    pass