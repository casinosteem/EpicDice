# Proof of fairness

### Data analysis of rolled numbers occurrence in EpicDice since the very beginning

This dataset recorded every single bet ever sent to @epicdice starting from `2019-02-28 16:24:10.967494` until `2019-06-13 13:37:26.029482`\(UTC\).

Download the excel sheet here: [https://mega.nz/\#!z8EDSYCY!yS\_svuOIULFxBNZRNpo\_nwMsczQPqaWNFmvMnZIfVek](https://mega.nz/#!z8EDSYCY!yS_svuOIULFxBNZRNpo_nwMsczQPqaWNFmvMnZIfVek)

Key columns in the dataset as follows:

* `refTransactionId`: the `trx_id` which you can verify in data explorer
* `user`: name of the player
* `rollResult`: generated rolled number out of `refTransactionId`
* `winLost`: `0` is lost while `1` is win

![EXCEL\_2019-06-15\_18-05-20.png](https://cdn.steemitimages.com/DQmeoTRekzpu2mknKfA7YgaTqggHghgV1SnMekbbjxHiW5m/EXCEL_2019-06-15_18-05-20.png)

Over the period, EpicDice has received 455,519 transactions of wager and the total amount is 16,215,981.400\(STEEM + SBD\). The full range of rolling numbers \(1 to 100\) is divided into 10 groups with 10 numbers in each of it. The goal of this analysis is to verify whether the occurrence of rolled numbers is evenly distributed across the range groups. In the perfect world, a totally random and fair algorithm should grant 10% occurrence to the 10 groups.

![EXCEL\_2019-06-15\_18-05-47.png](https://cdn.steemitimages.com/DQmZqshYEZ32o7RNnSZttaf3ujtHgNVMVb27hoeCfANEnZk/EXCEL_2019-06-15_18-05-47.png)

The graph shows that each category had a fair distribution as the lowest percentage was 9.56% while the highest was 10.10%. Merely a 0.54% deviation proves that there is absolutely no bias in random number generation. **Each roll stands a fair chance of getting a number ranging from 1 to 100.**

Ironically, when EpicDice was only supporting "rolling under" most of the time before the latest upgrade a few days ago, higher numbers like 95,96,97,98,99,100 used to be the killers to any bet when they were rolled. But they had the lowest occurrence at 9.56%.

