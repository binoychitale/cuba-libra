from typing import Any, Dict, List, Union

from modules.block_tree.block_tree import BlockTree
from modules.objects import Block


class Ledger:
    def __init__(self) -> None:
        self.ledger: List[Block] = []
        # Map of state-id to Pending block
        self.speculate_states: Dict[str, Block] = []

    def speculate(self, prev_block_state_id: int, block_id: str, txns: Any) -> int:
        self.speculate_states[block_id] = hash(prev_block_state_id + txns)

    def get_pending_state(self, block_id: str) -> Union[int, None]:
        return self.speculate_states[block_id]

    def commit(self, block_id: str, block_tree: BlockTree):
        block_to_commit = block_tree.pending_block_tree.find(block_id)
        self.ledger.append(block_to_commit)

    def get_committed_block(self, block_id: str) -> Block:
        for block in self.ledger:
            if block.id == block_id:
                return block
