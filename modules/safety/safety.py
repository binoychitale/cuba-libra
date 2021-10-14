from typing import List, Optional, Union

from modules.block_tree.block_tree import BlockTree
from modules.ledger.ledger import Ledger
from modules.objects import (
    Block,
    Certificate,
    LedgerCommitInfo,
    QuorumCertificate,
    TimeoutCertificate,
    TimeoutInfo,
    VoteInfo,
    VoteMsg,
)


class Safety:
    def __init__(
        self,
        private_key: Certificate,
        public_keys: List[Certificate],
        id,
        highest_vote_round: Optional[int] = -1,
        highest_qc_round: Optional[int] = -1,
    ) -> None:
        self.private_key = private_key
        self.public_keys = public_keys
        self.highest_vote_round = highest_vote_round
        self.highest_qc_round = highest_qc_round
        self.id = id

    def _increase_highest_vote_round(self, vote_round: int) -> None:
        self.highest_vote_round = max(self.highest_vote_round, vote_round)

    def _update_highest_qc_round(self, qc_round: int) -> None:
        self.highest_qc_round = max(self.highest_qc_round, qc_round)

    def _is_consecutive(self, block_round: int, round: int) -> bool:
        return round + 1 == block_round

    def _is_safe_to_extend(
        self, block_round: int, qc_round: int, tc: TimeoutCertificate
    ):
        return self._is_consecutive(block_round, tc.round) and qc_round >= max(
            tc.tmo_high_qc_rounds
        )

    def _is_safe_to_vote(
        self, block_round: int, qc_round: int, tc: TimeoutCertificate
    ) -> bool:
        if block_round <= max(self.highest_vote_round, qc_round):
            return False
        return True

    def _is_safe_to_timeout(
        self, round: int, qc_round: int, tc: TimeoutCertificate
    ) -> bool:
        if (qc_round < self.highest_qc_round) or (
            round <= max(self.highest_vote_round - 1, qc_round)
        ):
            return False

        return (
            qc_round == -1 or self._is_consecutive(round, qc_round)
        ) or self._is_consecutive(round, tc.round)

    def _commit_state_id_candidate(
        self, block_round: int, qc: QuorumCertificate, ledger: Ledger
    ) -> Union[int, None]:

        if self._is_consecutive(block_round, qc.vote_info_round):
            return ledger.pending_state(qc.id)

        return None

    def make_vote(
        self,
        block: Block,
        last_tc: TimeoutCertificate,
        ledger: Ledger,
        block_tree: BlockTree,
    ) -> Union[VoteMsg, None]:
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

    def make_timeout(
        self, round: int, high_qc: QuorumCertificate, last_tc: TimeoutCertificate
    ) -> Union[TimeoutInfo, None]:

        qc_round = high_qc.vote_info.round if high_qc else -1

        if not (
            Certificate.is_valid_signatures(high_qc, last_tc)
            and self._is_safe_to_timeout(round, qc_round, last_tc)
        ):
            print(
                Certificate.is_valid_signatures(high_qc, last_tc),
                self._is_safe_to_timeout(round, qc_round, last_tc),
            )
            return None

        self._increase_highest_vote_round(round)
        # TODO: Construct timeout info properly
        return TimeoutInfo(round, high_qc, sender=self.id, signature=None)
