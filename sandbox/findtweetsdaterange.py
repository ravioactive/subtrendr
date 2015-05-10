import sys
import pymongo
from unidecode import unidecode
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

	target_tw = -1
	if len(args) > 1:
		target_tw = int(args[1])
		if not target_tw or target_tw < 0:
			target_tw = -1

	if target_tw < 0:
		print 'target time window not found'
		sys.exit(1)

	windowsz = -1
	if len(args) > 2:
		windowsz = int(args[2])
		if not windowsz or windowsz < 0:
			windowsz = -1

	if windowsz < 0:
		print 'window size not found'
		sys.exit(1)

	suffix = ''
	if len(args) > 3:
		suffix = args[3]
		if not suffix or len(suffix) < 1:
			suffix = ''

	if len(suffix) == 0:
		print 'suffix not found'
		sys.exit(1)

	start_time = None
	end_time = None

	twcoll = db[trendname + '_tw_' + suffix]
	endquery = { '_id':target_tw }
	twcursor = twcoll.find(endquery)
	for doc in twcursor:
		end_time = doc['end']

	priortw = target_tw - 2*windowsz + 1
	if priortw <= 0:
		priortw = 1

	startquery = { '_id':priortw }
	twcursor = twcoll.find(startquery)
	for doc in twcursor:
		start_time = doc['start']

	if start_time is None or end_time is None:
		print 'Could not find start or end time'
		sys.exit(1)

	ngramdictionary = { 'unigrams' : {}, 'bigrams' : {}, 'trigrams' : {}}
	fname = trendname + "_" + suffix + "_" + str(target_tw)
	tweetscoll = db[trendname + '_tweets']
	tweetsquery = { 'timestamp' : { '$gte' : start_time, '$lt' : end_time } }
	tweetscursor = tweetscoll.find(tweetsquery)

	open(fname + '.txt', "w").close()
	with open(fname + '.txt', "a") as tweetsfile:
		for doc in tweetscursor:
			# print unidecode(doc['text'])
			for u in doc['unigrams'].keys():
				us = str(u)
				if us in ngramdictionary['unigrams'].keys():
					ngramdictionary['unigrams'][us] += doc['unigrams'][u]
				else:
					ngramdictionary['unigrams'][us] = doc['unigrams'][u]

			for b in doc['bigrams'].keys():
				bs = str(b)
				if bs in ngramdictionary['bigrams'].keys():
					ngramdictionary['bigrams'][bs] += doc['bigrams'][b]
				else:
					ngramdictionary['bigrams'][bs] = doc['bigrams'][b]

			for t in doc['trigrams'].keys():
				ts = str(t)
				if ts in ngramdictionary['trigrams'].keys():
					ngramdictionary['trigrams'][ts] += doc['trigrams'][t]
				else:
					ngramdictionary['trigrams'][ts] = doc['trigrams'][t]
			
			tweetsfile.write(unidecode(doc['text']) + '\n\n')

			
	sortedunigrams = sorted(ngramdictionary['unigrams'].items(), key=operator.itemgetter(1), reverse=True)
	open(fname + '_unigrams' + '.txt', "w").close()
	with open(fname + '_unigrams' + '.txt', "a") as tweetsunigrfile:
		for u in sortedunigrams:
			tweetsunigrfile.write(u[0] + ", " + str(u[1]) + '\n')

	sortedbigrams = sorted(ngramdictionary['bigrams'].items(), key=operator.itemgetter(1), reverse=True)
	open(fname + '_bigrams' + '.txt', "w").close()
	with open(fname + '_bigrams' + '.txt', "a") as tweetsbigrfile:
		for b in sortedbigrams:
			tweetsbigrfile.write(b[0] + ", " + str(b[1]) + '\n')

	sortedtrigrams = sorted(ngramdictionary['trigrams'].items(), key=operator.itemgetter(1), reverse=True)
	open(fname + '_trigrams' + '.txt', "w").close()
	with open(fname + '_trigrams' + '.txt', "a") as tweetstrigrfile:
		for t in sortedtrigrams:
			tweetstrigrfile.write(t[0] + ", " + str(t[1]) + '\n')
		

if __name__ == '__main__':
	main()