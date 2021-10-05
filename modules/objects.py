from typing import Any


class Block:
    pass


class QuorumCertificate:
    pass


class TimeoutCertificate:
    pass


class TimeoutInfo:

    def __init__(
        self,
        round: int,
        high_qc: QuorumCertificate,
        sender: Any,
        signature: Any,
        ) -> None:
        
        # TODO: Construct timeout info properly
        self.round = round
        self.high_qc = high_qc
        self.sender = sender  # Added automatically when constructed
        self.signature = signature  # ← signu(round, high qc.round); // Signed automatically when constructed


class TimeoutMessage:
    def __init__(self, round_no, high_qc, sender, signature) -> None:
        self.round = round_no
        self.high_qc = high_qc
        self.sender = sender
        self.signature = signature


class LedgerCommitInfo:
    
    def __init__(
        self,
        commit_state_id: int,
        vote_info_hash: str
    ) -> None:
        commit_state_id: int  # ⊥ if no commit happens when this vote is aggregated to QC
        vote_info_hash: str  # Hash of VoteMsg.vote info


class VoteInfo:

    def __init__(
        self,
        id: int,
        round: int,
        parent_id: int,
        parent_round: int,
        exec_state_id: int,
    ) -> None:
        self.id = id
        self.round = round
        self.parent_id = parent_id
        self.parent_round = parent_round
        self.exec_state_id = exec_state_id


class VoteMsg:
    
    def __init__(
        self,
        vote_info: VoteInfo,  # A VoteInfo record
        ledger_commit_info: LedgerCommitInfo,  # Speculated ledger info
        high_commit_qc: QuorumCertificate,
        sender: Any,  # sender ← u; // Added automatically when constructed
        signature: Any,  # signature ← signu(ledger commit info); // Signed automatically when constructed
    ) -> None:
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.high_commit_qc = high_commit_qc
        self.sender = sender
        self.signature = signature
        
    
    vote_info: VoteInfo  # A VoteInfo record
    ledger_commit_info: LedgerCommitInfo  # Speculated ledger info
    high_commit_qc: QuorumCertificate
    # sender ← u; // Added automatically when constructed
    # signature ← signu(ledger commit info); // Signed automatically when constructed
    pass

class Certificate:

    @staticmethod
    def is_valid_signatures(block: Block, certificate: TimeoutCertificate) -> bool:
        # TODO: Complete
        return False
