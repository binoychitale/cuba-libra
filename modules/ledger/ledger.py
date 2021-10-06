from typing import Any, Union

from modules.objects import Block


class Ledger:
    def __init__(self) -> None:
        pass

    def speculate(self, prev_block_id: int, block_id: int, txns: Any) -> int:
        pass

    def get_pending_state(self, block_id: int) -> Union[int, None]:
        pass

    def commit(self, block_id):
        pass

    def get_committed_block(self, block_id: int) -> Block:
        pass
