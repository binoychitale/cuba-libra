from typing import Any, Dict, List, Union

from modules.block_tree.block_tree import BlockTree
from modules.objects import Block, CommittedBlock, Transaction


class Ledger:
    def __init__(self, id) -> None:
        self.ledger: List[CommittedBlock] = []
        # Map of state-id to Pending block
        self.speculate_states: Dict[str, str] = {}
        self.id = id

    def speculate(self, block_id: str, txns: Any) -> int:
        # TODO change to legit transactions later
        trans = Transaction("hello", "", 0)
        txns = trans.command
        commit_state_id = (
            self.ledger[-1].commit_state_id if len(self.ledger) > 0 else ""
        )
        self.speculate_states[block_id] = hash(str(commit_state_id) + txns)

    def get_pending_state(self, block_id: str) -> Union[int, None]:
        return self.speculate_states[block_id]

    def commit(self, block_id: str, block_tree: BlockTree):
        block_to_commit = block_tree.pending_block_tree.find(block_id)
        print(
            "Ledger: ",
            list(([trx.command for trx in cb.block.payload] for cb in self.ledger)),
            "Validator {}".format(self.id),
        )
        print("Rounds: ", [cb.block.round for cb in self.ledger])

        self.ledger.append(
            CommittedBlock(block_to_commit, self.get_pending_state(block_id))
        )
        with open("ledger-pid-" + str(self.id), "a") as ledger_file:
            commands = []
            for txn in block_to_commit.payload:
                commands.append(txn.command + "\n")
            ledger_file.writelines(commands)
            ledger_file.flush()

    def get_committed_block(self, block_id: str) -> CommittedBlock:
        for block in self.ledger:
            if block.block.id == block_id:
                return block

    def display(self):
        ledger_disp = []
        for block in self.ledger:
            for txn in block.block.payload:
                ledger_disp.append(txn.command)
        return ledger_disp
