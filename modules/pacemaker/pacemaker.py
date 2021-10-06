from typing import Dict, List

from modules.objects import (
    QuorumCertificate,
    TimeoutCertificate,
    TimeoutInfo,
    TimeoutMessage,
)
from modules.utils import helpers as date_utils


class Pacemaker:
    def __init__(self, sender_id, f) -> None:
        self.current_round: int = 0
        self.last_round_tc: int = 0
        self.pending_timeouts: Dict[
            int, Dict[int, TimeoutMessage]
        ] = {}  # List of timeouts received per round.
        self.timer_start: int = date_utils.getTimeMillis()
        self.f: int = f

    def start_timer(self, new_round: int) -> None:
        self.timer_start = date_utils.getTimeMillis()
        self.current_round = new_round

    def local_timeout_round(self) -> TimeoutMessage:
        # TODO save_consensus_state()
        high_qc = None  # TODO BlockTree.get_high_qc()
        timeout_info = None  # TODO safety.make_timeout()
        return TimeoutMessage(timeout_info, self.last_round_tc, high_qc)

    def process_remote_timeout(self, timeout_message: TimeoutMessage) -> None:
        tmo_info: TimeoutInfo = timeout_message.tmo_info
        if tmo_info.round < self.current_round:
            return None
        if tmo_info.sender not in self.pending_timeouts[tmo_info.round]:
            self.pending_timeouts[tmo_info.round_no][tmo_info.sender] = timeout_message
        if len(self.pending_timeouts[tmo_info.round].keys()) == (self.f + 1):
            self.start_timer(self.current_round)
            self.local_timeout_round()

        if len(self.pending_timeouts[tmo_info.round].keys()) == (2 * self.f + 1):
            high_qc_rounds = map(
                lambda item: item.high_qc, self.pending_timeouts[tmo_info.round]
            )
            return TimeoutCertificate(
                tmo_info.round, high_qc_rounds, None
            )  # TODO add implementation here

    def advance_round_tc(self, tc: TimeoutCertificate) -> bool:
        if tc == None or tc.round < self.current_round:
            return False
        self.last_round_tc = tc
        self.start_timer(tc.round + 1)
        return True

    def advance_round_qc(self, qc: QuorumCertificate) -> bool:
        if qc.vote_info.round < self.current_round:
            return False
        self.last_round_tc = None
        self.start_timer(qc.vote_info.round + 1)
        return True
