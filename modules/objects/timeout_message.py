class TimeoutMessage:
    def __init__(self, round_no, high_qc, sender, signature) -> None:
        self.round = round_no
        self.high_qc = high_qc
        self.sender = sender
        self.signature = signature