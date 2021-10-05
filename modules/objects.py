from typing import Any, List


class Block:
    pass


class QuorumCertificate:
    pass


class TimeoutCertificate:

    def __init__(
        self,
        round: int,
        tmo_high_qc_rounds: List[int],
        tmo_signatures: List[Any]
    ) -> None:
        self.round = round
        self.tmo_high_qc_rounds = tmo_high_qc_rounds        
        self.tmo_signatures = tmo_signatures        


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

    def __init__(self, tmo_info: TimeoutInfo, last_round_tc: TimeoutCertificate, high_commit_qc: QuorumCertificate) -> None:
        self.tmo_info = tmo_info
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc

class LedgerCommitInfo:
    
    def __init__(
        self,
        commit_state_id: int,
        vote_info_hash: str
    ) -> None:
        self.commit_state_id = commit_state_id  # ⊥ if no commit happens when this vote is aggregated to QC
        self.vote_info_hash = vote_info_hash  # Hash of VoteMsg.vote info


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
        

class ProposalMessage:
    
    def __init__(
        self, 
        block: Block, 
        last_round_tc: TimeoutCertificate, 
        high_commit_qc: QuorumCertificate,
        signature: Any
        ) -> None:
        
        self.block = block
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc
        self.signature = signature  # TODO: signu(block.id);

class Certificate:

    def __init__(self) -> None:
        pass

    @staticmethod
    def is_valid_signatures(block: Block, certificate: TimeoutCertificate) -> bool:
        # TODO: Complete
        return False
