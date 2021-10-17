from typing import Dict, List

from modules.block_tree.pending_block_tree import PendingBlockTree
from modules.objects import Block, QuorumCertificate, Transaction, VoteMsg


class BlockTree:
    def __init__(self, ledger, f: int, id: int):
        self.pending_block_tree: PendingBlockTree = PendingBlockTree()
        self.pending_votes: Dict[str, List[VoteMsg]] = {}
        self.high_qc: QuorumCertificate = None
        self.high_commit_qc: QuorumCertificate = None
        self.ledger = ledger
        self.block_size = 4
        self.f = f
        self.id = id

    def process_qc(self, qc: QuorumCertificate):
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

    def execute_and_insert(self, b: Block):
        # TODO get actual transactions and pass them into speculate
        self.ledger.speculate(b.id, b.payload)
        self.pending_block_tree.add(b)

    def process_vote(self, vote: VoteMsg):
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
    def generate_block(self, txns: List[Transaction], current_round: int):
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
                + (str(self.high_qc.vote_info.id)
                if self.high_qc
                else "") + (",".join(self.high_qc.signatures)
                if self.high_qc is not None
                else ""),
            ),
        )

        return b
