from typing import Dict, List

from modules.block_tree.pending_block_tree import PendingBlockTree
from modules.objects import Block, QuorumCertificate, Transaction, VoteMsg


class BlockTree:
    """Block tree class."""

    def __init__(self, ledger, f: int, id: int):
        """

        Args:
            ledger:
            f:
            id:
        """
        self.pending_block_tree: PendingBlockTree = PendingBlockTree()
        self.pending_votes: Dict[str, List[VoteMsg]] = {}
        self.high_qc: QuorumCertificate = None
        self.high_commit_qc: QuorumCertificate = None
        self.ledger = ledger
        self.block_size = 4
        self.f = f
        self.id = id

    """
    Procedure process qc(qc)
        if qc.ledger commit info.commit state id 6= ⊥ then
            Ledger.commit(qc.vote info.parent id)
            pending block tree.prune(qc.vote info.parent id) // parent id becomes the new root of pending
            high commit qc ← maxround{qc, high commit qc}
        high qc ← maxround{qc, high qc}
    """

    def process_qc(self, qc: QuorumCertificate):
        """

        Args:
            qc:

        Returns:

        """
        trx_to_dq = []
        if not qc:
            return trx_to_dq
        if qc.ledger_commit_info.commit_state_id is not None and (
            self.high_commit_qc is None
            or qc.vote_info.round > self.high_commit_qc.vote_info.round
        ):
            trx_to_dq = self.ledger.commit(qc.vote_info.id, self)
            self.pending_block_tree.prune(qc.vote_info)
            self.high_commit_qc = (
                qc
                if (
                    self.high_commit_qc is None
                    or qc.vote_info.round > self.high_commit_qc.vote_info.round
                )
                else self.high_commit_qc
            )

        self.high_qc = (
            qc
            if (
                self.high_qc is None
                or qc.vote_info.round > self.high_qc.vote_info.round
            )
            else self.high_qc
        )
        return trx_to_dq

    """
    Procedure execute and insert(b)
        Ledger.speculate(b.qc.block id, b.id, b.payload)
        pending block tree.add(b)

    """

    def execute_and_insert(self, b: Block):
        """

        Args:
            b:

        Returns:

        """
        # TODO get actual transactions and pass them into speculate
        self.ledger.speculate(b.id, b.payload)
        self.pending_block_tree.add(b)

    """
    Function process vote(v)
        process qc(v.high commit qc)
        vote idx ← hash(v.ledger commit info)
        pending votes[vote idx] ← pending votes[vote idx] ∪ v.signature
        if |pending votes[vote idx]| = 2f + 1 then
            qc ←QC (
            vote info ← v.vote info,
            state id ← v.state id,
            votes ← pending votes[vote idx] )
            return qc
        return ⊥
    """

    def process_vote(self, vote: VoteMsg):
        """

        Args:
            vote:

        Returns:

        """
        dq_txns = self.process_qc(vote.high_commit_qc)
        vote_key = hash(vote.ledger_commit_info.fields())
        self.pending_votes[vote_key] = (
            self.pending_votes[vote_key] if vote_key in self.pending_votes else []
        )
        self.pending_votes[vote_key].append(vote)
        if len(self.pending_votes[vote_key]) == 2 * self.f + 1:
            # signatures = map(
            #     lambda vote_msg: vote_msg.signature, self.pending_votes[vote_key]
            # )
            signatures = []
            author_sig = ""  # TODO Add author signing mechanism
            qc = QuorumCertificate(
                vote.vote_info, vote.ledger_commit_info, signatures, self.id, author_sig
            )
            return (qc, dq_txns)
        return (None, dq_txns)

    """
    Function generate block(txns, current round)
        return Block (
        author ← u,
        round ← current round,
        payload ← txns,
        qc ← high qc,
        id ← hash(author || round || payload || qc.vote info.id || qc.signatures) )
    """

    def generate_block(self, txns: List[Transaction], current_round: int):
        """

        Args:
            txns:
            current_round:

        Returns:

        """
        commands = []
        for trans in txns:
            commands.append(trans.command)
        b = Block(
            self.id,
            current_round,
            txns,
            self.high_qc,
            hash(
                str(self.id)
                + str(current_round)
                + ",".join(commands)
                + (str(self.high_qc.vote_info.id) if self.high_qc else "")
                + (
                    ",".join(self.high_qc.signatures)
                    if self.high_qc is not None
                    else ""
                ),
            ),
        )

        return b
