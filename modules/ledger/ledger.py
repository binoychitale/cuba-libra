import logging
from typing import Dict, List, Union

from modules.block_tree.block_tree import BlockTree
from modules.objects import CommittedBlock, Transaction

logger = logging.getLogger(__name__)


class Ledger:
    def __init__(self, id) -> None:
        self.ledger: List[CommittedBlock] = []
        # Map of state-id to Pending block
        self.speculate_states: Dict[str, str] = {}
        self.id = id

    def speculate(self, block_id: str, txns: List[Transaction]) -> int:
        txns = ",".join([trx.command for trx in txns])
        commit_state_id = (
            self.ledger[-1].commit_state_id if len(self.ledger) > 0 else ""
        )
        self.speculate_states[block_id] = hash(str(commit_state_id) + txns)

    def get_pending_state(self, block_id: str) -> Union[int, None]:
        return self.speculate_states[block_id]

    def commit(self, block_id: str, block_tree: BlockTree):
        block_to_commit = block_tree.pending_block_tree.find(block_id)
        self.ledger.append(
            CommittedBlock(block_to_commit, self.get_pending_state(block_id))
        )
        transactions_to_dq = list(trx.id for trx in block_to_commit.payload)

        logger.info(
            "Committed transactions {} proposed by Leader {} in round {} in Validator {}".format(
                list(trx.command for trx in self.ledger[-1].block.payload),
                self.ledger[-1].block.author,
                self.ledger[-1].block.round,
                self.id,
            )
        )

        with open("ledger-pid-" + str(self.id), "a") as ledger_file:
            commands = []
            for txn in block_to_commit.payload:
                commands.append(txn.command + "\n")
            ledger_file.writelines(commands)
            ledger_file.flush()
        return transactions_to_dq

    def get_committed_block(self, block_id: str) -> CommittedBlock:
        for block in self.ledger:
            if block.block.id == block_id:
                return block

    def display(self):
        return list(([trx.command for trx in cb.block.payload] for cb in self.ledger))
