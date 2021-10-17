### Cryptographic checking ( Omitted gory details):

The pseudo code below shows the way in which validators can verify :
1. The authenticity of messages from a particular sender
2. Authenticity of QC votes and TC timeout messages (To ensure the authenticity of the voter)

```js
// Safety class methods

// Returns True if the message body matches the decryped signature
function verifyMsg(message) {

 decrypted_signature = verify(message.signature, public_key(message.author))

 return decrypted_signature == message.body
}

// Loop through each of the QC signatures, and verify that the encrypted digest
// can be decrypted and is equal to the body of the QC (this verifies the authenticity of the voter)
function verifyQC(qc) {
 for signatures in qc.signatures {
   decrypted_signature = verify(signature.digest, public_key(qc.signature.author))

   if decrypted_signature != qc.body{
     return False
   }
 }
 return True
}

// Loop through each of the TC signatures, and verify that the encrypted
// digest can be decrypted and is equal to the body of the TC (this verifies the
// authenticity of the sender of the timeout message)
function verifyTC(qc) {

 for signatures in tc.signatures {
   decrypted_signature = verify(signature.digest, public_key(tc.signature.author))

   if decrypted_signature != tc.body{
     return False
   }
 }
 return True
}
```

### Client Message Handling:

1. The pseudo-code below demonstrates how the validator’s Mempool should handle duplicate/retransmitted transactions in order to avoid committing a transaction twice

```js
// MemPool class

pending_transactions = list()
completed_transactions = list()

// Fetch <block_size> transactions from the mempool
function get_transactions() {
 new_transactions = []

 for transaction in pending transactions {

   new_transactions.append(transaction)

   if length(new_transactions) == block_size {
     return transactions
   }
 }
 return transactions
}

// Remove transactions from the pending queue after they are committed,
// so that they are not proposed twice
function dequeue_transaction(transaction) {

 completed_transactions.append(transaction)

 pending_transactions.delete(transaction)

}

// When a new transaction arrives, make sure it is not pending(i.e in pending_transactions)
// and not already committed (i.e in completed_transactions). Only if it is a new transaction, add it to queue
function new_transaction(transaction) {

 if transaction  not in (pending_transaction | completed transactions)
   pending_transactions.append(transaction)
}
```

2. Below is the pseudo code for the client to know when a submitted transaction is safely committed

```js
// Client module
function request_commit(transaction) {

 broadcast(payload=transaction, to=validators)

 // Wait until 2f+1 validators have committed the transaction
 await(length(responses) == 2f + 1)

 return True
}
```


### Syncing up lagging replicas:
Below is a potential way for lagging replicas to catch up to the block state.

```js
// Lagging server module
function sync_replica() {
 validator = some validator in validators

 // Make a network call to another validator to get the blocks in the
 // chain after the latest locally committed block
 new_blocks = validator.get_blocks_after(self.get_latest_committed_block())

 // Locally apply the new blocks retrieved
 commit_state_id = speculate(new_blocks)

 for validator in validators:

   // Ensure that at least 2f+1 validators have the same commit_state_id
   // (i.e an indirect hash of the entire chain).
   // This ensures that the the final state(commit_state_id) of the
   // entire chain is agreed upon by at least 2f+1   validators, which means it must be actual state
   assert(commit_state_id == validator.commit_state_id)

 commit(new_blocks)
}
```
