from modules.objects.timeout_message import TimeoutMessage
from typing import List, Dict
from utils.helpers import date as date_utils

class Pacemaker:
    def __init__(self, sender_id):
        self.current_round:int = 0
        self.last_round_tc:int = 0
        self.pending_timeouts:Dict(int, TimeoutMessage) = [] # List of timeouts received per round.
        self.timer_start:int = date_utils.getTimeMillis()

    def start_timer(self, new_round):
        self.timer_start = date_utils.getTimeMillis()
        self.current_round = new_round

    def local_timeout_round(self):
        #Safety.increase_last_vote_round(self.current_round)
        #save_consensus_state()
        if ()
        high_qc = None # BlockTree.get_high_qc()
        timeout_info = 
        timeout_message = TimeoutMessage(self.current_round, None, sender, None )
        this.T.push()





    def setup(ps:set, id:int):
        # do any additional setup here
        self.local_timeout_time =  round(time.time() * 1000)
    def cs(task):
      # to enter cs, enque and send request to all, then await replies from all
        --start
        reqc = logical_clock()
        send(('Request', reqc), to=ps)

        await(len(replied) == len(ps))

      # critical section
        task()

      # to exit cs, deque and send releases to all
        --release
        reqc = None
        send(('Reply', logical_clock()), to=waiting)
        --end
        waiting = set()
        replied = set()

    def run():
        while(True):
            -- receive
            # Check if 30 seconds have elapsed since timer was set
            if (round(time.time() * 1000) - self.local_timeout_time > 30000) :
                send(('Message-Local-Timeout', ""), to=self)

    # Have a separate receive handler for each type of message

    def receive(msg=('Message-Local-Timeout', body), from_=source):
        # Pacemaker handle local timeout
        print("Timed out locally")

    def receive(msg=('Message-Proposal', body), from_=source):
        # Handle message proposal
        print("Proposal received")
    def receive(msg=('Message-Vote', body), from_=source):
        # Handle vote message 
        print("Vote received")

    def receive(msg=('Message-Timeout', body), from_=source):
        # Handle remote timeout message 
        print("Timeout received")
