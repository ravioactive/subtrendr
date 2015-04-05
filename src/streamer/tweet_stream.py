# -*- coding: utf-8 -*-
import tweepy
import sys
from res import globalobjs
from model import mongomodel


class MongoStreamListener(tweepy.StreamListener):
    def __init__(self, trend, db, logfile):
        self.trend = trend
        self.db = db
        self.logfile = logfile
        self.calls = 0
        self.step = 1000
        self.smallstep = 100

    def on_status(self, status):
        #print status.text
        pass

    def on_data(self, tweet):
        #DAO based approach, initdao in __init__?
        self.calls += 1

        ret = mongomodel.insertMongo(tweet, self.trend, self.db)
        ret = ret.encode('utf-8', 'ignore')
        self.logfile.write(ret)
        if self.calls % self.step == 0:
            print globalobjs.getUptime(), 'taken for', self.calls, 'tweets'
        if self.calls % self.smallstep == 0:
            sys.stdout.write('.')
        #print "RET:\n", ret

    def on_error(self, status_code):
        print >> sys.stderr, 'Encountered error with status code:', status_code
        return True  # Don't kill the stream

    def on_timeout(self):
        print >> sys.stderr, 'Timeout...'
        return True  # Don't kill the stream


def main():
    args = sys.argv[1:]

    if len(args) < 1:
        print "Tweet collections USAGE: missing \'trend\' argument"
        sys.exit(1)

    trend = args[0]
    if not trend or trend == '':
        print "Value for argument \'trend\' is either blank or d.n.e."
        sys.exit(1)

    print "Tweet collection for trend ", trend, '...'

    keyset = 1
    if len(args) > 1:
        keyset = int(args[1])

    globalobjs.init(trend, keyset)
    auth = tweepy.OAuthHandler(globalobjs.consumer_key, globalobjs.consumer_secret)
    auth.set_access_token(globalobjs.access_token, globalobjs.access_token_secret)
    # api = tweepy.API(auth)

    sapi = tweepy.streaming.Stream(auth, MongoStreamListener(trend, globalobjs.db, globalobjs.getLogFile(trend)))
    try:
        sapi.filter(track=[trend])
    except(KeyboardInterrupt, SystemExit):
        print "User stopped with Ctrl+C"
    finally:
        print "ENTER FINALLY"
        globalobjs.destroy(trend)

if __name__ == '__main__':
    main()
