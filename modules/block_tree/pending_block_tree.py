from typing import Dict, List

from modules.objects import Block, VoteInfo


class PendingBlockTree:
    def __init__(self):
        self.tree: List[Block] = []

    def prune(self, vote_info: VoteInfo):
        pruned_tree = []
        for block in self.tree:
            if (
                vote_info.id == block.id
                or block.qc is None
                or block.qc.vote_info.parent_id != vote_info.parent_id
            ):
                pruned_tree.append(block)
        self.tree = pruned_tree

    def add(self, block: Block):
        self.tree.append(block)

    def find(self, block_id):
        for block in self.tree:
            if block.id == block_id:
                return block
