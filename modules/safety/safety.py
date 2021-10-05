from typing import List, Optional, Union
from modules.objects import TimeoutCertificate, Block, QuorumCertificate, VoteMsg 
from modules.ledger.ledger import Ledger

class Certificate:
    pass

class Safety:
    def __init__(
        self,
        private_key: Certificate,
        public_keys: List[Certificate],
        highest_vote_round: Optional[int]=0,
        highest_qc_round: Optional[int]=None,
        ) -> None:
        self.private_key = private_key
        self.public_keys = public_keys
        self.highest_vote_round = highest_vote_round
        self.highest_qc_round = highest_qc_round
    
    def _increase_highest_vote_round(self, round: int) -> None:
        self.highest_vote_round = max(self.highest_vote_round, round)

    def _update_highest_qc_round(self, qc_round: int) -> None:
        self.highest_qc_round = max(self.highest_qc_round, round)
    
    def _is_consecutive(self, block_round: int, round: int) -> bool:
        return round + 1 == block_round
    
    def _is_safe_to_extend(self, block_round: int, qc_round: int, tc: TimeoutCertificate):
        return (
            self._is_consecutive(block_round, tc.round) and qc_round >= max(tc.tmo_high_qc_rounds)
            )

    def _is_safe_to_vote(self, block_round: int, qc_round: int, tc: TimeoutCertificate) -> bool:
        if block_round <= max(self.highest_vote_round, qc_round):
            return False

    def _is_safe_to_timeout(self, round: int , qc_round: int, tc: TimeoutCertificate) -> bool:
        if (qc_round < self.highest_qc_round) or (round <= max(self.highest_vote_round - 1, qc_round)):
            return False

        return self._is_consecutive(round, qc_round) or self._is_consecutive(round, tc.round)    

    def _commit_state_id_candidate(self, block_round: int, qc: QuorumCertificate, ledger: Ledger) -> Union[int, None]:

        if self._is_consecutive(block_round, qc.vote_info_round):
            return ledger.pending_state(qc.id)
        
        return None

    def make_vote(self, block: Block, last_tc: TimeoutCertificate):
        qc_round = block.qc.vote_info.round