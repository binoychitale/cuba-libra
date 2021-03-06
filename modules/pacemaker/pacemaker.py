import logging
from typing import Dict

from modules.block_tree.block_tree import BlockTree
from modules.objects import (
    QuorumCertificate,
    TimeoutCertificate,
    TimeoutInfo,
    TimeoutMessage,
)
from modules.safety.safety import Safety
from modules.utils import helpers as date_utils

logger = logging.getLogger(__name__)


class Pacemaker:
    def __init__(self, f: int, id: int, leader_election, gst: float) -> None:
        """

        Args:
            f:
            id:
            leader_election:
            gst:
        """
        self.current_round: int = 0
        self.last_round_tc: TimeoutCertificate = None
        self.pending_timeouts: Dict[
            int, Dict[int, TimeoutMessage]
        ] = {}  # List of timeouts received per round.
        self.timer_start: int = date_utils.getTimeMillis()
        self.f: int = f
        self.round_done = False
        self.id = id
        self.gst = gst
        self.leader_election = leader_election

    """
    Function get round timer(r)
        return round timer formula (We use 10 * GST value that we determined from multiple iterations of DA runs)
    """

    def get_round_timer(self):
        return 10 * self.gst

    """
    Procedure start timer(new round)
        stop timer(current round)
        current round ← new round
        start local timer for round current round for duration get round timer(current round)
    """

    def start_timer(self, new_round: int) -> None:
        self.timer_start = date_utils.getTimeMillis()
        self.current_round = new_round
        self.round_done = True

    """
    Procedure local timeout round()
        save consensus state()
        timeout info ← Safety.make timeout(current round, Block-Tree.high qc, last round tc)
        broadcast TimeoutMsghtimeout info, last round tc, Block-Tree.high commit qci
    """

    def local_timeout_round(
        self, safety: Safety, block_tree: BlockTree
    ) -> TimeoutMessage:
        timeout_info = safety.make_timeout(
            self.current_round, block_tree.high_qc, self.last_round_tc
        )

        # Send timeout message back to caller which will do the Broadcast to all other validators
        return TimeoutMessage(
            timeout_info, self.last_round_tc, block_tree.high_qc, self.id
        )

    """
    Used pseudocode from paper
    """

    def extract_high_qc(self, timeout_msg):
        return timeout_msg.high_qc

    def extract_timeout_signatures(self, timeout_msg):
        return (timeout_msg.tmo_info.signature, timeout_msg.id)

    def process_remote_timeout(
        self, timeout_message: TimeoutMessage, safety: Safety, block_tree: BlockTree
    ) -> None:
        tmo_info: TimeoutInfo = timeout_message.tmo_info
        if tmo_info.round < self.current_round:
            return None
        self.pending_timeouts[tmo_info.round] = (
            self.pending_timeouts[tmo_info.round]
            if tmo_info.round in self.pending_timeouts
            else {}
        )
        if tmo_info.sender not in self.pending_timeouts[tmo_info.round]:
            self.pending_timeouts[tmo_info.round][tmo_info.sender] = timeout_message
        if len(self.pending_timeouts[tmo_info.round].keys()) == (self.f + 1):
            self.start_timer(self.current_round)
            self.local_timeout_round(safety, block_tree)

        if len(self.pending_timeouts[tmo_info.round].keys()) == (2 * self.f + 1):
            high_qc_rounds = map(
                self.extract_high_qc, self.pending_timeouts[tmo_info.round]
            )
            timeout_signatures = map(
                self.extract_timeout_signatures,
                self.pending_timeouts[tmo_info.round].values(),
            )
            if self.id != self.leader_election.get_leader(self.current_round):
                self.start_timer(self.current_round + 1)
                return None
            return TimeoutCertificate(
                tmo_info.round, high_qc_rounds, timeout_signatures
            )  # TODO add implementation here

    """
    Function advance round tc(tc)
        if tc = ⊥ ∨ tc.round < current round then
            return false
        last round tc ← tc
        start timer(tc.round + 1)
        return true

    """

    def advance_round_tc(self, tc: TimeoutCertificate) -> bool:
        if tc == None or tc.round < self.current_round:
            return False
        self.last_round_tc = tc

        logger.info(
            "Advancing Round to {} and starting timer after processing TC of round {}".format(
                tc.round + 1, tc.round
            )
        )
        self.start_timer(tc.round + 1)
        return True

    """
    Function advance round qc(qc)
        if qc.vote info.round < current round then
            return false
        last round tc ← ⊥
        start timer(qc.vote info.round + 1)
        return true

    """

    def advance_round_qc(self, qc: QuorumCertificate) -> bool:
        qc_round = qc.vote_info.round if qc else -1
        if qc_round < self.current_round:
            return False
        self.last_round_tc = None

        logger.info(
            "Advancing Round to {} and starting timer after processing QC of Proposal from round {}".format(
                qc_round + 1, qc_round
            )
        )
        self.start_timer(qc_round + 1)
        return True
