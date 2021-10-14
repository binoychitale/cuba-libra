from os import stat
from typing import Any, Dict, List, Optional, Tuple

from nacl import encoding
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


class Block:
    def __init__(
        self,
        author: Any,  # The author of the block, may not be the same as qc.author after view-change
        round: int,  # The round that generated this proposal
        payload: Any,  # Proposed transaction(s)
        qc: QuorumCertificate,  # QC for parent block
        id: str,  # A unique digest of author, round, payload, qc.vote info.id and qc.signatures
    ) -> None:

        self.author = author
        self.round = round
        self.payload = payload
        self.qc = qc
        self.id = id


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

    def _sign_timeout_msg(self, signing_key: SigningKey) -> bytes:
        return Signatures.sign_message(
            bytes(str(self.id), encoding="utf-8"), signing_key
        )

    def create_signed_payload(self, signing_key: SigningKey) -> Tuple:
        return (self, self._sign_timeout_msg(signing_key))

    def verify_signed_payload(
        self, signed_payload: SignedMessage, verify_key: VerifyKey
    ) -> bool:
        return Signatures.verify_message(signed_payload, verify_key) == bytes(
            str(self.id), encoding="utf-8"
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

    def _sign_vote(self, signing_key: SigningKey) -> bytes:
        return Signatures.sign_message(
            bytes(str(self.sender), encoding="utf-8"), signing_key
        )

    def create_signed_payload(self, signing_key: SigningKey) -> Tuple:
        return (self, self._sign_vote(signing_key))

    def verify_signed_payload(
        self, signed_payload: SignedMessage, verify_key: VerifyKey
    ) -> bool:
        return Signatures.verify_message(signed_payload, verify_key) == bytes(
            str(self.sender), encoding="utf-8"
        )


class ProposalMessage:
    def __init__(
        self,
        block: Block,
        last_round_tc: TimeoutCertificate,
        high_commit_qc: QuorumCertificate,
        signature: Any,
        sender_id: int,
    ) -> None:

        self.block = block
        self.last_round_tc = last_round_tc
        self.high_commit_qc = high_commit_qc
        self.signature = signature  # TODO: signu(block.id);
        self.sender_id = sender_id

    def _sign_proposal(self, signing_key: SigningKey) -> bytes:
        return Signatures.sign_message(
            bytes(str(self.sender_id), encoding="utf-8"), signing_key
        )

    def create_signed_payload(self, signing_key: SigningKey) -> Tuple:
        return (self, self._sign_proposal(signing_key))

    def verify_signed_payload(
        self, signed_payload: SignedMessage, verify_key: VerifyKey
    ) -> bool:
        return Signatures.verify_message(signed_payload, verify_key) == bytes(
            str(self.sender_id), encoding="utf-8"
        )


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


class Hasher:

    engine = sha256
    encoder = HexEncoder

    @staticmethod
    def hash(
        msg: bytes, engine: Optional[Any] = engine, encoder: Optional[Any] = encoder
    ) -> bytes:
        return engine(msg, encoder=encoder)


class Transaction:
    def __init__(self, command: str):
        self.command = command


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
        key_pairs: Tuple[SigningKey, VerifyKey],
        public_key_map: Dict[int, VerifyKey],
    ) -> None:
        self.nvalidators = nvalidators
        self.key_pairs = key_pairs
        self.public_key_map = public_key_map


def generate_test_configs() -> List[TestConfig]:
    n_validators = [4, 10]
    tests = []

    for n in n_validators:
        key_pairs = {idx: Signatures.init_signatures() for idx in range(n)}
        public_key_map = {idx: pub_key for idx, (_, pub_key) in key_pairs.items()}
        tests.append(
            {
                "nvalidators": n,
                "key_pairs": key_pairs,
                "public_key_map": public_key_map,
            }
        )

    return [TestConfig(**config) for config in tests]
