# -*- coding: utf-8 -*-
import re
import os
import pymongo
import datetime
import keys
import time

global inited
inited = False


def init(keyset = 1):

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

    connection_string = "mongodb://localhost"
    connection = pymongo.MongoClient(connection_string)
    global db
    db = connection.trendcom
    print type(db)

    global urlpat
    urlpat = re.compile(r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
    global mentionpat
    mentionpat = re.compile(r"@[^\s]+")
    global hastagpat
    hastagpat = re.compile(r'#([^\s]+)')
    global metapunctpat
    metapunctpat = re.compile('[^a-zA-Z0-9]+')
    global repeatgrp1

    repeatgrp1 = re.compile(r"(.)\1{2,}", re.DOTALL)
    global repeatgrp2
    repeatgrp2 = re.compile(r"(..)\1{2,}", re.DOTALL)
    global repeatsubspat
    repeatsubspat = r"\1\1"

    global stopwords_list
    stopwords_list = getAllStopwords()
    global slangDict
    # slangDict=getSlangDictionary()
    global logfile
    logfile = None
    # logfile = getLogFile()
    global ts_beg
    ts_beg = datetime.datetime.now()


    global ldaObjBasePath
    ldaObjBasePath = getLdaObjBasePath()

    global DICT
    DICT = "d"
    global DICT_FILE_TYPE
    DICT_FILE_TYPE = ".dict"

    global CORPUS
    CORPUS = "c"
    global MM_CORPUS_TYPE
    MM_CORPUS_TYPE = ".mm"
    global BLEI_CORPUS_TYPE
    BLEI_CORPUS_TYPE = ".lda-c"
    global SVMLIGHT_CORPUS_TYPE
    SVMLIGHT_CORPUS_TYPE = ".svmlight"
    global LOW_CORPUS_TYPE
    LOW_CORPUS_TYPE = ".low"

    global MODEL
    MODEL = "m"
    global LDA_MODEL_TYPE
    LDA_MODEL_TYPE = ".lda"

    global num_topics_lda
    num_topics_lda = 35
    global lda_chunk_size
    lda_chunk_size = 2000
    global update_freq
    update_freq = 1
    global passes_corpus
    passes_corpus = 1

    inited = True


def isInit():
    return inited


def validatedLdaFileName(name, extn=""):
    if extn != "":
        name = name + extn
    filepath = os.path.join(ldaObjBasePath, name)
    fullObjName = ""
    if os.path.isfile(filepath):
        fullObjName = filepath
    return fullObjName


def getLdaObjBasePath():
    objPath = os.path.join(os.path.join(os.path.join(os.path.abspath(os.path.pardir), 'code'), 'resources'), 'lda')
    return objPath


def getLdaObjFileName(trend, typeName, **kwargs):
    typeStr, extn = "", ""
    if typeName == DICT:
        typeStr = "_dict_"
        extn = DICT_FILE_TYPE
    elif typeName == CORPUS:
        typeStr = "_corpus_"
        if "extn" in kwargs:
            extn = kwargs["extn"]
        else:
            extn = ""
    elif typeName == MODEL:
        typeStr = "_model_"
        extn = LDA_MODEL_TYPE
    else:
        return ""

    nameonly = trend + typeStr + datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d-%H-%M-%S")
    fullnameonly = os.path.join(ldaObjBasePath, nameonly)
    fullname = fullnameonly + extn

    i = 1
    while(os.path.isfile(fullname)):
        fullname = fullnameonly + "_" + i + extn
        i += 1

    return fullname


def getUptime():
    ts_now = datetime.datetime.now()
    ts_diff = ts_now - ts_beg
    return ts_diff


def getTrendStopWords(trend):
    lines = []
    try:
        trendStopWordsFilePath = os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath(os.path.pardir), 'code'), 'resources'), 'stopwords'), trend+'_stopwords.txt')
        f = open(trendStopWordsFilePath, 'r')
        lines = f.read().splitlines()
        f.close()
    except IOError:
        print "File not found: " + trendStopWordsFilePath

    return lines


def getAllStopwords():
    allStopWordsFilePath = os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath(os.path.pardir), 'code'), 'resources'), 'stopwords'), 'all_stopwords.txt')
    f = open(allStopWordsFilePath, 'r')
    lines = f.read().splitlines()
    f.close()
    return lines


def getSlangDictionary():
    allSlangWordsFilePath = os.path.join(os.path.join(os.path.join(os.path.join(os.path.abspath(os.path.pardir), 'code'), 'resources'), 'slangwords'), 'all_slangwords.txt')
    f = open(allSlangWordsFilePath, 'r')
    keyvalues = {k: v for (k, v) in [slw.split(':') for slw in f]}
    f.close()
    return keyvalues



def getLogFile(trend = ""):
    global logfile
    if logfile is not None:
        return logfile

    trendLogFileName = trend + "current.log"
    logDir = os.path.join(os.path.join(os.path.abspath(os.path.pardir), 'code'), 'logs')
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
