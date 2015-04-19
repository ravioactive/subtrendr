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

	lastk = 10
	subtrendsColl = db[trendname+'_subtrend_'+str(lastk)]
	subtrecColl = db[trendname+'_subtrec_'+str(lastk)]
	unigramColl = db[trendname+'_unistate']
	bigramColl = db[trendname+'_bistate']
	trigramColl = db[trendname+'_tristate']

	subtrendtwColl = db[trendname+'_tw_'+str(lastk)]
	num_windows = subtrendtwColl.count()
	subtrec_query = {'_id' : num_windows-1}
	subtrec_filter = {}

	subtrec_cursor = subtrecColl.find(subtrec_query)
	for doc in subtrec_cursor:
		# print doc['consistent']['bigrams']
		subtrending_unigrams = doc['unigrams']
		sorted_subtrending_unigrams = sorted(subtrending_unigrams.items(), key=operator.itemgetter(1), reverse=True)
		

		subtrending_bigrams = doc['bigrams']
		sorted_subtrending_bigrams = sorted(subtrending_bigrams.items(), key=operator.itemgetter(1), reverse=True)
		

		subtrending_trigrams = doc['trigrams']
		sorted_subtrending_trigrams = sorted(subtrending_trigrams.items(), key=operator.itemgetter(1), reverse=True)
		

		accelerating_unigrams = doc['accelerating']['unigrams']
		sorted_accelerating_unigrams = sorted(accelerating_unigrams.items(), key=operator.itemgetter(1), reverse=True)
		

		accelerating_bigrams = doc['accelerating']['bigrams']
		sorted_accelerating_bigrams = sorted(accelerating_bigrams.items(), key=operator.itemgetter(1), reverse=True)
		

		accelerating_trigrams = doc['accelerating']['trigrams']
		sorted_accelerating_trigrams = sorted(accelerating_trigrams.items(), key=operator.itemgetter(1), reverse=True)
		
		
		consistent_unigrams = doc['consistent']['unigrams']
		consistent_unigrams_counts = []
		for unigram in consistent_unigrams:
			unigram_trending_count = -1
			unigram_subtrending_cursor = subtrendsColl.find({'_id':unigram},{'trend_count':True})
			for subtrendrdoc in unigram_subtrending_cursor:
				unigram_trending_count = subtrendrdoc['trend_count']
			if unigram_trending_count > 0:
				consistent_unigrams_counts.append((unigram, unigram_trending_count))
		sorted_consistent_unigrams = sorted(consistent_unigrams_counts, key=operator.itemgetter(1), reverse=True)
		
		
		consistent_bigrams = doc['consistent']['bigrams']
		consistent_bigrams_counts = []
		for bigram in consistent_bigrams:
			bigram_trending_count = -1
			bigram_subtrending_cursor = subtrendsColl.find({'_id':bigram},{'trend_count':True})
			for subtrendrdoc in bigram_subtrending_cursor:
				bigram_trending_count = subtrendrdoc['trend_count']
			if bigram_trending_count > 0:
				consistent_bigrams_counts.append((bigram, bigram_trending_count))
		sorted_consistent_bigrams = sorted(consistent_bigrams_counts, key=operator.itemgetter(1), reverse=True)
		

		consistent_trigrams = doc['consistent']['trigrams']
		consistent_trigrams_counts = []
		for trigram in consistent_trigrams:
			trigram_trending_count = -1
			trigram_subtrending_cursor = subtrendsColl.find({'_id':trigram},{'trend_count':True})
			for subtrendrdoc in trigram_subtrending_cursor:
				trigram_trending_count = subtrendrdoc['trend_count']
			if trigram_trending_count > 0:
				consistent_trigrams_counts.append((trigram, trigram_trending_count))
		sorted_consistent_trigrams = sorted(consistent_trigrams_counts, key=operator.itemgetter(1), reverse=True)
		
		# subtrending 
		print '\n=========================\nTop 25 Subtrending NGrams\n=========================\n'
		print '\nUNIGRAMS\n--------'
		top25_sorted_subtrending_unigrams = sorted_subtrending_unigrams[:25]
		for unigram in top25_sorted_subtrending_unigrams:
			print unigram[1], "\t:\t", unigram[0]
		print '\nBIGRAMS\n-------'
		top25_sorted_subtrending_bigrams = sorted_subtrending_bigrams[:25]
		for bigram in top25_sorted_subtrending_bigrams:
			print bigram[1], "\t:\t", bigram[0]
		print '\nTRIGRAMS\n--------'
		top25_sorted_subtrending_trigrams = sorted_subtrending_trigrams[:25]
		for trigram in top25_sorted_subtrending_trigrams:
			print trigram[1], "\t:\t", trigram[0]

		# accelerating
		print '\n==========================\nTop 25 Accelerating NGrams\n==========================\n'
		print '\nUNIGRAMS\n--------'
		top25_sorted_accelerating_unigrams = sorted_accelerating_unigrams[:25]
		for unigram in top25_sorted_accelerating_unigrams:
			print unigram[1], "\t:\t", unigram[0]
		print '\nBIGRAMS\n-------'
		top25_sorted_accelerating_bigrams = sorted_accelerating_bigrams[:25]
		for bigram in top25_sorted_accelerating_bigrams:
			print bigram[1], "\t:\t", bigram[0]
		print '\nTRIGRAMS\n--------'
		top25_sorted_accelerating_trigrams = sorted_accelerating_trigrams[:25]
		for trigram in top25_sorted_accelerating_trigrams:
			print trigram[1], "\t:\t", trigram[0]

		# consistent
		print '\n==========================\nTop 25 Consistent NGrams\n==========================\n'
		print '\nUNIGRAMS\n--------'
		top25_sorted_consistent_unigrams = sorted_consistent_unigrams[:25]
		for unigram in top25_sorted_consistent_unigrams:
			print unigram[1], "\t:\t", unigram[0]
		print '\nBIGRAMS\n-------'
		top25_sorted_consistent_bigrams = sorted_consistent_bigrams[:25]
		for bigram in top25_sorted_consistent_bigrams:
			print bigram[1], "\t:\t", bigram[0]
		print '\nTRIGRAMS\n--------'
		top25_sorted_consistent_trigrams = sorted_consistent_trigrams[:25]
		for trigram in top25_sorted_consistent_trigrams:
			print trigram[1], "\t:\t", trigram[0]


if __name__ == '__main__':
	main()