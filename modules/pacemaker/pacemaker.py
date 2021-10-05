from modules.objects import TimeoutCertificate, TimeoutMessage, TimeoutInfo
from typing import List, Dict
from utils import date as date_utils

class Pacemaker:
    def __init__(self, sender_id, f):
        self.current_round:int = 0
        self.last_round_tc:int = 0
        self.pending_timeouts:Dict[int, Dict[int, TimeoutMessage]] = {} # List of timeouts received per round.
        self.timer_start:int = date_utils.getTimeMillis()
        self.f:int = f

    def start_timer(self, new_round):
        self.timer_start = date_utils.getTimeMillis()
        self.current_round = new_round

    def local_timeout_round(self):
        #TODO save_consensus_state()
        high_qc = None #TODO BlockTree.get_high_qc()
        timeout_info = None #TODO safety.make_timeout()
        return TimeoutMessage(timeout_info, self.last_round_tc, high_qc)
    
    def process_remote_timeout(self, timeout_message:TimeoutMessage):
        tmo_info:TimeoutInfo = timeout_message.tmo_info
        if tmo_info.round_no < self.current_round:
            return None
        if tmo_info.sender not in self.pending_timeouts[tmo_info.round_no]:
            self.pending_timeouts[tmo_info.round_no][tmo_info.sender] = timeout_message
        if len(self.pending_timeouts[tmo_info.round_no].keys()) == (self.f + 1):
            self.start_timer(self.current_round)
            self.local_timeout_round()

        if len(self.pending_timeouts[tmo_info.round_no].keys()) == (2 * self.f + 1):
            return TimeoutCertificate() #TODO add implementation here

        return None
    
    def advance_round_tc(self, tc):
        if tc == None or tc.round < self.current_round:
            return False
        self.last_round_tc = tc
        self.start_timer(tc.round + 1)
        return True

    def advance_round_qc(self, qc):
        if qc.vote_info.round < self.current_round:
            return False
        self.last_round_tc = None
        self.start_timer(qc.vote_info.round + 1)
        return True