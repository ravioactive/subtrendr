# -*- coding: utf-8 -*-

import re
from unidecode import unidecode
from res import globalobjs

urlpat = re.compile(r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
mentionpat = re.compile(r"@[^\s]+")
hastagpat = re.compile(r'#([^\s]+)')
metapunctpat = re.compile('[^a-zA-Z0-9]+')
repeatgrp1 = re.compile(r"(.)\1{2,}", re.DOTALL)
repeatgrp2 = re.compile(r"(..)\1{2,}", re.DOTALL)
repeatsubspat = r"\1\1"


# ===============ENCODE===============
def encodeStream(tweet):
    #tweet=unicode(tweet,'utf-8')
    #tweet=tweet.encode('utf-8','ignore')
    tweet = unidecode(tweet)
    tweet = tweet.lower()
    return tweet


# ===============CLEANSING===============
def removeMentions(tweet):
    tweet = re.sub(mentionpat, '', tweet)
    return tweet


def removeUrl(tweet):
    tweet = re.sub(urlpat, '', tweet)
    return tweet



def removeHashtags(tweet):
    # tweet = re.sub(hastagpat, r'\1', tweet)
    tweet = re.sub(hastagpat, '', tweet)
    return tweet


def isRT(tweet):
    match = re.search(r"[\s]*(rt|RT)[\W]+", tweet)
    if match:
        return True
    else:
        return False


# ===============TRIMMING===============
def removeMetaPunct(tweet):
    tweet = re.sub(metapunctpat, ' ', tweet)
    return tweet


def replaceRepeats_gt2(tweet_str):
    replacedTokens = []
    word_list = tweet_str.split(' ')
    for token in word_list:
        replacedTokens.append(re.sub(repeatgrp1, repeatsubspat, re.sub(repeatgrp2, repeatsubspat, token)))
    replacedTokens_str = ' '.join([i for i in replacedTokens])
    return replacedTokens_str


def trimTweet(tweet):
    return tweet.strip()


# ===============TOKENIZATION===============
def ngrams(input, n):
  input = input.split(' ')
  output = {}
  for i in range(len(input)-n+1):
    g = ' '.join(input[i:i+n])
    output.setdefault(g, 0)
    output[g] += 1
  return output


def unigramifyTweet(tweet_str):
    unigrams = ngrams(tweet_str, 1)
    return unigrams


def bigramifyTweet(tweet_str):
    bigrams = ngrams(tweet_str, 2)
    return bigrams


# ===============STOPWORDS===============

def removeStopWords(tweet_str):
    #print "EMPTY" if not globalobjs.stopwords_list else "FULL"
    word_list = tweet_str.split(' ')
    after_stopwords = ' '.join([i for i in word_list if i not in globalobjs.stopwords_list])
    return after_stopwords


# ===============SLANGS===============

def translateSlangs(tweet_tokens):
    return [subel for sub in [globalobjs.slangDict[tok].split() if tok in globalobjs.slangDict and globalobjs.slangDict[tok] is not '' else [tok] for tok in tweet_tokens] for subel in sub]


# ===============BINDER FUNCTION===============
#   [Y]encode -> [Y]trim -> [Y]urls -> [Y]mentions -> [Y]hashtags ->
#                [Y]punctuation -> [Y]metachar -> [Y]trim ->
#   [Y]tokenize ->
#                [N]slangs -> [Y]replaceGT2 -> [N]slangs -> [Y]stopwords

def processTweetText(tweet):
#   [Y]encode ->
    tweet = encodeStream(tweet)


#   [Y]trim ->
    tweet = trimTweet(tweet)
#   [Y]urls->
    tweet = removeUrl(tweet)
#   [Y]mentions
    tweet = removeMentions(tweet)
#   [Y]hashtags ->
    tweet = removeHashtags(tweet)


#   [Y]punctuation -> [Y]metachar ->
    tweet = removeMetaPunct(tweet)
#   [Y]trim ->
    tweet = trimTweet(tweet)
    
#   [Y]repeats->
    tweet = replaceRepeats_gt2(tweet)
#   [N]slangs->
#   tokens=translateSlangs(tokens)
#   [Y]stopwords->
    tweet = removeStopWords(tweet)

    # return bigram list
    #return tokens
    return tweet



def testTweetProcessor():
    #Works!
    globalobjs.init('test', 1)
    url_test = ["Office For iPhone And Android Is Now Free  http://tcrn.ch/1rH7Fkx  by @alex",
                "1. amazing fit  @TBdressClub dress=>http://goo.gl/qwIwus        shoes=>http://goo.gl/Y95sdJ   pic.twitter.com/3dE4SFgUmT"]
    for urls in url_test:
        print 'removeUrl BEFORE:', urls
        print 'removeUrl AFTER:', removeUrl(urls)

    #works!
    mention_test = u"Like our @FInishLine images for #MarchMadness? Here they are. Even the ones that didn't make the cut. http://blog.finishline.com/2014/03/24/rep-your-team-for-march-madness/ …".encode('utf-8', 'ignore')
    print 'removeMentions BEFORE:', mention_test
    print 'removeMentions AFTER:', removeMentions(mention_test)

    #works!
    hashtag_test = "Top shares this week! The latest on #MarchMadness and this year's #Sweet16 and Obama's plan inRussia and Crimea http://shar.es/B32pX "
    print 'removeHashtags BEFORE:', hashtag_test
    print 'removeHashtags AFTER:', removeHashtags(hashtag_test)

    #works!
    whitespace_test = "    The @SEC was\n\n    7th in Conference RPI during the regular season. They’re 7-0 in the NCAA Tournament. #MarchMadness   "
    #whitespace_test="new\nline\ntwee..\n\n..eet"
    print 'remove white space BEFORE:', whitespace_test
    print 'remove white space AFTER:', trimTweet(removeMetaPunct(whitespace_test))

    #DONE
    metachar_test = "new\nline\ntwee..\n\n..eet"
    print 'removeMetachars BEFORE:', metachar_test
    print 'removeMetachars AFTER:', removeMetaPunct(metachar_test)

    #Doesn't work
    punctuation_meta_test = "Ohhh Shittt...it's missed gym o'clock again...FUCK!!\n*cracks 3rd beer"
    print 'removeMetaPunct BEFORE:', punctuation_meta_test
    print 'removeMetaPunct AFTER:', removeMetaPunct(punctuation_meta_test)

    #Doesn't work
    repeats_test = "Ohhh Shittt it's missed gym o'clock again...FUCKKKK!!\n*cracks 3rd beer"
    print 'replaceRepeats_gt2 BEFORE:', repeats_test
    print 'replaceRepeats_gt2 AFTER:', replaceRepeats_gt2(repeats_test)

    #works!
    stopword_test = 'anybody considering best inward several provided'
    stopword_test_tokens = stopword_test.split()
    print 'removeStopWords BEFORE:', stopword_test_tokens
    print 'removeStopWords AFTER:', removeStopWords(stopword_test)

    #slangword_test=''

if __name__ == '__main__':
    testTweetProcessor()
