from typing import Dict, Optional, Tuple, Union

from nacl.signing import SigningKey, VerifyKey

from modules.block_tree.block_tree import BlockTree
from modules.ledger.ledger import Ledger
from modules.objects import (
    Block,
    Certificate,
    LedgerCommitInfo,
    QuorumCertificate,
    TimeoutCertificate,
    TimeoutInfo,
    TimeoutMessage,
    VoteInfo,
    VoteMsg,
)


class Safety:
    def __init__(
        self,
        private_key: Certificate,
        public_keys: Dict[int, Tuple[SigningKey, VerifyKey]],
        id,
        highest_vote_round: Optional[int] = -1,
        highest_qc_round: Optional[int] = -1,
    ) -> None:
        """

        Args:
            private_key:
            public_keys:
            id:
            highest_vote_round:
            highest_qc_round:
        """
        self.private_key = private_key
        self.public_keys = public_keys
        self.highest_vote_round = highest_vote_round
        self.highest_qc_round = highest_qc_round
        self.id = id

    """
    Procedure increase highest vote round(round)
        // commit not to vote in rounds lower than round
        highest vote round ← max{round, highest vote round}
    """

    def _increase_highest_vote_round(self, vote_round: int) -> None:
        """

        Args:
            vote_round:

        Returns:

        """
        self.highest_vote_round = max(self.highest_vote_round, vote_round)

    """
    Procedure update highest qc round(qc round)
        highest qc round ← max{qc round, highest qc round}
    """

    def _update_highest_qc_round(self, qc_round: int) -> None:
        """

        Args:
            qc_round:

        Returns:

        """
        self.highest_qc_round = max(self.highest_qc_round, qc_round)

    """
    Function consecutive(block round, round)
        return round + 1 = block round
    """

    def _is_consecutive(self, block_round: int, round: int) -> bool:
        """

        Args:
            block_round:
            round:

        Returns:

        """
        return round + 1 == block_round

    """
    Function safe to extend(block round, qc round, tc)
        return consecutive(block round, tc.round) ∧ qc round ≥ max{tc.tmo high qc rounds}
    """

    def _is_safe_to_extend(
        self, block_round: int, qc_round: int, tc: TimeoutCertificate
    ):
        """

        Args:
            block_round:
            qc_round:
            tc:

        Returns:

        """
        return self._is_consecutive(block_round, tc.round) and qc_round >= max(
            tc.tmo_high_qc_rounds
        )

    """
    Function safe to vote(block round, qc round, tc)
        if block round ≤ max{highest vote round, qc round} then
            // 1. must vote in monotonically increasing rounds
            // 2. must extend a smaller round
            return false
        // Extending qc from previous round or safe to extend due to tc
        return consecutive(block round, qc round) ∨ safe to extend(block round, qc round, tc)

    """

    def _is_safe_to_vote(
        self, block_round: int, qc_round: int, tc: TimeoutCertificate
    ) -> bool:
        """

        Args:
            block_round:
            qc_round:
            tc:

        Returns:

        """
        if block_round <= max(self.highest_vote_round, qc_round):
            return False
        return True

    """
    Function safe to timeout(round, qc round, tc)
        if qc round < highest qc round ∨ round ≤ max{highest vote round − 1, qc round} then
            // respect highest qc round and don’t timeout in a past round
            return false
        // qc or tc must allow entering the round to timeout
        return consecutive(round, qc round) ∨ consecutive(round, tc.round)
    """

    def _is_safe_to_timeout(
        self, round: int, qc_round: int, tc: TimeoutCertificate
    ) -> bool:
        """

        Args:
            round:
            qc_round:
            tc:

        Returns:

        """
        if (qc_round < self.highest_qc_round) or (
            round <= max(self.highest_vote_round - 1, qc_round)
        ):
            return False

        return (qc_round == -1 or self._is_consecutive(round, qc_round)) or (
            tc is None or self._is_consecutive(round, tc.round)
        )

    """
    Function commit state id candidate(block round, qc)
        // find the committed id in case a qc is formed in the vote round
        if consecutive(block round, qc.vote info.round) then
            return Ledger.pending state(qc.id)
        else
            return ⊥
    """

    def _commit_state_id_candidate(
        self, block_round: int, qc: QuorumCertificate, ledger: Ledger
    ) -> Union[int, None]:
        """

        Args:
            block_round:
            qc:
            ledger:

        Returns:

        """
        if self._is_consecutive(block_round, qc.vote_info_round):
            return ledger.pending_state(qc.id)

        return None

    """
    Function make vote(b, last tc)
        qc round ← b.qc.vote info.round
        if valid signatures(b, last tc) ∧ safe to vote(b.round, qc round, last tc) then
            update highest qc round(qc round) // Protect qc round
            increase highest vote round(b.round) // Don’t vote again in this (or lower) round
            
            // VoteInfo carries the potential QC info with ids and rounds of the parent QC
            vote info ←VoteInfo(
            (id, round) ← (b.id, b.round),
            (parent id, parent round) ← (b.qc.vote info.id, qc round)
            exec state id ← Ledger.pending state(b.id) )
            
            ledger commit info ←LedgerCommitInfo (
                commit state id ← commit state id candidate(b.round, b.qc),
                vote info hash ← hash(vote info) 
            )
            return VoteMsg(vote info, ledger commit info, Block-Tree.high commit qc)
        return ⊥

    """

    def make_vote(
        self,
        block: Block,
        last_tc: TimeoutCertificate,
        ledger: Ledger,
        block_tree: BlockTree,
    ) -> Union[VoteMsg, None]:
        """

        Args:
            block:
            last_tc:
            ledger:
            block_tree:

        Returns:

        """
        qc_round = block.qc.vote_info.round if block.qc else -1

        if not (
            Certificate.is_valid_signatures(block, last_tc)
            and self._is_safe_to_vote(block.round, qc_round, last_tc)
        ):
            return None

        self._update_highest_qc_round(qc_round)
        self._increase_highest_vote_round(block.round)

        vote_info: VoteInfo = VoteInfo(
            id=block.id,
            round=block.round,
            parent_id=block.qc.vote_info.id if block.qc else None,
            parent_round=qc_round,
            exec_state_id=ledger.get_pending_state(block.id),
        )

        ledger_commit_info: LedgerCommitInfo = LedgerCommitInfo(
            commit_state_id=ledger.get_committed_block(
                vote_info.parent_id
            ).commit_state_id
            if vote_info.parent_id
            else "",
            vote_info_hash=str(
                hash(vote_info.fields())
            ),  # TODO: Verify hashing done here
        )

        # TODO: Complete sender and signature for votemsg
        return VoteMsg(
            vote_info,
            ledger_commit_info,
            block_tree.high_commit_qc,
            sender=self.id,
            signature=None,
        )

    """
    Function make timeout(round, high qc, last tc)
        qc round ← high qc.vote info.round;
        if valid signatures(high qc, last tc) ∧ safe to timeout(round, qc round, last tc) then
            increase highest vote round(round) // Stop voting for round
            return TimeoutInfohround, high qci
        return ⊥

    """

    def make_timeout(
        self, round: int, high_qc: QuorumCertificate, last_tc: TimeoutCertificate
    ) -> Union[TimeoutInfo, None]:
        """

        Args:
            round:
            high_qc:
            last_tc:

        Returns:

        """
        qc_round = high_qc.vote_info.round if high_qc else -1

        if not (
            Certificate.is_valid_signatures(high_qc, last_tc)
            and self._is_safe_to_timeout(round, qc_round, last_tc)
        ):
            return None

        # self._increase_highest_vote_round(round)
        # TODO: Construct timeout info properly
        return TimeoutInfo(round, high_qc, sender=self.id, signature=None)

    def verify_tc(self, timeout_cert: TimeoutCertificate) -> bool:
        """

        Args:
            timeout_cert:

        Returns:

        """
        for (signature, id) in timeout_cert.tmo_signatures:
            if not TimeoutMessage.verify_sig_from_id(
                id, signature, self.public_keys[id][1]
            ):
                return False
        return True
