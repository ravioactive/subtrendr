import sys
import pymongo
import operator

def main():
	args = sys.argv[1:]
	trendname = args[0]
	if not trendname or trendname == '':
		print 'Trend value missing. Abort.'
		sys.exit(1)


	connection_string = "mongodb://localhost"
	connection = pymongo.MongoClient(connection_string)
	db = connection.subtrendr

	tw = -1
	if len(args) > 1:
		tw = int(args[1])
		if not tw or tw < 0:
			tw = -1

	if tw < 0:
		print 'time window not read'
		sys.exit(1)

	suffix = ''
	if len(args) > 2:
		suffix = args[2]
		if not suffix or len(suffix) < 1:
			suffix = ''

	if len(suffix) == 0:
		print 'suffix not found'
		sys.exit(1)

	wscoll = db[trendname + '_workset_' + suffix]
	wsquery = {'ws_hist' : { '$elemMatch' : { '$elemMatch' : { '$in' : [17] } } } }
	

	wscursor = wscoll.find(wsquery)
	twfound = False
	twngrams = {}
	for doc in wscursor:
		twfound = False
		twentry = []
		for item in doc['ws_hist']:
			if item[0] == tw:
				twfound = True
				twentry.append(item)
			if twfound == True and item[0] == tw-1:
				twentry.append(item)
		if twfound == True:
			ngramobj = { 'id' : doc['_id'], 'tw_data' : twentry }
			twngrams[doc['_id']] = ngramobj

	print len(twngrams)
	for item in twngrams.keys():
		print twngrams[item]

	reccoll = db[trendname + '_subtrec_' + suffix]
	recquery = { '_id' : tw }
	reccursor = reccoll.find(recquery)
	print 'no of docs found: ', reccursor.count()
	twdoc = None
	for doc in reccursor:
		twdoc = doc

	unigrams = doc['unigrams']
	bigrams = doc['bigrams']
	trigrams = doc['trigrams']

	for u in unigrams:
		twngrams.pop(u, None)
	for b in bigrams:
		twngrams.pop(b, None)
	for t in trigrams:
		twngrams.pop(t, None)
	
	print 'remaining ngrams: ', len(twngrams)
	for item in twngrams.keys():
		print twngrams[item]


if __name__ == '__main__':
	main()

