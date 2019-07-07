from steem import Steem
import steem
from steem.blockchain import Blockchain
from steem.post import Post
import json
import datetime
import sqlite3
from beem.blockchain import Blockchain
from beem.block import Block
from beem.block import BlockHeader
from beem.transactionbuilder import TransactionBuilder
from beembase.operations import Transfer
import json
import time
import sys
from math import ceil, floor
import random
from beem.account import Account
from datetime import datetime, timezone
import calendar
import time
import schedule
import sys
import atexit
import os
import hmac
import string
import hashlib
import base64

IS_SHOW_LOG = False

cred = "<sensitive data removed>"
database_admin = "<sensitive data removed>"


ref = db.reference('Production/epic')
transRef = ref.child('meta/transactions/')
statusRef = ref.child('meta/status/backend/')
statusFERef = ref.child('meta/status/frontends/')
controlRef = ref.child('meta/controls/')
configRef = ref.child('meta/configs/')
hashRef = ref.child('meta/hashs/')
specialHashRef = ref.child('meta/specialHash/')
restrictionRef = ref.child('meta/restriction/')
houseFundRef = ref.child('meta/houseFund/')
betContestRef = ref.child('meta/contest/weeklys/data')
tokenTransactionsRef = ref.child('meta/tokens/transactions')

# config
watching = 'epicdice'
maxwin = {'STEEM': 100.000, 'SBD': 100.000}
houseEdge = 0.02
minbet = 0.10
maxRate = 95
minRate = 6
referralRate = 0.15

blacklistRef = ref.child('blacklist')
userList = []
softList = []
retrieveInterval = 10
initialControlCount = 0
controlCount = 0

isFirstTime = 1
lastProcessedBlock = 0
dictionaryKey = {}
activeUTCServedSeedInSecond = ""

blackListEnrollThreshold = 10
upliftDuration = 10 * 60

def storeDatabase(rollResult, refBlockNumber, refTransactionId, memo, asset, amount, user, factor, rate, winLost, totalPayout, unixTimeStamp, date, multiplier, betType):
    try:
        transRef.push().set({
            'rollResult': rollResult,
            'refBlockNumber': refBlockNumber,
            'refTransactionId': refTransactionId,
            'memo': memo,
            'asset': asset,
            'amount': amount,
            'user': user,
            'factor': factor,
            'rate': rate,
            'winLost': winLost,
            'totalPayout': totalPayout,
            'unixTimeStamp': unixTimeStamp,
            'date': date,
            'multiplier': multiplier,
            'betType': betType
        })
    except Exception as e:
        print('Store Database Error !!! ' + str(e))


def retrieveBlackList():
    # userList =[]
    try:
        userList[:] = []
        snapshot = blacklistRef.child("confirmed").get()
        print('******************* List of Blacklisted user ***************************************************')
        for key, val in snapshot.items():
            print('BlackListed :  key ' + key + ' dateAdded ' +
                  val['date'] + '  user : ' + val['user'])
            userList.append(val['user'])
        print('******************* End ************************************************************************')
    except Exception as e:
        print('retrieveBlackList Error !!! ' + str(e))
        

def upThePotentialCount(username):
    try:
        potentialListSnapshot = blacklistRef.child("potentialList").child(username).get()
        if potentialListSnapshot is not None:
            potentialCount = potentialListSnapshot['count']
            potentialCount = potentialCount + 1
            blacklistRef.child("potentialList").child(username).update({
                'username': username,
                'count': potentialCount
            })
    except Exception as e:
        print('upThePotentialCount error !!! ' + str(e))

def resetSoftBannedCount():
    try:
        printX('resetSoftBannedCount ')
        softList[:] = []
        snapshot = blacklistRef.child("potentialList").get()
        for key, val in snapshot.items():
            if val['count'] != 0:
                if val['upliftUnix'] - getUnix() < 0:
                    softList.append(val['username'])
        for username in softList:
            blacklistRef.child("potentialList").child(username).update({
                'count': 0,
            })
    except Exception as e:
        print('resetSoftBannedCount error !!! ' + str(e))

def potentialBlackListChecking(potentialBlackListName):
    try:
        potentialListSnapshot = blacklistRef.child("potentialList").child(potentialBlackListName).get()
        if potentialListSnapshot is not None:
            potentialCount = potentialListSnapshot['count']
            potentialCount = potentialCount + 1
            blacklistRef.child("potentialList").child(potentialBlackListName).update({
                'username': potentialBlackListName,
                'count': potentialCount,
                'upliftUnix' : getUnix() + upliftDuration
            })

            if potentialCount > blackListEnrollThreshold :
                blacklistRef.child("confirmed").push().set({
                    'date': getUTCTime(),
                    'user': potentialBlackListName
                })
        else:
            blacklistRef.child("potentialList").child(potentialBlackListName).set({
                'username': potentialBlackListName,
                'count': 1,
                'upliftUnix' : getUnix() + upliftDuration
            })

        return blackListEnrollThreshold - potentialCount - 1
    except Exception as e:
        print('setPotentialBlackList error !!! ' + str(e))

def getPotentialViolateCount(username):
    try :        
        tempSnapshot = blacklistRef.child("potentialList").child(username).get()
        if tempSnapshot is not None:
            return tempSnapshot['count']
    except Exception as e:
        print('getPotentialViolateCount error !!! ' + str(e))

def checkPoint():
    try:
        currentDate = str(datetime.now(timezone.utc).astimezone())
        statusRef.update({
            'lastUpdateDate': currentDate,
            'unixtimestamp': getUnix(),
            'statusCode': 0,
            'serverSideSeed': 'empty'
        })
    except Exception as e:
        print('checkPoint error !!! ' + str(e))

def setFrontEndStatus():
    try:
        statusFERef.update({
            'description': "description",
            'title': "title",
            'status': "1"
        })
    except Exception as e:
        print('setFrontEndStatus error !!! ' + str(e))

def updateIsLatestBlock(latest):
    try:
        # currentDate = str(datetime.now(timezone.utc).astimezone())
        statusRef.update({
            'isLatestBlock' : latest
        })
    except Exception as e:
        print('updateIsLatestBlock error !!! ' + str(e))

def getControlCount():
    try:
        controlSnapshot = controlRef.get()
        controlCount = controlSnapshot['count']
        return controlCount
    except Exception as e:
        print('getControlCount error ' + str(e))
    return controlCount


def registerListener():
    controlRef.listen(listener)


def listener(event):
    printX(event.event_type)  # can be 'put' or 'patch'
    printX(event.path)  # relative to the reference, it seems
    activeCount = event.data['count']
    printX("activeCount " + str(activeCount) +
          " initialControlCount " + str(initialControlCount))
    if initialControlCount is not activeCount:
        printX('initialControlCount not same to activeCount')
        # print('ERROR!!! Terminating this program to prevent Duplicate program running.')
        try:
            print(
                'ERROR!!! Terminating this program to prevent Duplicate program running.')
            os._exit(1)
        except SystemExit:
            print('dont care')


def setControlCount(count):
    try:
        controlRef.set({
            'count': count
        })
    except Exception as e:
        print('setControlCount error ' + str(e))


def setConfig():
    try:
        configRef.set({
            'houseEdge': 0.02,
            'maxPayoutOnWin': 100.00,
            'referralRate' : 0.125

        })
    except Exception as e:
        print('setConfig error ' + str(e))

def getConfig():
    try:
        global houseEdge
        global referralRate
        global maxPayoutOnWin
        global maxwin

        configSnap = configRef.get()
        houseEdgeDatabase =  configSnap['houseEdge']
        referralRateDatabase = configSnap['referralRate']
        maxPayoutOnWinDatabase = configSnap['maxPayoutOnWin']

        maxPayoutOnWinDatabase = maxPayoutOnWinDatabase + 5.000 #Buffer 5 
        maxwinDatabase = {'STEEM': maxPayoutOnWinDatabase, 'SBD': maxPayoutOnWinDatabase}
        houseEdge = houseEdgeDatabase
        referralRate = referralRateDatabase
        maxPayoutOnWin = maxPayoutOnWinDatabase
        maxwin = maxwinDatabase
        
        printX('getConfig houseEdge ' + str(houseEdge) + " referralRate " + str(referralRate) + " maxPayoutOnWin " + str(maxPayoutOnWinDatabase) + str(maxwin))
        return houseEdge
    except Exception as e:
        print('getConfig error ' + str(e))

def setHash(serverSeedHash):
    try:
        global uniqueHashKeyOld
        global uniqueHashKeyNew
        global isFirstTime  
        global activeUTCServedSeedInSecond

        newRef = hashRef.push()
        uniqueHashKeyNew = newRef.key
        if isFirstTime == 1:
            uniqueHashKeyOld = uniqueHashKeyNew
            isFirstTime = 0
        activeUTCServedSeedInSecond =  getDateTime()
        hashRef.child(uniqueHashKeyNew).set({
            'unixTimeStamp' : getUnix(),
            'serverSeedHash': serverSeedHash,
            'serverSeed': "not-yet-release",
        })
    except Exception as e:
        print('setHash error ' + str(e))

def updateServerSeed(serverSeedHash , serverSeed , uniqueKey):
    try:
        hashRef.child(uniqueKey).update({
            'serverSeed': serverSeed,
        })
    except Exception as e:
        print('updateServerSeed error ' + str(e))     


def deleteServerSeed(uniqueKey):
    try:
        hashRef.child(uniqueKey).delete()
        # hashRef.delete()
    except Exception as e:
        print('deleteServerSeed error ' + str(e))  


def getSpecialHash():
    try:
        specialHashRef = ref.child('specialHash/')
        specialSnap = specialHashRef.get()
        specialHashSeed =  specialSnap['special']['serverSeedHash']
        return str(specialHashSeed)
    except Exception as e:
        print('getSpecialHash error ' + str(e)) 

def getSpecialSeed():
    try:
        specialHashRef = ref.child('specialHash/')
        specialSnap = specialHashRef.get()
        specialSeed =  specialSnap['special']['serverSeed']
        return str(specialSeed)
    except Exception as e:
        print('getSpecialSeed error ' + str(e))

def setSpecialHash(serverSeedHash , serverSeed):
    try:
        specialHashRef.child("special").set({
            'unixTimeStamp' : getUnix(),
            'serverSeedHash': serverSeedHash,
            'serverSeed': serverSeed,
        })
    except Exception as e:
        print('setHash error ' + str(e))     

def setRestriction(countryCode):
    try:
        restrictionRef.child("country").push().set({
            'countryCode' : countryCode
        })
    except Exception as e:
        print('setRestriction error ' + str(e))                      

def getReferral(playerName):
    try:
        referralRef = ref.child('Referral/Player/' + playerName)
        referralUserSnap = referralRef.get()
        if referralUserSnap is not None:
            inviter =  referralUserSnap['inviter']
            printX("inviter " + inviter)
            return inviter
        else:
            return None    
    except Exception as e:
        print('getReferral error ' + str(e))

def setReferralAmount(inviter, player,amountPlayed ,payout ,JsonTransaction , unixTimestamp , dateTime , asset , result , prediction , multiplier , won , referralPayout):
    try:
        ref.child("Referral/Transaction/" +inviter +"/" + player).push().set({
            'inviter' : inviter,
            'player' : player,
            'amountPlayed' : amountPlayed,
            'payout' : payout,
            'JsonTransaction' : JsonTransaction,
            'unixTimestamp' :unixTimestamp,
            'date' : dateTime,
            'asset' : asset,
            'result' : result,
            'prediction' : prediction,
            'multiplier' : multiplier,
            'won' : won,
            'referralPayout' : referralPayout
        })
    except Exception as e:
        print('setReferralAmount error ' + str(e))   

def setHouseFund():
    try:
        account = Account(watching)
        availableBal = account.available_balances
        steemBal = account.available_balances[0]
        SBDBal = account.available_balances[1]

        houseFundRef.child(watching).set({
            'houseAccName' : watching,
            'sbdBal' : SBDBal,
            'steemBal' : steemBal,
            'availableBal' : availableBal,
            'unixTimestamp' : getUnix()
        })
    except Exception as e:
        print('setHouseFund error ' + str(e))    


def setUserBetContest(username , sbd , steem):
    try:
        betContestRef.child(username).set({
            'sbd': sbd,
            'steem': steem,
            'count' : 0
        })
    except Exception as e:
        print('setUserBetContest error ' + str(e))        

def updateUserBetContest(username , sbd , steem , unixTimeStamp):
    try:
        contestSnapshot = betContestRef.child(username).get()
        if contestSnapshot is not None:
            sbdContest = contestSnapshot['sbd']
            steemContest = contestSnapshot['steem']
            countContest = contestSnapshot['count']

            updatedSteem = steemContest + steem
            updatedSbd = sbdContest + sbd
            updatedTotal = updatedSteem + updatedSbd
            updatedCount = countContest + 1

            updatedTotal = float_round(updatedTotal, 3, round)
            updatedSbd = float_round(updatedSbd, 3, round)
            updatedSteem = float_round(updatedSteem, 3, round)

            betContestRef.child(username).update({
                'sbd': updatedSbd,
                'steem': updatedSteem,
                'count' : updatedCount,
                'totalWager' : updatedTotal,
                'unixTimeStamp': unixTimeStamp,
            })
        else:
            betContestRef.child(username).set({
            'sbd': sbd,
            'steem': steem,
            'totalWager' : steem + sbd,
            'count' : 1,
            'unixTimeStamp': unixTimeStamp,
            'ranking': 99999
        })   
    except Exception as e:
        print('updateUserBetContest error ' + str(e))
   
def storeForToken(refBlockNumber, refTransactionId, asset, amount, user, unixTimeStamp):
    try:
        tokenTransactionsRef.push().set({
            'refBlockNumber': refBlockNumber,
            'refTransactionId': refTransactionId,
            'asset': asset,
            'amount': amount,
            'user': user,
            'unixTimeStamp': unixTimeStamp,
            'token' : 0,
            'tokenDistributed' : False
        })
    except Exception as e:
        print('storeForToken Error !!! ' + str(e))

# *****************************************************************************************************************************************

wif = "<insert your active key>"

# connect node and private active key
client = steem.Steem(nodes=['https://appbase.buildteam.io'], keys=[wif])

database = "./dicedb.db"
conn = sqlite3.connect(database)
c = conn.cursor()

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as error:
        print(error)

    return None


def printX(data):
    if IS_SHOW_LOG:
        print(str(data))


def getUnix():
    d = datetime.utcnow()
    unixtime = calendar.timegm(d.utctimetuple())
    return unixtime

def getDateTime():
    utc_dt = datetime.now(timezone.utc)  # UTC time
    dt = utc_dt.astimezone()  # local time
    # print('dt ' + str(dt) + " utc_dt " + str(utc_dt))
    return str(dt)

def getUTCTime():
    utc_dt = datetime.now(timezone.utc)  # UTC time
    return str(utc_dt)

def getHourUTCTime():
    utc_dt = str(datetime.now(timezone.utc))  # UTC time
    indexOfColonSecond = utc_dt.index(":")
    secondOfUTC = utc_dt[indexOfColonSecond-2:indexOfColonSecond]
    return str(secondOfUTC)

def getSecondUTCTime():
    utc_dt = str(datetime.now(timezone.utc))  # UTC time
    indexOfColonSecond = utc_dt.index(":")
    secondOfUTC = utc_dt[indexOfColonSecond+4:indexOfColonSecond+6]
    return str(secondOfUTC)

def getMinuteUTCTime():
    utc_dt = str(datetime.now(timezone.utc))  # UTC time\
    indexOfColonSecond = utc_dt.index(":")
    minuteOfUTC = utc_dt[indexOfColonSecond+1:indexOfColonSecond+3]
    return str(minuteOfUTC)

# with param
def getHourUTCTimeWithParam(utc_dt):
    # utc_dt = str(datetime.now(timezone.utc))  # UTC time
    indexOfColonSecond = utc_dt.index(":")
    secondOfUTC = utc_dt[indexOfColonSecond-2:indexOfColonSecond]
    return str(secondOfUTC)

def getSecondUTCTimeWithParam(utc_dt):
    # utc_dt = str(datetime.now(timezone.utc))  # UTC time
    indexOfColonSecond = utc_dt.index(":")
    secondOfUTC = utc_dt[indexOfColonSecond+4:indexOfColonSecond+6]
    return str(secondOfUTC)

def getMinuteUTCTimeWithParam(utc_dt):
    # utc_dt = str(datetime.now(timezone.utc))  # UTC time\
    indexOfColonSecond = utc_dt.index(":")
    minuteOfUTC = utc_dt[indexOfColonSecond+1:indexOfColonSecond+3]
    return str(minuteOfUTC)

def convertUnixToTime(unixTime):
    utc = datetime.fromtimestamp(unixTime)
    indexOfPlusUnix= utc.index("+")
    indexOfColonUnix = utc.index(":")
    secondOfResult = utc[indexOfColonUnix+4:indexOfPlusUnix]
    return secondOfResult
    

def converter(object_):
    if isinstance(object_, datetime.datetime):
        return object_.__str__()


def float_round(num, places=0, direction=floor):
    return direction(num * (10**places)) / float(10**places)

def clientTransfer(sender, recipient, amount, memo):
    if 'STEEM' in amount:
        # get STEEM transfer amount
        asset = 'STEEM'
        amount = amount[:-6]
    else:
        # get SBD transfer amount
        asset = 'SBD'
        amount = amount[:-4]

    client.transfer(recipient, float(amount), asset, memo, sender)
    printX("{} return transfer to {}".format(sender, recipient + " " + amount))

def selectDb():
    c.execute("SELECT * FROM last_check;")
    blockheight = c.fetchall()
    startblock = blockheight[0][0]

def getAssetFromAmount(amount):
    asset = amount[-5:]
    if asset != 'STEEM':
        asset = amount[-3:]
    return asset


def isWatchingAccountSufficient(amountHost, assetHost):
    account = Account(watching)
    availableBal = account.available_balances
    steemBal = str(account.available_balances[0])
    SBDBal = str(account.available_balances[1])

    steemBal = float(str(steemBal[:-6]))
    SBDBal = float(str(SBDBal[:-4]))

    if assetHost in 'STEEM':
        if steemBal > amountHost:
            return True
        else:
            return False
    elif assetHost in 'SBD':
        if SBDBal > amountHost:
            return True
        else:
            return False

    return False

def processActiveBet(houseEdgeParam , referralRateParam):
    # get active bets
    c.execute("SELECT block, txid, user, amount, bet, asset, hashServerSeed , serverSeed , clientSeed FROM percentagebets WHERE processed IS NOT 1 AND won IS NOT 0")
    bets = c.fetchall()
    for bet in bets:
        block = bet[0]
        txid = bet[1]
        user = bet[2]
        amount = bet[3]
        memo = bet[4]
        asset = bet[5]

        printX('$$$$$$$$$$$$$$ Processing Bet $$$$$$$$$$$$$$$$$$$$$$$')
        printX('block ' + str(block))
        printX('txid ' + str(txid))
        printX('user ' + user)
        printX('amount ' + str(amount))
        printX('memo ' + memo)
        printX('asset ' + asset)

        result = 1000000
        offset = 0
        length = 5
        endValue = offset + length

        # Most crucial part of entire program, it calculates result of bet based on transactionID , this code is same as Javascript found on the website Fairness tab
        while result > 999999:
            try:
                chop = txid[offset:endValue]
                offset += 5
                endValue = offset + length
                result = int(chop, 16)
                printX('chop ' + chop)
                printX('txid ' + txid)
                printX('result ' + str(result))

                try:
                    tempResult = result % (10000)/100
                    printX('Below Rounding Result : ' + str(tempResult))
                    tempResult = int(round(tempResult))
                    printX('After Rounding Result : ' + str(tempResult))
                    if tempResult == 0:
                        printX('tempResult is zero .. trying next 5 char ')
                        result = 1000000
                except Exception as e:
                    print('error '+ str(e))
            except:
                result = -1

        won = 0
        factor = 0
        if result > -1:
            result = tempResult
            processed = True
            try:
                details = memo
                prediction = ""
                details = str(details).lower()
                rate = 0
                betType = 0
                if 'over' in details:
                    indexOfSpace = memo.index(" ")
                    rate = int(memo[indexOfSpace:indexOfSpace + 3])
                    prediction = memo[:5+3]
                    betType = 1
                    factor = 100 - rate
                    if result > rate:
                        won = 1
                elif 'above' in details:
                    indexOfSpace = memo.index(" ")
                    rate = int(memo[indexOfSpace:indexOfSpace+ 3])
                    prediction = memo[:6+3]
                    betType = 1
                    factor = 100 - rate
                    if result > rate:
                        won = 1
                elif 'below' in details or 'under' in details:
                    indexOfSpace = memo.index(" ")
                    rate = int(memo[indexOfSpace:indexOfSpace + 3])
                    prediction = memo[:6+3]
                    betType = 2
                    factor = 0 + rate - 1
                    if result < rate:
                        won = 1
                else:
                    factor = 0   
            except:
                factor = 0

            printX('factor ' + str(factor))
            printX('won ' + str(won))
            printX('houseEdgeParam ' + str(houseEdgeParam))
            payout = 0
            multiplier = (100/factor) * ( 1 - houseEdgeParam)
            multiplier = float_round(multiplier, 2, round)
            printX('multiplier ' + str(multiplier))

            if won == 1 and factor > 0:
                processed = False
                payout = (float(amount) * 100/factor) * (1 - houseEdgeParam)
                payout = float_round(payout, 3, round)
                try:
                    transactionJSON = {}
                    transactionJSON["diceRolled"] = str(result)
                    transactionJSON["TransactionId"] = txid
                    transactionJSON["BlockNumber"] = str(block)
                    transactionJSON["isValid"] = True

                    clientTransfer(watching, user, str(payout) + " " + asset, 'You have Won! Dice Rolled: ' + str(result) + ". Your Prediction: " + prediction + ". Multiplier: " +  str(multiplier) + ". Win Chance: " + str(factor)+ "%" + '\n' + json.dumps(transactionJSON))
                    print('>>>>>>>>>>  ' + user + ', You Won! . Dice Roll : ' + str(result) + " Your Prediction: " + prediction + ". Multiplier: " +  str(multiplier) + ". Win Chance: " + str(factor)+ "%" + '\n' + json.dumps(transactionJSON) + " amount " + str(amount) + " currency " + asset)
               
                except Exception as e:
                    print('ERROR SENDING MONEY ' + str(e))
            elif won == 0:
                payout = 0.001
                try:
                    transactionJSON = {}
                    transactionJSON["diceRolled"] = str(result)
                    transactionJSON["TransactionId"] = txid
                    transactionJSON["BlockNumber"] = str(block)
                    transactionJSON["isValid"] = True
                    clientTransfer(watching, user, str(payout) + " " + asset, 'You Lost. Dice Rolled: ' + str(result) + ". Your Prediction: " + prediction + ". Multiplier: " +  str(multiplier) + ". Win Chance: " + str(factor)+ "%" + '\n' + json.dumps(transactionJSON))
                    print('>>>>>>>>>> ' + user + ', You Lost. Dice Roll : ' + str(result) + " Your Prediction: " + prediction + ". Multiplier: " +  str(multiplier) + ". Win Chance: " + str(factor)+ "%" + '\n' + json.dumps(transactionJSON) + " amount " + str(amount) + " currency " + asset)
                  
                except Exception as e:
                     print('ERROR SENDING MONEY 2 ' + str(e))        

            processed = True
            unsaved = 1
            try:
                inviterName = getReferral(user)
                if inviterName is not None:
                    printX("houseEdgeParam " + str(houseEdgeParam) + " referralRateParam " + str(referralRateParam) + " amount " + str(amount))
                    referralPayout = (float(amount)) * (houseEdgeParam) * referralRateParam
                    referralPayout = float_round(referralPayout, 5, round)
                    setReferralAmount(inviterName ,user , float(amount)  , str(payout) , json.dumps(transactionJSON) , getUnix() ,getDateTime() , asset , str(result) , prediction , str(multiplier) , won , referralPayout)
            except Exception as e:
                print("setReferralAmount error " + str(e))

            while unsaved == 1:
                try:
                    with conn:
                        c.execute("UPDATE percentagebets SET result=?, won=?, processed=? WHERE block=? AND txid=?",
                                  (result, float(won), processed, block, txid))
                    unsaved = 0
                    printX('Updated percentagebets Succesfully')
                except Exception as e:
                    print('ERROR SAVING TO DATABASE! ' + str(e))

            storeDatabase(str(result), str(block), txid,  prediction, asset, amount, user,
                          factor, rate, won, payout, getUnix(), getDateTime(), multiplier, betType)
           
            if asset == "STEEM" :
                updateUserBetContest(user , 0 , amount , getUnix())   
            else:
                updateUserBetContest(user , amount , 0 , getUnix())   
    conn.commit()


def main():
    checkPoint()
    
    startblock = 0
    try:
        conn = create_connection(database)
        if conn is not None:
            printX('###########################')
            printX('#### Database connected #####')
            printX('###########################')

        c = conn.cursor()

        c.execute("SELECT blockheight FROM last_check")
        last_check = c.fetchall()
        startblock = last_check[0][0]
      

    except Exception as error:
        conn.close()
        print(error)
        if startblock is None or startblock == 0:
            startblock = int(input("Please insert initial block number."))
            try:
                with conn:
                    c.execute(
                        '''INSERT OR IGNORE INTO last_check (blockheight) VALUES (?)''',  (startblock,))

            except Exception as e:
                print('ERROR UPDATING BLOCKHEIGHT 1 ' + str(e))
            startblock = int(startblock)

    getblock = startblock

    go = True
    while go == True:
        # Block was read based on block number and always trying to catch the latest block.
        try:
            blockchain = Blockchain()
            print('Block : ' + str(getblock))
        except:
            print("Latest Block")
        try:
            block = Block(getblock)
        except:
            block = None
            printX('###########################')
            printX('#### End of Block #########')
            printX('###########################')
        
        try:
            if getblock % retrieveInterval == 0:
                retrieveBlackList()
                checkPoint()
                getConfig()
                setHouseFund()

            if getblock % 200 == 0 :
                resetSoftBannedCount()       
        except Exception as e:
            print('Error get blacklist ' + str(e))

        # Iterating each transaction on every block to check any transaction is send to @epicdice, then storing all crucial value into global variable which later will be stored into local database for processing.
        if block != None:
            for i, txs in enumerate(block.transactions):
                for (j, tx) in enumerate(txs['operations']):
                    if tx['type'] == 'transfer_operation' and tx['value']['to'] in [watching]:
                        if tx != None:
                            transId = txs['transaction_id']
                            precision = str(tx['value']['amount']['precision'])
                            nai = tx['value']['amount']['nai']
                            fromWho = tx['value']['from']
                            toWho = tx['value']['to']
                            amount = tx['value']['amount']['amount']
                            ref_block_num = txs['ref_block_num']
                            transaction_num = txs['transaction_num']
                            block_num = txs['block_num']
                            memo = tx['value']['memo']
                            transType = tx['type']

                            finalAmount = (float(amount) * 0.1 **
                                           float(precision)) * 100 / 100
                            finalAmount = float_round(finalAmount, 3, round)

                            if '@@000000013' in nai:
                                finalAmountWithAsset = str(
                                    finalAmount) + ' SBD'
                                asset = 'SBD'
                            else:
                                finalAmountWithAsset = str(
                                    finalAmount) + ' STEEM'
                                asset = 'STEEM'

                        else:
                            print('is None')

                        sender = fromWho
                        factor = 0

                        try:
                            details = memo
                            betType = 0

                            details = str(details).lower()
                            rate = 0
                            if 'over' in details:
                                indexOfSpace = memo.index(" ")
                                rate = int(memo[indexOfSpace:indexOfSpace + 3])
                                factor = 100 - rate
                                betType = 1
                            elif 'above' in details:
                                indexOfSpace = memo.index(" ")
                                rate = int(memo[indexOfSpace:indexOfSpace + 3])
                                factor = 100 - rate
                                betType = 1
                            elif 'below' in details or 'under' in details:
                                try:
                                    indexOfSpace = memo.index(" ")
                                    rate = int(memo[indexOfSpace:indexOfSpace+3])
                                    printX("indexOfSpace " + str(indexOfSpace))    
                                except Exception as e:
                                      print('failed ' + str(e))  
                                factor = 0 + rate - 1
                                betType = 2
                            else:
                                factor = 0  
                        except Exception as e:
                            print('Exception ' + str(e))
                            factor = 0

                        printX(
                            '**************************  Bet Found ***********************************')
                        printX('Transaction : ' + str(tx))
                        printX('transType : ' + transType)
                        printX('fromWho : ' + fromWho)
                        printX('toWho : ' + toWho)
                        printX('amount : ' + amount)
                        printX('finalAmount : ' + str(finalAmount))
                        printX('finalAmountWithAsset : ' + finalAmountWithAsset)
                        printX('precision : ' + str(precision))
                        printX('nai : ' + nai)
                        printX('memo : ' + memo)
                        printX('rate ' + str(rate))
                        printX('factor ' + str(factor))
                        printX('ref_block_num ' + str(ref_block_num))
                        printX('block_num ' + str(block_num))
                        printX('transaction_num ' + str(transaction_num))
                        printX('transId ' + str(transId))

                        if factor > 0:
                            # Calculation of the possible winning payout and go through a series of validation checking.
                            win = (float(finalAmount) * 100/factor) * ( 1 - houseEdge)
                            win = float_round(win, 3, round)

                            if sender in userList:
                                printX('Found in blacklisted*****')
                            else:
                                if float(finalAmount) < minbet:
                                    printX('Sorry, Minimum bet is ' + str(minbet))
                                    clientTransfer(watching, sender , str(finalAmountWithAsset), 'Refund invalid bet. Minimum bet is ' + str(minbet) + ' . ' + str(potentialBlackListChecking(sender)) + ' more invalid bets will get your account permanently blacklisted.')
                                elif win > maxwin[asset]:
                                    clientTransfer(watching, sender, str(finalAmountWithAsset), 'Refund invalid bet. The maximum amount you can win in one game is '+str(maxwin[asset])+' '+asset + ' . ' + str(potentialBlackListChecking(sender)) + ' more invalid bets will get your account permanently blacklisted.')
                                    printX('Sorry, the maximum amount you can win in one game is ' + str(maxwin[asset])+' '+asset)
  
                                elif not isWatchingAccountSufficient(finalAmount, asset):
                                    clientTransfer(watching, sender, str(finalAmountWithAsset), 'Sorry, Host insufficient fund. Refund Your Bet. Refund initiated')
                                    printX('Host insufficient fund.')
                                else:
                                    error = 0

                                    if betType == 1:
                                        if rate < minRate or rate >= 96:
                                            error = 1
                                            clientTransfer(watching, sender, str(finalAmountWithAsset), 'Refund invalid Bet. Cannot bet below  6 or above 96. ' + str(potentialBlackListChecking(sender)) + ' more invalid bets will get your account permanently blacklisted.')
                                            printX('Below min rate or over 100')
                                    elif betType == 2:
                                        if rate > maxRate or rate <= 1:
                                            error = 1
                                            clientTransfer(watching, sender, str(finalAmountWithAsset), 'Refund invalid Bet. Cannot bet above 95 or below 1. ' +  str(potentialBlackListChecking(sender)) + ' more invalid bets will get your account permanently blacklisted.')
                                            printX('Exceeded max rate or below 1')
                                    if error == 0:
                                        # store valid bet into local database
                                        try:
                                            with conn:
                                                c.execute('''INSERT OR IGNORE INTO percentagebets (block, txid, user, amount, bet, asset, hashServerSeed, serverSeed , clientSeed) VALUES (?,?,?,?,?,?,?,?,?)''', (
                                                    getblock, transId, sender, finalAmount, memo, asset , "" , "" , "" ))
                                                printX(
                                                    'Insert to database succesfully !!!')
                                        except Exception as e:
                                            print('ERROR INSERTING BET ' + str(e))
                                            print('Sorry, Your bet is invalid 1')
                                            clientTransfer(watching, sender, str(finalAmountWithAsset), 'Refund invalid Bet. ' + str(potentialBlackListChecking(sender)) + ' more invalid bets will get your account permanently blacklisted.')
                                
                        else:
                            print('Generic exception !!!')
            getblock = getblock + 1
        else:
            go = False
        try:
            with conn:
                c.execute('''UPDATE last_check SET blockheight=?''', (getblock,))
        except Exception as e:
            conn.close()
            print('ERROR UPDATING BLOCKHEIGHT 2 ' + str(e))
        processActiveBet(houseEdge , referralRate) 
    return getblock


if __name__ == "__main__":
    initialControlCount = getControlCount()
    initialControlCount = initialControlCount + 1
    setControlCount(initialControlCount)
    
    registerListener()
    getConfig()

    updateIsLatestBlock(False)
    lastblock = 0
    blockstall = 0
    retrieveBlackList()

    while True:
        block = main()
        if block == lastblock:
            blockstall = blockstall + 1
        else:
            blockstall = 0
            lastblock = block
            updateIsLatestBlock(True)

        if blockstall > 3:
            sys.exit()
        time.sleep(2)

@atexit.register
def goodbye():
    controlRef.listen(None)
    printX("You are now leaving the Python sector.")

atexit.register(goodbye)
