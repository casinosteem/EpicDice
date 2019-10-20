# Fairness

### Transaction ID is the only source to generate rolled number

When a user fires a bet\(transaction\) to the house account, the block contains that transaction has to be verified and signed by the Steem witness to be considered valid. In the process of block signing, various information of a particular transaction like `ref_block_num`, `ref_block_prefix`, `expiration` and so on, contributed in the generation of a fully random 40 hex digits `trx_id`. Read more about this process in [Steem Developer Portal](https://developers.steem.io/tutorials-recipes/understanding-transaction-status).

This very blockchain-generated `trx_id` is what EpicDice would solely use to generate a rolled number via formula below:

```javascript
var transId ='<replace with trx_id>'

var result = 1000000
var offset = 0
var length = 5
var endValue = offset + length
var chop
var finalResult
while (result > 999999) {
chop = transId.substring(offset, endValue)
offset += 5
endValue = offset + length
result = parseInt(chop, 16)
finalResult = result % (10000) / 100
finalResult = Math.round(finalResult)
console.log("finalResult : " + finalResult)
if (finalResult === 0) {
result = 1000000
}
}
```

You can find this formula in "Fairness" section of the game site and verify all your bet result instantly.

For interested souls in finding out how technically a `trx_id` is computed, the answer lies in [Steem Official GitHub Repository](https://github.com/steemit/steem).

### But how is this system "provably-fair"?

Now you know how a transaction ID is generated. Unlike other platforms, EpicDice does not add a custom client/server seed or nuances in the random number generation. It shows that the house would have **zero possibility to manipulate the outcome**.

You placed a bet and get a rolled number from the game site. Retrieve the transaction ID from data explorer like [steemd.com](https://steemd.com), input the ID into the formula above in a javascript compiler like [playcode.io](https://playcode.io/online-javascript-editor) and run it. The generated rolled number from the script would be exactly same as the one you get from our gaming site.

You confirmed that the house did not modify anything in the process. Hence, fairness is proven.

Or better yet, just utilize the fairness tool on the game site to make your life easier.

