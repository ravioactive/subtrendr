# -*- coding: utf-8 -*-
import re
import os
import pymongo
import datetime
import keys
import time

global inited
inited = False


def init(trend, keyset = 1):

    if isInit():
        return

    if keyset not in keys.keychain:
        print "Error: Keys " + str(keyset) + " not found in keychain. Using default."
        keyset = keys.keychain["default"]
    global consumer_key
    consumer_key = keys.keychain[keyset]["consumer_key"]
    global consumer_secret
    consumer_secret = keys.keychain[keyset]["consumer_secret"]
    global access_token
    access_token = keys.keychain[keyset]["access_token"]
    global access_token_secret
    access_token_secret = keys.keychain[keyset]["access_token_secret"]

    # mongo connection
    connection_string = "mongodb://localhost"
    connection = pymongo.MongoClient(connection_string)
    global db
    db = connection.subtrendr
    print type(db)

    global stopwords_list    
    stopwords_list = getAllStopwords()
    trend_stopword_list = getTrendStopWords(trend)
    stopwords_list.append(trend_stopword_list)
    global slangDict
    # slangDict=getSlangDictionary()
    global logfile
    logfile = None
    logfile = getLogFile(trend)
    global ts_beg
    ts_beg = datetime.datetime.now()


    inited = True


def isInit():
    return inited


def getUptime():
    ts_now = datetime.datetime.now()
    ts_diff = ts_now - ts_beg
    return ts_diff


def getTrendStopWords(trend):
    lines = []
    try:
        trendStopWordsFilePath = os.path.join(os.path.join(os.path.abspath(os.path.pardir), 'stopwords'), trend+'_stopwords.txt')
        f = open(trendStopWordsFilePath, 'r')
        lines = f.read().splitlines()
        f.close()
    except IOError:
        print "No stopwords given for this trend at " + trendStopWordsFilePath
        pass

    return lines


def getAllStopwords():
    allStopWordsFilePath = os.path.join(os.path.join(os.path.abspath(os.path.pardir), 'stopwords'), 'all_stopwords.txt')
    f = open(allStopWordsFilePath, 'r')
    lines = f.read().splitlines()
    f.close()
    return lines


def getSlangDictionary():
    allSlangWordsFilePath = os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath(os.path.pardir), 'src'), 'res'), 'slangwords'), 'all_slangwords.txt')
    f = open(allSlangWordsFilePath, 'r')
    keyvalues = {k: v for (k, v) in [slw.split(':') for slw in f]}
    f.close()
    return keyvalues



def getLogFile(trend = ""):
    global logfile
    if logfile is not None:
        return logfile

    trendLogFileName = trend + "_current.log"
    logDir = os.path.join(os.path.abspath(os.path.pardir), 'logs')
    stdlogfilename = os.path.join(logDir, trendLogFileName)
    stdlogfilefound = os.path.isfile(stdlogfilename)
    if(stdlogfilefound):
        ts_suffix = datetime.datetime.fromtimestamp(os.path.getctime(stdlogfilename)).strftime("%Y-%m-%d-%H-%M-%S")
        logfilename = os.path.join(logDir, "log_" + trend + ts_suffix + ".log")
        i = 1
        while os.path.isfile(logfilename):
            logfilename = os.path.join(logDir, "log_" + trend + ts_suffix + "_" + str(i) + ".log")
            i += 1

        os.rename(stdlogfilename, logfilename)

    # currlogFilePath = os.path.join(logDir, stdlogfilename)
    # print "currlogFilePath", currlogFilePath
    # print "stdlogfilename", stdlogfilename
    # print "is current.log still there?", os.path.isfile(stdlogfilename)
    if os.path.isfile(stdlogfilename):
        datetime.datetime.fromtimestamp(os.path.getctime(stdlogfilename)).strftime("%Y-%m-%d-%H-%M-%S")
    f = open(os.path.join(logDir, trendLogFileName), "w+")
    logfile = f
    return f


def destroy():
    logfile.close()
    print "CLOSED LOG FILE"


if __name__ == '__main__':
    init('test', 1)