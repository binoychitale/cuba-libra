from typing import Dict, List

from modules.objects import Block, VoteInfo


class PendingBlockTree:
    def __init__(self):
        self.tree: List[Block] = []

    def prune(self, parent_id):
        pruned_tree = []
        parent_block = self.find(parent_id)
        for block in self.tree:
            # Parent_block.id !== parent_id
            if (
                parent_block.id == block.id
                or block.qc is None
                or block.qc.vote_info.parent_id != parent_id
            ):
                pruned_tree.append(block)
        self.tree = pruned_tree

    def add(self, block: Block):
        self.tree.append(block)

    def find(self, block_id) -> Block:
        for block in self.tree:
            if block.id == block_id:
                return block
