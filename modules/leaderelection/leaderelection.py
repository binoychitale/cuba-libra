import random
from typing import Any, Dict, List

from modules.ledger.ledger import Ledger
from modules.objects import QuorumCertificate
from modules.pacemaker.pacemaker import Pacemaker


class Leader:
    pass


class LeaderElection:
    def __init__(
        self,
        validators: int,
        # window_size: int,
        # exclude_size: int,
        # reputation_leaders: Dict[int, Leader] = {},
    ) -> None:
        self.validators = validators
        self.window_size = 10
        self.exclude_size = 3
        self.reputation_leaders = {}

    def elect_reputation_leader(self, qc: QuorumCertificate, ledger: Ledger) -> Leader:
        active_validators, last_authors = set(), set()
        current_qc = qc

        i = 0
        while i < self.window_size or len(last_authors) < self.exclude_size:
            current_block = ledger.get_committed_block(current_qc.vote_info.parent_id)
            block_author = current_block.author

            if i < self.window_size:
                active_validators = active_validators | current_qc.signatures.signers()
            if len(last_authors) < self.exclude_size:
                last_authors = last_authors | set(block_author)

            current_qc = current_block.qc
            i += 1

        active_validators = active_validators - last_authors
        # TODO: Verify seed logic
        random.seed(qc.vote_info.round)
        return random.choice(tuple(active_validators))

    def update_leaders(
        self, qc: QuorumCertificate, pacemaker: Pacemaker, ledger: Ledger
    ):
        extended_round = qc.vote_info.parent_round
        qc_round = qc.vote_info.round
        current_round = pacemaker.current_round

        if extended_round + 1 == qc_round and qc_round + 1 == current_round:
            self.reputation_leaders[current_round + 1] = self.elect_reputation_leader(
                qc, ledger
            )

    def get_leader(self, round: int) -> Leader:
        leader = self.reputation_leaders.get(round)
        if leader:
            return leader

        return (round // 2) % self.validators
