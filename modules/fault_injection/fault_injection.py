# -*- generated by 1.0.14 -*-
import da
_config_object = {}
import time
from typing import Dict, NamedTuple, Tuple
from nacl.signing import SigningKey, VerifyKey
from scipy.stats import bernoulli
from modules.block_tree.block_tree import BlockTree
from modules.leaderelection.leaderelection import LeaderElection
from modules.ledger.ledger import Ledger
from modules.main.main import Main
from modules.objects import FailType, MsgType, ProposalMessage, Transaction
from modules.pacemaker.pacemaker import Pacemaker
from modules.safety.safety import Safety
from validator import Validator

class ValidatorFI(Validator, da.DistProcess):

    def __init__(self, procimpl, props):
        super().__init__(procimpl, props)
        self._events.extend([])

    def setup(self, ps, id, f, key_pair, public_key_map, validator_map, kv_pairs_map, failure_config, **rest_458):
        super().setup(ps=ps, id=id, f=f, key_pair=key_pair, public_key_map=public_key_map, validator_map=validator_map, kv_pairs_map=kv_pairs_map, failure_config=failure_config, **rest_458)
        self._state.ps = ps
        self._state.id = id
        self._state.f = f
        self._state.key_pair = key_pair
        self._state.public_key_map = public_key_map
        self._state.validator_map = validator_map
        self._state.kv_pairs_map = kv_pairs_map
        self._state.failure_config = failure_config
        self._state.failure_config = self._state.failure_config
        super().setup(self._state.ps, self._state.id, self._state.f, self._state.key_pair, self._state.public_key_map, self._state.validator_map, self._state.kv_pairs_map)

    def send(self, m, to):
        for failure in self._state.failure_config.failures:
            if (((failure.src == super().get_validator_id()) or (failure.src == '_')) and ((failure.dest == self.get_pid(to)) or (failure.dest == '_') or ((failure.dest == 'leader') and (self.get_pid(to) == super().get_leader()))) and ((failure.msg_type == MsgType.Wildcard) or (failure.msg_type == self.msg_string_to_enum(m[0]))) and (super().get_current_round() == failure.round)):
                to_fail = bernoulli.rvs(failure.prob, size=1)
                if (to_fail[0] == 0):
                    break
                elif (failure.fail_type == FailType.Delay):
                    time.sleep(failure.val)
                elif (failure.fail_type == FailType.MsgLoss):
                    return
                elif (failure.fail_type == FailType.SetAttr):
                    if (failure.attr == 'round'):
                        super().set_current_round(failure.val)
                    elif (failure.attr == 'highest_vote_round'):
                        super().set_highest_vote_round(failure.val)
        super().send(m, to)

    def get_pid(self, dest_p_obj):
        for (self._state.id, p_obj) in enumerate(super().get_validator_map()):
            if (dest_p_obj == p_obj):
                return self._state.id

    def msg_string_to_enum(self, msg_type):
        if (msg_type == 'Message-Proposal'):
            return MsgType.Proposal
        elif (msg_type == 'Message-Vote'):
            return MsgType.Vote
        elif (msg_type == 'Message-Timeout'):
            return MsgType.TimeOut
