# Fairness

## Fairness that is provable

All the random number generation on EpicDice is coming from **Transactino ID** and **Server Seed**. Transaction ID is generated on Steem blockchian the moment it is broadcasted. While server seed is decided by the house system every 2 minutes. An encoded server seed is published on the Steem blockchain before it was applied in new random number generation. Then the server seed is revealed before next one is generated.

This combination shows that the house would have **zero possibility to manipulate the outcome** while making sure system security is not compromised.

## Dice

Manual verification can be done over [_playcode.io_](https://playcode.io/450370?tabs=script.js,preview,console)_._

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

## Between

Manual verification can be done over [_playcode.io_](https://playcode.io/470482?tabs=script.js,preview,console)_._

| rawValue | Face Value |
| :--- | :--- |
| 0 - 3 | A |
| 4 - 7 | 2 |
| 8 - 11 | 3 |
| 12 - 15 | 4 |
| 16 - 19 | 5 |
| 20 - 23 | 6 |
| 24 - 27 | 7 |
| 28 - 31 | 8 |
| 32 - 35 | 9 |
| 36- 39 | 10 |
| 40 - 43 | J |
| 44 - 47 | Q |
| 48 - 51 | K |

```javascript
    var result_trans_id ="<Insert the transaction id of your bet that sent to epicdice>"
    var serverSeed = "<Insert the server seed reveal by Epicdice every 2 minutes>"

    var result = 1000000
    var offset = 0
    var length = 5
    var endValue = offset + length
    var chop
    var tempResult
    var won = 0

    var tempHash = sha256(serverSeed + result_trans_id)
    while (result > 999999) {
        try {
            chop = tempHash.substring(offset, endValue)
            offset += 5
            endValue = offset + length
            result = parseInt(chop, 16)
   
            try {
                tempResult = result % (10000) / 100
                tempResult = Math.round(tempResult);
                console.log("Final Result " + tempResult)
                if (tempResult === 0) {
                    result = 1000000
                }
            } catch (err2) {
                console.log(err2)
            }
        } catch (err) {
            console.log(err)
            result = -1
        }
    }

function sha256(ascii) {
	function rightRotate(value, amount) {
		return (value>>>amount) | (value<<(32 - amount));
	};
	
	var mathPow = Math.pow;
	var maxWord = mathPow(2, 32);
	var lengthProperty = 'length'
	var i, j; // Used as a counter across the whole file
	var result = ''

	var words = [];
	var asciiBitLength = ascii[lengthProperty]*8;
	
	//* caching results is optional - remove/add slash from front of this line to toggle
	// Initial hash value: first 32 bits of the fractional parts of the square roots of the first 8 primes
	// (we actually calculate the first 64, but extra values are just ignored)
	var hash = sha256.h = sha256.h || [];
	// Round constants: first 32 bits of the fractional parts of the cube roots of the first 64 primes
	var k = sha256.k = sha256.k || [];
	var primeCounter = k[lengthProperty];
	/*/
	var hash = [], k = [];
	var primeCounter = 0;
	//*/

	var isComposite = {};
	for (var candidate = 2; primeCounter < 64; candidate++) {
		if (!isComposite[candidate]) {
			for (i = 0; i < 313; i += candidate) {
				isComposite[i] = candidate;
			}
			hash[primeCounter] = (mathPow(candidate, .5)*maxWord)|0;
			k[primeCounter++] = (mathPow(candidate, 1/3)*maxWord)|0;
		}
	}
	
	ascii += '\x80' // Append Ƈ' bit (plus zero padding)
	while (ascii[lengthProperty]%64 - 56) ascii += '\x00' // More zero padding
	for (i = 0; i < ascii[lengthProperty]; i++) {
		j = ascii.charCodeAt(i);
		if (j>>8) return; // ASCII check: only accept characters in range 0-255
		words[i>>2] |= j << ((3 - i)%4)*8;
	}
	words[words[lengthProperty]] = ((asciiBitLength/maxWord)|0);
	words[words[lengthProperty]] = (asciiBitLength)
	
	// process each chunk
	for (j = 0; j < words[lengthProperty];) {
		var w = words.slice(j, j += 16); // The message is expanded into 64 words as part of the iteration
		var oldHash = hash;
		// This is now the undefinedworking hash", often labelled as variables a...g
		// (we have to truncate as well, otherwise extra entries at the end accumulate
		hash = hash.slice(0, 8);
		
		for (i = 0; i < 64; i++) {
			var i2 = i + j;
			// Expand the message into 64 words
			// Used below if 
			var w15 = w[i - 15], w2 = w[i - 2];

			// Iterate
			var a = hash[0], e = hash[4];
			var temp1 = hash[7]
				+ (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) // S1
				+ ((e&hash[5])^((~e)&hash[6])) // ch
				+ k[i]
				// Expand the message schedule if needed
				+ (w[i] = (i < 16) ? w[i] : (
						w[i - 16]
						+ (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15>>>3)) // s0
						+ w[i - 7]
						+ (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2>>>10)) // s1
					)|0
				);
			// This is only used once, so *could* be moved below, but it only saves 4 bytes and makes things unreadble
			var temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)) // S0
				+ ((a&hash[1])^(a&hash[2])^(hash[1]&hash[2])); // maj
			
			hash = [(temp1 + temp2)|0].concat(hash); // We don't bother trimming off the extra ones, they're harmless as long as we're truncating when we do the slice()
			hash[4] = (hash[4] + temp1)|0;
		}
		
		for (i = 0; i < 8; i++) {
			hash[i] = (hash[i] + oldHash[i])|0;
		}
	}
	
	for (i = 0; i < 8; i++) {
		for (j = 3; j + 1; j--) {
			var b = (hash[i]>>(j*8))&255;
			result += ((b < 16) ? 0 : '') + b.toString(16);
		}
	}
	return result;
};
```



