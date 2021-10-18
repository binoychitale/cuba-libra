from collections import OrderedDict
from typing import Dict

from modules.objects import Transaction


class MemPool:
    def __init__(self) -> None:
        self.queue: Dict[str, Transaction] = OrderedDict()
        self.processed_queue: Dict[str, bool] = {}
