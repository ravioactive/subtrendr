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

	topk = 25
	if len(args) > 1:
		topk = args[1]
		if not topk or topk < 0:
			topk = 25


	suffix = ''
	if len(args) > 2:
		suffix = args[2]
		if not suffix or len(suffix) < 1:
			suffix = ''

	if len(suffix) == 0:
		print 'suffix not found'
		sys.exit(1)

	filewrite = False
	if len(args) > 3:
		filewrite = True if args[3] == 'true' else False
	
	windownum = -1
	if len(args) > 4:
		windownum = int(args[4])
		if not windownum or windownum < 0:
			windownum = -1

	if windownum < 0:
		subtrendtwColl = db[trendname+'_tw_'+suffix]
		num_windows = subtrendtwColl.count()
		windownum = num_windows - 1

	topk = int(topk)
	subtrendsColl = db[trendname+'_subtrend_'+suffix]
	subtrecColl = db[trendname+'_subtrec_'+suffix]
	unigramColl = db[trendname+'_unistate']
	bigramColl = db[trendname+'_bistate']
	trigramColl = db[trendname+'_tristate']

	# subtrendtwColl = db[trendname+'_tw_'+str(lastk)]
	# num_windows = subtrendtwColl.count()
	subtrec_query = {'_id' : windownum}
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
		sorted_consistent_unigrams = sorted(consistent_unigrams.items(), key=operator.itemgetter(1), reverse=True)
		

		consistent_bigrams = doc['consistent']['bigrams']
		sorted_consistent_bigrams = sorted(consistent_bigrams.items(), key=operator.itemgetter(1), reverse=True)


		consistent_trigrams = doc['consistent']['trigrams']
		sorted_consistent_trigrams = sorted(consistent_trigrams.items(), key=operator.itemgetter(1), reverse=True)

		# subtrending 
		if filewrite == False:
			print '\n=========================\nTop', topk, 'Subtrending NGrams\n=========================\n'
			print '\nUNIGRAMS\n--------'
			beg = 0
			topK_sorted_subtrending_unigrams = sorted_subtrending_unigrams[:topk]
			for unigram in topK_sorted_subtrending_unigrams:
				print unigram[1], "\t:\t", unigram[0]
			print '\nBIGRAMS\n-------'
			topK_sorted_subtrending_bigrams = sorted_subtrending_bigrams[:topk]
			for bigram in topK_sorted_subtrending_bigrams:
				print bigram[1], "\t:\t", bigram[0]
			print '\nTRIGRAMS\n--------'
			topK_sorted_subtrending_trigrams = sorted_subtrending_trigrams[:topk]
			for trigram in topK_sorted_subtrending_trigrams:
				print trigram[1], "\t:\t", trigram[0]

			# accelerating
			print '\n==========================\nTop', topk, 'Accelerating NGrams\n==========================\n'
			print '\nUNIGRAMS\n--------'
			topK_sorted_accelerating_unigrams = sorted_accelerating_unigrams[:topk]
			for unigram in topK_sorted_accelerating_unigrams:
				print unigram[1], "\t:\t", unigram[0]
			print '\nBIGRAMS\n-------'
			topK_sorted_accelerating_bigrams = sorted_accelerating_bigrams[:topk]
			for bigram in topK_sorted_accelerating_bigrams:
				print bigram[1], "\t:\t", bigram[0]
			print '\nTRIGRAMS\n--------'
			topK_sorted_accelerating_trigrams = sorted_accelerating_trigrams[:topk]
			for trigram in topK_sorted_accelerating_trigrams:
				print trigram[1], "\t:\t", trigram[0]

			# consistent
			print '\n==========================\nTop', topk, 'Consistent NGrams\n==========================\n'
			print '\nUNIGRAMS\n--------'
			topK_sorted_consistent_unigrams = sorted_consistent_unigrams[:topk]
			for unigram in topK_sorted_consistent_unigrams:
				print unigram[1], "\t:\t", unigram[0]
			print '\nBIGRAMS\n-------'
			topK_sorted_consistent_bigrams = sorted_consistent_bigrams[:topk]
			for bigram in topK_sorted_consistent_bigrams:
				print bigram[1], "\t:\t", bigram[0]
			print '\nTRIGRAMS\n--------'
			minlen = topk if topk <= len(sorted_consistent_trigrams) else len(sorted_consistent_trigrams)
			topK_sorted_consistent_trigrams = sorted_consistent_trigrams[:topk]
			for trigram in topK_sorted_consistent_trigrams:
				print trigram[1], "\t:\t", trigram[0]

		else:
			unigramfile = trendname + "_" + suffix + "_" + str(windownum) + "_unigrams.txt"
			open(unigramfile, "w").close()
			with open(unigramfile, "a") as uf:
				uf.write(" --- Subtrending ---\n")
				for su in sorted_subtrending_unigrams[:topk]:
					uf.write(su[0] + ", " + str(su[1]) + '\n')

				uf.write(" --- Accelerating ---\n")
				for au in sorted_accelerating_unigrams[:topk]:
					uf.write(au[0] + ", " + str(au[1]) + '\n')

				uf.write(" --- Consistent ---\n")
				for cu in sorted_consistent_unigrams[:topk]:
					uf.write(cu[0] + ", " + str(cu[1]) + '\n')

			bigramfile = trendname + "_" + suffix + "_" + str(windownum) + "_bigrams.txt"
			open(bigramfile, "w").close()
			with open(bigramfile, "a") as bf:
				bf.write(" --- Subtrending ---\n")
				for sb in sorted_subtrending_bigrams[:topk]:
					bf.write(sb[0] + ", " + str(sb[1]) + '\n')

				bf.write(" --- Accelerating ---\n")
				for ab in sorted_accelerating_bigrams[:topk]:
					bf.write(ab[0] + ", " + str(ab[1]) + '\n')

				bf.write(" --- Consistent ---\n")
				for cb in sorted_consistent_bigrams[:topk]:
					bf.write(cb[0] + ", " + str(cb[1]) + '\n')			

			trigramfile = trendname + "_" + suffix + "_" + str(windownum) + "_trigrams.txt"
			open(trigramfile, "w").close()
			with open(trigramfile, "a") as tf:
				tf.write(" --- Subtrending ---\n")
				for st in sorted_subtrending_trigrams[:topk]:
					tf.write(st[0] + ", " + str(st[1]) + '\n')

				tf.write(" --- Accelerating ---\n")
				for at in sorted_accelerating_trigrams[:topk]:
					tf.write(at[0] + ", " + str(at[1]) + '\n')

				tf.write(" --- Consistent ---\n")
				for ct in sorted_consistent_trigrams[:topk]:
					tf.write(ct[0] + ", " + str(ct[1]) + '\n')


if __name__ == '__main__':
	main()