#!/bin/bash
rm ledger-pid-*
python -m da --message-buffer-size 1000000 modules/fault_injection/fault_injection.da
python -m da --message-buffer-size 1000000 client.da
python -m da --message-buffer-size 1000000 validator.da
python -m da --message-buffer-size 1000000 wrapper.da 
