# -*- coding: utf-8 -*-
import sys
import streamfilters
import json
from datetime import datetime
import pymongo
# import logger - logging suppport


def insertMongo(twitterResponseJSON, trendId, db):
    tweetJSON = json.loads(twitterResponseJSON)

    ret = "[RAW]: " + str(tweetJSON)

    if limitInfo(tweetJSON):
        return ret

    try:
        ret += "\n\n" + addUser(tweetJSON, trendId, db) + "\n\n" + addTweet(tweetJSON, trendId, db) + "\n\n\n\n\n\n"
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        ret = 'Exception Masked', str(sys.exc_info()[0])
        raise

    return ret


def addTweet(tweetJSON, trendId, db):
    if not englishOnly(tweetJSON):
        return '[NON-EN]! ' + tweetJSON['text']

    ret = ""
    if isRetweet(tweetJSON):
        #  return '[RETWEET] ' + tweetJSON['text']
        ret += '[RETWEET] [PASS]'

    ret += "[TWEET]: "
    tweet = fetchTweet(tweetJSON, trendId, db)
    newtweet = False
    if tweet is None:
        newtweet = True
        tweet = parseTweet(tweetJSON)
        ret += "[NEW]: "
    else:
        ret += '[DUP]: '

    pushed = pushTrendInto(tweet, trendId)
    if newtweet or pushed:
        tweets = db.tweets
        upsert(tweet, tweets)

    ret += str(tweet)
    return ret


def addUser(tweetJSON, trendId, db):
    user = fetchUser(tweetJSON, trendId, db)
    newuser = False
    ret = "[USER]: "
    if user is False:
        ret = "NO USER FOUND"
        return ret
    if user is None:
        newuser = True
        user = parseUser(tweetJSON)
        ret = "[NEW]: "
    else:
        ret = "[DUP]: "

    pushed = pushTrendInto(user, trendId)

    tweetId = str(tweetJSON['id_str'])
    tweetRecorded = pushTweetForUser(user, tweetId)

    if newuser or pushed or tweetRecorded:
        users = db.users
        upsert(user, users)

    ret = str(user)
    return ret


def addTrend(trendstr, db):
    trend = fetchTrend(trendstr, db)
    if trend is None:
        print "[NEW]: "
        trends = db.trends
        trendId = trends.count() + 1        # How to find auto incrementing id?
        trend = {"_id": trendstr, "trendId": trendId}
        upsert(trend, trends)
        return trendId
    else:
        return str(trend['trendId'])


def upsert(doc, coll):
    coll.save(doc, manipulate=False, safe=True)

# ################################# TREND OPS ##################################


def fetchTrend(trend, db):
    trends = db.trends
    t = trends.find_one({'_id': trend})
    return t


def fetchTrendId(trend, db):
    t = fetchTrend(trend, db)
    if t is None:
        return -1
    else:
        return t['trendId']


def getTweetsCursor(trend, db, filters = None, limit = None):
    tId = fetchTrendId(trend, db)
    tweets = db.tweets
    query = {"trends": str(tId)}
    if not filters:
        print "No filter provided. Fetching ALL Tweets."
    else:
        query.update(filters)

    cursor = None
    if not limit or type(limit) is not type(int()):
        cursor = tweets.find(query).sort('_id', pymongo.ASCENDING)
    else:
        cursor = tweets.find(query).sort('_id', pymongo.ASCENDING).limit(limit)

    print "CURSOR QUERY:", query
    print "CURSOR COUNT:", cursor.count()
    return cursor


def pushTrendInto(jsonModel, trendId):
    if 'trends' not in jsonModel:
        jsonModel['trends'] = []

    if trendId not in jsonModel['trends']:
        jsonModel['trends'].append(trendId)
        return True
    else:
        return False


def pushTweetForUser(userJSON, tweetId):
    if 'tweets' not in userJSON:
        userJSON['tweets'] = []

    if tweetId not in userJSON['tweets']:
        userJSON['tweets'].append(tweetId)
        return True
    else:
        return False


# Unused
def seenForTrend(jsonModel, trendId):
    trends = jsonModel['trends']
    if trends is None:
        return False
    else:
        return trendId in trends

# ################################# TWEET OPS ##################################
# Tweet obj:
#     * user_id,
#     * text,
#     * id_str,
#     * lang,
#     * coord,
#     * loc,
#     * created_at,
#     * trend_ids[]


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


def parseTweet(tweetJSON):
    parsedTweet = {}
    tweet_text = tweetJSON['text']
    parsedTweet['text'] = tweet_text

    tokenizedTweet = streamfilters.processTweetText(tweet_text)
    parsedTweet['tokens'] = tokenizedTweet

    parsedTweet['_id'] = str(tweetJSON['id_str'])
    parsedTweet['lang'] = str(tweetJSON['lang'])
    if tweetJSON['coordinates'] is not "":
        parsedTweet['coord'] = str(tweetJSON['coordinates'])
    if tweetJSON['geo'] is "":
        parsedTweet['loc'] = str(tweetJSON['user']['location'])
    else:
        parsedTweet['loc'] = tweetJSON['geo']
    parsedTweet['created_at'] = tweetJSON['created_at']
    date = datetime.strptime(parsedTweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    parsedTweet['timestamp'] = date
    parsedTweet['user_id'] = str(tweetJSON['user']['id'])
    # parsedTweet['retweeted'] = tweetJSON['retweeted']
    # parsedTweet['retweeted_id'] = ''
    # if tweetJSON['retweeted'] and 'retweeted_status' in tweetJSON:
    #     if 'id_str' in tweetJSON['retweeted_status']:
    #         parsedTweet['retweeted_id'] = tweetJSON['retweeted_status']['id_str']
    return parsedTweet


def fetchTweet(tweetJSON, trendId, db):
    # log refetching
    tweetId = tweetJSON['id_str']
    tweets = db.tweets
    tweet = tweets.find_one({'_id': tweetId})
    return tweet

# ################################# USER OPS ##################################
# User obj:
#     * id_str,
#     * location,
#     * name,
#     * screen_name,
#     * trend_ids [],


def parseUser(tweetJSON):
    parsedUser = {}
    parsedUser['_id'] = str(tweetJSON['user']['id'])
    parsedUser['loc'] = tweetJSON['user']['location']
    parsedUser['name'] = tweetJSON['user']['name']
    parsedUser['handle'] = tweetJSON['user']['screen_name']
    return parsedUser


def fetchUser(tweetJSON, trendId, db):
    user = None
    try:
        userId = tweetJSON['user']['id']
        users = db.users
        user = users.find_one({'_id': userId})
    except:
        print "Exception in finding user:"
        print tweetJSON
        user = None
    return user
