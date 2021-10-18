import logging
from typing import Dict, List, Tuple, Union

from modules.block_tree.block_tree import BlockTree
from modules.leaderelection.leaderelection import LeaderElection
from modules.ledger.ledger import Ledger
from modules.mempool.mempool import MemPool
from modules.objects import (
    Event,
    EventType,
    ProposalMessage,
    QuorumCertificate,
    TimeoutCertificate,
    TimeoutMessage,
    VoteMsg,
)
from modules.pacemaker.pacemaker import Pacemaker
from modules.safety.safety import Safety

logger = logging.getLogger(__name__)


class Main:
    """Main class"""

    def __init__(
        self,
        block_tree: BlockTree,
        leader_election: LeaderElection,
        pacemaker: Pacemaker,
        safety: Safety,
        ledger: Ledger,
        mempool: MemPool,
        id: int,
    ) -> None:
        """

        Args:
            block_tree:
            leader_election:
            pacemaker:
            safety:
            ledger:
            mempool:
            id:
        """
        self.block_tree: BlockTree = block_tree
        self.leader_election: LeaderElection = leader_election
        self.pacemaker: Pacemaker = pacemaker
        self.safety: Safety = safety
        self.ledger: Ledger = ledger
        self.mempool: MemPool = mempool
        self.u = None
        self.id = id
        self.round_done = False

    """
    Procedure process certificate qc(qc)
        Block-Tree.process qc(qc)
        LeaderElection.update leaders(qc)
        Pacemaker.advance round(qc.vote info.round)
    """

    def process_certificate_qc(self, qc: QuorumCertificate) -> None:
        """

        Args:
            qc:

        Returns:

        """
        trx_to_dq = self.block_tree.process_qc(qc)

        # TODO Fix this self.leader_election.update_leaders(qc, self.pacemaker, self.ledger)
        self.pacemaker.advance_round_qc(qc)

        return trx_to_dq

    """
    Procedure process proposal msg(P)
        process certificate qc(P.block.qc)
        process certificate qc(P.high commit qc)
        Pacemaker.advance round tc(P.last round tc)
        round ← Pacemaker.current round
        leader ← LeaderElection.get leader(current round)
        if P.block.round 6= round ∨ P.sender 6= leader ∨ P.block.author 6= leader then
            return
        Block-Tree.execute and insert(P) // Adds a new speculative state to the Ledger
        vote msg ← Safety.make vote(P.block, P.last round tc)
        if vote msg 6= ⊥ then
            send vote msg to LeaderElection.get leader(current round + 1)
    """

    def process_proposal_msg(
        self, proposal: ProposalMessage
    ) -> Tuple[Union[None, VoteMsg], List[str]]:
        """

        Args:
            proposal:

        Returns:

        """
        trx_to_dq = []
        if proposal.block.qc:
            trx_to_dq = self.process_certificate_qc(proposal.block.qc)
            self.process_certificate_qc(proposal.high_commit_qc)
        if proposal.last_round_tc:
            if not self.safety.verify_tc(proposal.last_round_tc):
                return (None, trx_to_dq)
            self.pacemaker.advance_round_tc(proposal.last_round_tc)

        current_round = self.pacemaker.current_round
        leader = self.leader_election.get_leader(current_round)

        if (
            proposal.block.round != current_round
            or proposal.sender_id != leader
            or proposal.block.author != leader
            or (
                len(proposal.block.payload) == 0
                and len(
                    self.block_tree.pending_block_tree.find(
                        proposal.block.qc.vote_info.id
                    ).payload
                )
                == 0
            )
        ):
            return (None, trx_to_dq)

        self.block_tree.execute_and_insert(proposal.block)
        vote_msg = self.safety.make_vote(
            proposal.block,
            proposal.last_round_tc,
            ledger=self.ledger,
            block_tree=self.block_tree,
        )

        if not vote_msg:
            return (None, trx_to_dq)

        # TODO: Capture return value and send to leader election
        # send vote_msg to LeaderElection.get_leader(round+1)
        self.pacemaker.start_timer(self.pacemaker.current_round + 1)
        return (vote_msg, trx_to_dq)

    """
    Procedure process new round event(last tc)
        if u = LeaderElection.get leader(Pacemaker.current round) then
            // Leader code: generate proposal.
            b ← Block-Tree.generate block( MemPool.get transactions(),Pacemaker.current round )
            broadcast ProposalMsghb, last tc, Block-Tree.high commit qci
    """

    def process_new_round_event(self, last_tc: TimeoutCertificate) -> ProposalMessage:
        """

        Args:
            last_tc:

        Returns:

        """
        if self.id == self.leader_election.get_leader(self.pacemaker.current_round):
            trx_id_list, transactions = self.get_transactions()
            b = self.block_tree.generate_block(
                transactions, self.pacemaker.current_round
            )

            # TODO: Fix signature
            self.block_tree.execute_and_insert(b)
            return ProposalMessage(
                b,
                last_tc,
                self.block_tree.high_commit_qc,
                signature=None,
                sender_id=self.id,
                trx_ids=trx_id_list,
            )

    """
    Procedure process timeout msg(M)
        process certificate qc(M.tmo info.high qc)
        process certificate qc(M.high commit qc)
        Pacemaker.advance round tc(M.last round tc)
        tc ← Pacemaker.process remote timeout(M)
        if tc != ⊥ then
            Pacemaker.advance round(tc)
            process new round event(tc)
    """

    def process_timeout_msg(self, timeout_message: TimeoutMessage) -> ProposalMessage:
        """

        Args:
            timeout_message:

        Returns:

        """
        self.process_certificate_qc(timeout_message.tmo_info.high_qc)
        self.process_certificate_qc(timeout_message.high_commit_qc)
        self.pacemaker.advance_round_tc(timeout_message.last_round_tc)
        timeout_certificate = self.pacemaker.process_remote_timeout(
            timeout_message, self.safety, self.block_tree
        )
        if not timeout_certificate:
            return None

        self.pacemaker.advance_round_tc(timeout_certificate)
        return self.process_new_round_event(timeout_certificate)

    """
    Procedure process vote msg(M)
        qc ← Block-Tree.process vote(M)
        if qc != ⊥ then
            process certificate qc(qc)
            process new round event(⊥)
    """

    def process_vote_msg(self, vote_message: VoteMsg) -> None:
        """

        Args:
            vote_message:

        Returns:

        """
        process_vote_res = self.block_tree.process_vote(vote_message)
        qc = process_vote_res[0]
        trx_to_dq = process_vote_res[1]
        if not qc:
            return (None, trx_to_dq)

        self.process_certificate_qc(qc)
        # self.process_new_round_event(None)  # TODO: Important to figure out why
        return (qc, trx_to_dq)

    """
    Procedure start event processing(M)
        if M is a local timeout then Pacemaker.local timeout round()
        if M is a proposal message then process proposal msg(M)
        if M is a vote message then process vote msg(M)
        if M is a timeout message then process timeout message(M)
    """

    def start_event_processing(self, event: Event) -> None:
        """

        Args:
            event:

        Returns:

        """
        event_type = event.get_event_type

        if event_type == EventType.LOCAL_TIMEOUT:
            pass

        if event_type == EventType.PROPOSAL_MESSAGE:
            pass

        if event_type == EventType.VOTE_MESSAGE:
            pass

        if event_type == EventType.TIMEOUT_MESSAGE:
            pass

    def check_if_current_leader(self):
        """

        Returns:

        """
        return self.leader_election.get_leader(self.pacemaker.current_round) == self.id

    def get_next_proposal(self, new_qc, old_tx_ids):
        """

        Args:
            new_qc:
            old_tx_ids:

        Returns:

        """
        logger.info(
            "Leader {} Initiating new Proposal for round {}".format(
                self.leader_election.get_leader(self.pacemaker.current_round),
                self.pacemaker.current_round,
            )
        )
        trx_id_list, transactions = self.get_transactions(old_tx_ids)
        new_block = self.block_tree.generate_block(
            transactions, self.pacemaker.current_round
        )
        self.block_tree.execute_and_insert(new_block)
        return ProposalMessage(new_block, None, new_qc, None, self.id, trx_id_list)

    def get_transactions(self, old_txids=[]):
        """

        Args:
            old_txids:

        Returns:

        """
        trx_id_list, transactions = [], []
        block_requests = []

        for (k, v) in self.mempool.queue.items():
            if k not in old_txids:
                block_requests.append((k, v))
            if len(block_requests) == self.block_tree.block_size:
                break
        for id, transaction in block_requests:
            trx_id_list.append(id)
            transactions.append(transaction)

        logger.info(
            "Round {} Proposal contains Transactions {}".format(
                self.pacemaker.current_round,
                ",".join([trx.command for trx in transactions]),
            ),
        )
        return trx_id_list, transactions

    def deque_trx(self, trx_ids: List[str]) -> Dict[str, int]:
        """

        Args:
            trx_ids:

        Returns:

        """
        trx_client_map = {}
        for req_id in trx_ids:
            transaction = self.mempool.queue.get(req_id)
            if transaction:
                self.mempool.queue.pop(req_id)
                trx_client_map[transaction.id] = transaction.client_id

        return trx_client_map
