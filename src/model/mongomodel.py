# -*- coding: utf-8 -*-
import sys
import streamfilters
import json
from datetime import datetime


def insertMongo(twitterResponseJSON, trend, db):
    tweetJSON = json.loads(twitterResponseJSON)

    ret = "[RAW]: " + str(tweetJSON)

    if limitInfo(tweetJSON):
        return ret

    try:
        tweetDoc = addTweet(tweetJSON, trend, db)
        if tweetDoc is None:
            print twitterResponseJSON

        ret += "\n\n" + tweetDoc + "\n\n\n\n\n\n"
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        ret = 'Exception Masked', str(sys.exc_info()[0])
        raise

    return ret


def addNGramsToDictionaries(db, trend, unigrams, bigrams):
    # add to respective dictionaries
    unigramDict = db[trend+'_unigr']
    for uni in unigrams.keys():
        u = unigramDict.find_one({'_id': uni})
        if u is None:
            uid = unigramDict.count()+1
            u = { '_id' : uni, 'ngramid' : uid }
            upsert(u, unigramDict)
    
    bigramDict = db[trend+'_bigr']
    for bi in bigrams.keys():
        b = bigramDict.find_one({'_id': bi})
        if b is None:
            bid = bigramDict.count()+1
            b = { '_id' : b, 'ngramid' : bid }
            upsert(b, bigramDict)

    return


def upsertNGramCounts(db, trend, unigrams, bigrams):
    # This collection will be named uniquely for each trend
    # we have a collection with 
    #    {ngram-id, total, last edited, last total, [{count, time}]}
    # for each ngram. We add this ngram into that collection
    
    now = datetime.utcnow()
    u = None
    unigramCountColl = db[trend+'_unistate']
    for uni in unigrams.keys():
        u = unigramCountColl.find_one({'_id' : uni})
        if u is None:
            u = { '_id' : uni, 'total' : unigrams[uni], 'last_change' : now, 'last_total' : -1}
            u['hist'] = []
        else:
            u['last_total'] = u['total']
            u['total'] += unigrams[uni]
            u['last_change'] = now

        u['hist'].insert(0, (u['total'], now))
        upsert(u, unigramCountColl)

    b = None
    bigramCountColl = db[trend+'_bistate']
    for bi in bigrams.keys():
        b = bigramCountColl.find_one({'_id' : bi})
        if b is None:
            b = { '_id' : bi, 'total' : bigrams[bi], 'last_change' : now, 'last_total' : -1}
            b['hist'] = []
        else:
            b['last_total'] = b['total']
            b['total'] += bigrams[bi]
            b['last_change'] = now

        b['hist'].insert(0, (b['total'], now))
        upsert(b, bigramCountColl)
    return


def addTweet(tweetJSON, trend, db):
    if shouldAddTweet(tweetJSON) is False:
        return "NON ENGLISH"

    tweet = fetchTweet(tweetJSON, trend, db)
    newTweet = False
    if tweet is None:
        newTweet = True
    
    if newTweet == True:
        tweet = parseTweet(tweetJSON)
        addNGramsToDictionaries(db, trend, tweet['unigrams'], tweet['bigrams'])
    
    upsertNGramCounts(db, trend, tweet['unigrams'], tweet['bigrams'])

    if newTweet:
        tweets = db[trend+'_tweets']
        upsert(tweet, tweets)

    return str(tweet)


def upsert(doc, coll):
    coll.save(doc, manipulate=False, safe=True)

################################# TWEET OPS ##################################

def shouldAddTweet(tweetJSON):
    if not englishOnly(tweetJSON):
        return False
    return True


def isRetweet(tweetJSON):
    return tweetJSON['retweeted'] or streamfilters.isRT(tweetJSON['text'])


def limitInfo(tweetJSON):
    if 'limit' in tweetJSON:
        return True
    else:
        return False


def englishOnly(tweetJSON):
    if 'lang' in tweetJSON:
        if tweetJSON['lang'] == 'en':
            return True
        else:
            return False
    else:
        print 'Unknown language'
        return False


# Tweet obj:
#     * text,
#     * id_str,
#     * lang,
#     * created_at
#     * unigrams
#     * bigrams
def parseTweet(tweetJSON):
    parsedTweet = {}
    tweet_text = tweetJSON['text']
    parsedTweet['text'] = tweet_text

    cleansedTweet = streamfilters.processTweetText(tweet_text)
    
    tweetUnigrams = streamfilters.unigramifyTweet(cleansedTweet)
    parsedTweet['unigrams'] = tweetUnigrams

    tweetBigrams = streamfilters.bigramifyTweet(cleansedTweet)
    parsedTweet['bigrams'] = tweetBigrams

    parsedTweet['_id'] = str(tweetJSON['id_str'])
    parsedTweet['lang'] = str(tweetJSON['lang'])
    parsedTweet['created_at'] = tweetJSON['created_at']
    date = datetime.strptime(parsedTweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    parsedTweet['timestamp'] = date
    return parsedTweet


def fetchTweet(tweetJSON, trend, db):
    # log refetching
    tweetId = tweetJSON['id_str']
    tweets = db[trend+'_tweets']
    tweet = tweets.find_one({'_id': tweetId})
    return tweet
