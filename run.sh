#!/bin/bash
rm ledger-pid-*
python -m da modules/fault_injection/fault_injection.da
python -m da client.da
python -m da validator.da
python -m da wrapper.da 