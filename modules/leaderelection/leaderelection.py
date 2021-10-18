import random
from typing import Dict, Optional

from modules.ledger.ledger import Ledger
from modules.objects import QuorumCertificate
from modules.pacemaker.pacemaker import Pacemaker


class Leader:
    pass


class LeaderElection:
    def __init__(
        self,
        validators: int,
        window_size: Optional[int] = 3,
        exclude_size: Optional[int] = 10,
        reputation_leaders: Optional[Dict[int, Leader]] = None,
    ) -> None:
        """

        Args:
            validators:
            window_size:
            exclude_size:
            reputation_leaders:
        """
        self.validators = validators
        self.window_size = window_size
        self.exclude_size = exclude_size
        self.reputation_leaders = {} if not reputation_leaders else None

    """Used pseudo code from paper."""

    def elect_reputation_leader(self, qc: QuorumCertificate, ledger: Ledger) -> Leader:
        """

        Args:
            qc:
            ledger:

        Returns:

        """
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

    """
    Procedure update leaders(qc)
        extended round ← qc.vote info.parent round
        qc round ← qc.vote info.round
        current round ← PaceMaker.current round
        if extended round + 1 = qc round ∧ qc round + 1 = current round then
            reputation leaders[current round + 1] ← elect reputation leader(qc)
    """

    def update_leaders(
        self, qc: QuorumCertificate, pacemaker: Pacemaker, ledger: Ledger
    ):
        """

        Args:
            qc:
            pacemaker:
            ledger:

        Returns:

        """
        extended_round = qc.vote_info.parent_round
        qc_round = qc.vote_info.round
        current_round = pacemaker.current_round

        if extended_round + 1 == qc_round and qc_round + 1 == current_round:
            self.reputation_leaders[current_round + 1] = self.elect_reputation_leader(
                qc, ledger
            )

    """
    Function get leader(round)
    if (round, leader) ∈ reputation leaders then
        return leader // Reputation-based leader
    return validators[floor(round/2) mod |validators|] // Round-robin leader (two rounds per leader)
    """

    def get_leader(self, round: int) -> int:
        """

        Args:
            round:

        Returns:

        """
        leader = self.reputation_leaders.get(round)
        if leader:
            return leader

        return (round // 2) % self.validators
