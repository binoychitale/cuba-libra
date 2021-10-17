import pickle
from collections import namedtuple
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError, CryptoError
from nacl.hash import sha256
from nacl.signing import SignedMessage, SigningKey, VerifyKey


class TimeoutCertificate:
    def __init__(
        self, round: int, tmo_high_qc_rounds: List[int], tmo_signatures: List[Any]
    ) -> None:
        self.round = round
        self.tmo_high_qc_rounds = tmo_high_qc_rounds
        self.tmo_signatures = tmo_signatures


class LedgerCommitInfo:
    def __init__(self, commit_state_id: int, vote_info_hash: str) -> None:
        self.commit_state_id = (
            commit_state_id  # ⊥ if no commit happens when this vote is aggregated to QC
        )
        self.vote_info_hash = vote_info_hash  # Hash of VoteMsg.vote info

    def fields(self):
        return (self.commit_state_id, self.vote_info_hash)

    def __repr__(self):
        from pprint import pformat

        return pformat(vars(self), indent=4, width=1)


class VoteInfo:
    def __init__(
        self,
        id: int,
        round: int,
        parent_id: int,
        parent_round: int,
        exec_state_id: int,
    ) -> None:
        self.id = id
        self.round = round
        self.parent_id = parent_id
        self.parent_round = parent_round
        self.exec_state_id = exec_state_id

    def fields(self):
        return (
            self.id,
            self.round,
            self.parent_id,
            self.parent_round,
            self.exec_state_id,
        )

    def __repr__(self):
        from pprint import pformat

        return pformat(vars(self), indent=4, width=1)


class QuorumCertificate:
    def __init__(
        self,
        vote_info: VoteInfo,
        ledger_commit_info: LedgerCommitInfo,
        signatures: List[Any],  # TODO: A quorum of signature,
        author: int,  # u - The validator that produced the q,
        author_signature: Any,  # ← signu(signatures),
    ) -> None:
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.signatures = signatures
        self.author = author
        self.author_signature = author_signature

    def __repr__(self):
        from pprint import pformat

        return pformat(vars(self), indent=4, width=1)


class Transaction:
    def __init__(self, command: str, id: str, client_id: int):
        self.command = command
        self.id = id
        self.retry_count = 0
        self.client_id = client_id

    def create_signed_payload(self, signing_key: SigningKey) -> Tuple:
        signed_payload = Signatures.pickle_and_sign_payload(self, signing_key)
        return (self, signed_payload)


class Block:
    def __init__(
        self,
        author: Any,  # The author of the block, may not be the same as qc.author after view-change
        round: int,  # The round that generated this proposal
        payload: List[Transaction],  # Proposed transaction(s)
        qc: QuorumCertificate,  # QC for parent block
        id: str,  # A unique digest of author, round, payload, qc.vote info.id and qc.signatures
    ) -> None:

        self.author = author
        self.round = round
        self.payload = payload
        self.qc = qc
        self.id = id

    def __repr__(self):
        from pprint import pformat

        return pformat(vars(self), indent=4, width=1)


class CommittedBlock:
    def __init__(
        self,
        block: Block,
        commit_state_id: str,  # A unique digest of author, round, payload, qc.vote info.id and qc.signatures
    ) -> None:
        self.block = block
        self.commit_state_id = commit_state_id


class TimeoutInfo:
    def __init__(
        self,
        round: int,
        high_qc: QuorumCertificate,
        sender: Any,
        signature: Any,
    ) -> None:

        # TODO: Construct timeout info properly
        self.round = round
        self.high_qc = high_qc
        self.sender = sender  # Added automatically when constructed
        self.signature = signature  # ← signu(round, high qc.round); // Signed automatically when constructed


class TimeoutMessage:
    def __init__(
        self,
        tmo_info: TimeoutInfo,
        last_round_tc: TimeoutCertificate,
        high_commit_qc: QuorumCertificate,
        id: int,
    ) -> None:
        self.tmo_info = tmo_info
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc
        self.id = id

    def create_signed_payload(self, signing_key: SigningKey) -> Tuple:
        self.tmo_info.signature = Signatures.sign_message(
            bytes(str(self.id), encoding="utf-8"), signing_key
        )
        signed_payload = Signatures.pickle_and_sign_payload(self, signing_key)
        return (self, signed_payload)

    @staticmethod
    def verify_sig_from_id(id, signature, verify_key):
        return Signatures.verify_message(signature, verify_key) == bytes(
            str(id), encoding="utf-8"
        )


class VoteMsg:
    def __init__(
        self,
        vote_info: VoteInfo,  # A VoteInfo record
        ledger_commit_info: LedgerCommitInfo,  # Speculated ledger info
        high_commit_qc: QuorumCertificate,
        sender: Any,  # sender = u; // Added automatically when constructed
        signature: Any,  # signature = signu(ledger commit info); // Signed automatically when constructed
    ) -> None:
        self.vote_info = vote_info
        self.ledger_commit_info = ledger_commit_info
        self.high_commit_qc = high_commit_qc
        self.sender = sender
        self.signature = signature

    def create_signed_payload(self, signing_key: SigningKey) -> Tuple:
        signed_payload = Signatures.pickle_and_sign_payload(self, signing_key)
        return self, signed_payload


class ProposalMessage:
    def __init__(
        self,
        block: Block,
        last_round_tc: TimeoutCertificate,
        high_commit_qc: QuorumCertificate,
        signature: Any,
        sender_id: int,
        trx_ids: List[str],
    ) -> None:

        self.block = block
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc
        self.signature = signature  # TODO: signu(block.id);
        self.sender_id = sender_id
        self.trx_ids = trx_ids

    def __repr__(self):
        from pprint import pformat

        return pformat(vars(self), indent=4, width=1)

    def create_signed_payload(self, signing_key: SigningKey) -> Tuple:
        signed_payload = Signatures.pickle_and_sign_payload(self, signing_key)
        return self, signed_payload


class Certificate:
    def __init__(self) -> None:
        pass

    @staticmethod
    def is_valid_signatures(block: Block, certificate: TimeoutCertificate) -> bool:
        # TODO: Complete
        return True


class Signatures:

    encoder = HexEncoder

    @staticmethod
    def init_signatures() -> Tuple[SigningKey, VerifyKey]:
        private_key = SigningKey.generate()
        public_key = private_key.verify_key

        return private_key, public_key

    @staticmethod
    def sign_message(
        msg: bytes, private_key: SigningKey, encoder: Optional[Any] = encoder
    ) -> SignedMessage:
        return private_key.sign(msg, encoder=encoder)

    @staticmethod
    def verify_message(
        signed_msg: SignedMessage,
        public_key: VerifyKey,
        encoder: Optional[Any] = encoder,
    ) -> bytes:
        try:
            return public_key.verify(signed_msg, encoder=encoder)
        except (CryptoError, BadSignatureError):
            return False

    @staticmethod
    def pickle_and_sign_payload(obj: Any, signing_key: SigningKey) -> bytes:
        pickled_obj = pickle.dumps(obj)
        return Signatures.sign_message(pickled_obj, signing_key)

    @staticmethod
    def verify_signed_payload(
        signed_payload: SignedMessage, verify_key: VerifyKey
    ) -> Any:
        verified_obj = Signatures.verify_message(signed_payload, verify_key)
        if verified_obj:
            return pickle.loads(verified_obj)
        return False


class Hasher:

    engine = sha256
    encoder = HexEncoder

    @staticmethod
    def hash(
        msg: bytes, engine: Optional[Any] = engine, encoder: Optional[Any] = encoder
    ) -> bytes:
        return engine(msg, encoder=encoder)


class EventType:
    LOCAL_TIMEOUT = "local_timeout"
    PROPOSAL_MESSAGE = "proposal_message"
    VOTE_MESSAGE = "vote_message"
    TIMEOUT_MESSAGE = "timeout_message"


class Event:
    def __init__(self) -> None:
        pass

    def get_event_type(self) -> EventType:
        pass


class Proposal:
    def __init__(self) -> None:
        self.last_round_tc: TimeoutCertificate = None
        self.block: Block = None


class TestConfig:
    def __init__(
        self,
        nvalidators: int,
        validator_key_pairs: Tuple[SigningKey, VerifyKey],
        validator_pubkey_map: Dict[int, VerifyKey],
        client_key_pairs: Tuple[SigningKey, VerifyKey],
        client_pubkey_map: Dict[int, VerifyKey],
        num_clients: int,
    ) -> None:
        self.nvalidators = nvalidators
        self.validator_key_pairs = validator_key_pairs
        self.validator_pubkey_map = validator_pubkey_map
        self.client_key_pairs = client_key_pairs
        self.client_pubkey_map = client_pubkey_map
        self.num_clients = num_clients


class MsgType(Enum):
    Proposal = 1
    QC = 2
    TimeOut = 3
    Vote = 4
    Wildcard = 5  # matches all message types


class FailType(Enum):
    MsgLoss = 1
    Delay = 2
    SetAttr = 3


FailureConfig = namedtuple("FailureConfig", ["failures", "seed"])
Failure = namedtuple(
    "Failure",
    ["src", "dest", "msg_type", "round", "prob", "fail_type", "val", "attr"],
)


failure_cases = [
    {
        "msg": "Minority fail: Message Loss",
        "rules": FailureConfig(
            failures=[],
            seed=0,
        ),
    },
    {
        "msg": "Minority fail: Message Loss",
        "rules": FailureConfig(
            failures=[
                Failure(
                    src=0,
                    dest="_",
                    msg_type=MsgType.Wildcard,
                    round=1,
                    prob=1,
                    fail_type=FailType.MsgLoss,
                    val=None,
                    attr=None,
                )
            ],
            seed=0,
        ),
    },
    {
        "msg": "Minority fail: Message Delay",
        "rules": FailureConfig(
            failures=[
                Failure(
                    src=0,
                    dest="_",
                    msg_type=MsgType.Wildcard,
                    round=1,
                    prob=1,
                    fail_type=FailType.Delay,
                    val=10,
                    attr=None,
                )
            ],
            seed=0,
        ),
    },
    {
        "msg": "Majority fail: Validator vote delay",
        "rules": FailureConfig(
            failures=[
                Failure(
                    src="_",
                    dest="leader",
                    msg_type=MsgType.Vote,
                    round=1,
                    prob=1,
                    fail_type=FailType.Delay,
                    val=7,
                    attr=None,
                )
            ],
            seed=0,
        ),
    },
    {
        "msg": "Chained falure: Validator proposal loss(round 1) + follower vote loss (ronud 2)",
        "rules": FailureConfig(
            failures=[
                Failure(
                    src="leader",
                    dest="_",
                    msg_type=MsgType.Proposal,
                    round=1,
                    prob=1,
                    fail_type=FailType.Delay,
                    val=None,
                    attr=None,
                ),
                Failure(
                    src="_",
                    dest="leader",
                    msg_type=MsgType.Vote,
                    round=2,
                    prob=1,
                    fail_type=FailType.Delay,
                    val=None,
                    attr=None,
                ),
            ],
            seed=0,
        ),
    },
    {
        "msg": "Invalid round number",
        "rules": FailureConfig(
            failures=[
                Failure(
                    src=1,
                    dest="_",
                    msg_type=MsgType.Wildcard,
                    round=3,
                    prob=1,
                    fail_type=FailType.SetAttr,
                    val=1,
                    attr="round",
                ),
            ],
            seed=0,
        ),
    },
    # {
    #     "msg": "Majority fail: Message Delay",
    #     "rules": [
    #         Failure(
    #             src=0,
    #             dest="_",
    #             msg_type=MsgType.Wildcard,
    #             round=1,
    #             prob=1,
    #             fail_type=FailType.Delay,
    #             val=7,
    #             attr=None,
    #         ),
    #         Failure(
    #             src=1,
    #             dest="_",
    #             msg_type=MsgType.Wildcard,
    #             round=1,
    #             prob=1,
    #             fail_type=FailType.Delay,
    #             val=None,
    #             attr=None,
    #         ),
    #     ],
    # },
    # Failure(
    #     src="leader",
    #     dest="_",
    #     msg_type=MsgType.Vote,
    #     round=3,
    #     prob=0.5,
    #     fail_type=FailType.SetAttr,
    #     val=2,
    #     attr="highest_vote_round",
    # ),
]


def generate_test_configs() -> List[TestConfig]:
    n_validators = [4, 10]
    n_clients = [10, 2]
    tests = []

    for i, n in enumerate(n_validators):
        validator_key_pairs = {idx: Signatures.init_signatures() for idx in range(n)}
        validator_pubkey_map = {
            idx: pub_key for idx, (_, pub_key) in validator_key_pairs.items()
        }
        client_key_pairs = {
            idx: Signatures.init_signatures() for idx in range(n_clients[i])
        }
        client_pubkey_map = {
            idx: pub_key for idx, (_, pub_key) in client_key_pairs.items()
        }
        tests.append(
            {
                "nvalidators": n,
                "validator_key_pairs": validator_key_pairs,
                "validator_pubkey_map": validator_pubkey_map,
                "client_key_pairs": client_key_pairs,
                "client_pubkey_map": client_pubkey_map,
                "num_clients": n_clients[i],
            }
        )

    return [TestConfig(**config) for config in tests]
