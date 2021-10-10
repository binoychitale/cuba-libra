from typing import Union

from modules.block_tree.block_tree import BlockTree
from modules.leaderelection.leaderelection import LeaderElection
from modules.ledger.ledger import Ledger
from modules.mempool.mempool import MemPool
from modules.objects import (
    Block,
    Event,
    EventType,
    Proposal,
    ProposalMessage,
    QuorumCertificate,
    TimeoutCertificate,
    TimeoutMessage,
    Transaction,
    VoteMsg,
)
from modules.pacemaker.pacemaker import Pacemaker
from modules.safety.safety import Safety


class Main:
    def __init__(
        self,
        block_tree: BlockTree,
        leader_election: LeaderElection,
        pacemaker: Pacemaker,
        safety: Safety,
        ledger: Ledger,
        id: int,
    ) -> None:
        self.block_tree: BlockTree = block_tree
        self.leader_election: LeaderElection = leader_election
        self.pacemaker: Pacemaker = pacemaker
        self.safety: Safety = safety
        self.ledger: Ledger = ledger
        self.u = None
        self.mempool: MemPool = None
        self.id = id

    def process_certificate_qc(self, qc: QuorumCertificate) -> None:
        self.block_tree.process_qc(qc)
        # TODO Fix this self.leader_election.update_leaders(qc, self.pacemaker, self.ledger)
        self.pacemaker.advance_round_qc(qc)

    def process_proposal_msg(self, proposal: ProposalMessage) -> Union[None, VoteMsg]:
        if proposal.block.qc:
            self.process_certificate_qc(proposal.block.qc)
            self.process_certificate_qc(proposal.high_commit_qc)
        if proposal.last_round_tc:
            self.pacemaker.advance_round_tc(proposal.last_round_tc)

        current_round = self.pacemaker.current_round
        leader = self.leader_election.get_leader(current_round)

        if (
            proposal.block.round != current_round
            or proposal.sender_id != leader
            or proposal.block.author != leader
        ):
            return None

        self.block_tree.execute_and_insert(proposal.block)
        vote_msg = self.safety.make_vote(
            proposal.block,
            proposal.last_round_tc,
            ledger=self.ledger,
            block_tree=self.block_tree,
        )

        if not vote_msg:
            return None

        # TODO: Capture return value and send to leader election
        # send vote_msg to LeaderElection.get_leader(round+1)
        self.pacemaker.start_timer(self.pacemaker.current_round + 1)
        return vote_msg

    def process_new_round_event(self, last_tc: TimeoutCertificate) -> None:
        # TODO: Identify and use U
        if self.u == self.leader_election.get_leader(self.pacemaker.current_round):
            # TODO: Leader code - generate proposal

            b = self.block_tree.generate_block(
                self.mempool.get_transactions(), self.pacemaker.current_round
            )

            # TODO: Broadcast and fix signature
            return ProposalMessage(
                b, last_tc, self.block_tree.high_commit_qc, signature=None
            )

    def process_timeout_msg(self, timeout_message: TimeoutMessage) -> None:
        self.process_certificate_qc(timeout_message.tmo_info.high_qc)
        self.process_certificate_qc(timeout_message.high_commit_qc)
        self.pacemaker.advance_round_tc(timeout_message.last_round_tc)

        timeout_certificate = self.pacemaker.process_remote_timeout(
            timeout_message, self.safety, self.block_tree
        )

        if not timeout_certificate:
            return None

        self.pacemaker.advance_round_tc(timeout_certificate)
        self.process_new_round_event(timeout_certificate)

    def process_vote_msg(self, vote_message: VoteMsg) -> None:
        qc = self.block_tree.process_vote(vote_message)
        if not qc:
            return None

        self.process_certificate_qc(qc)
        # self.process_new_round_event(None)  # TODO: Important to figure out why
        return qc

    def start_event_processing(self, event: Event) -> None:
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
        return self.leader_election.get_leader(self.pacemaker.current_round) == self.id

    def get_next_proposal(self, new_qc):
        # dummy transaction
        trans = Transaction("hello")
        new_block = self.block_tree.generate_block(
            [trans], self.pacemaker.current_round
        )
        self.block_tree.execute_and_insert(new_block)
        self.pacemaker.start_timer(self.pacemaker.current_round + 1)

        return ProposalMessage(new_block, None, new_qc, None, self.id)
