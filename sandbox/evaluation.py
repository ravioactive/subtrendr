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

	target_tw = -1
	if len(args) > 1:
		target_tw = int(args[1])
		if not target_tw or target_tw < 0:
			target_tw = -1

	if target_tw < 0:
		print 'target time window not found'
		sys.exit(1)

	suffix = ''
	if len(args) > 2:
		suffix = args[2]
		if not suffix or len(suffix) < 1:
			suffix = ''

	if len(suffix) == 0:
		print 'suffix not found'
		sys.exit(1)

	unirelfname = trendname + "_" + suffix + "_" + str(target_tw) + "_relevance_unigrams.txt"
	birelfname = trendname + "_" + suffix + "_" + str(target_tw) + "_relevance_bigrams.txt"
	trirelfname = trendname + "_" + suffix + "_" + str(target_tw) + "_relevance_trigrams.txt"

	uni_TP = []
	uni_FP = []
	uni_FN = []
	uni_TN = []
	
	bi_TP = []
	bi_FP = []
	bi_FN = []
	bi_TN = []
	
	tri_TP = []
	tri_FP = []
	tri_FN = []
	tri_TN = []

	resultdoc = None
	resultscoll = db[trendname + "_subtrec_" + suffix]
	resultscursor = resultscoll.find( { '_id' : target_tw } )
	for doc in resultscursor:
		resultdoc = doc

	with open(unirelfname) as urf:
		for line in urf:
			ur = line.split(",")
			# print ur
			if ur[1] == "1\n":
				uni_TP.append(ur[0])
			else:
				uni_TN.append(ur[0])

	print "Unigram TPs: ", len(uni_TP), "Unigram TNs:", len(uni_TN)
	uni_TP = set(uni_TP)
	uni_TN = set(uni_TN)

	with open(birelfname) as brf:
		for line in brf:
			br = line.split(",")
			# print br
			if br[1] == "1\n":
				bi_TP.append(br[0])
			else:
				bi_TN.append(br[0])	

	print "Bigram TPs: ", len(bi_TP), "Bigram TNs:", len(bi_TN)
	bi_TP = set(bi_TP)
	bi_TN = set(bi_TN)

	with open(trirelfname) as trf:
		for line in trf:
			tr = line.split(",")
			# print tr
			if tr[1] == "1\n":
				tri_TP.append(tr[0])
			else:
				tri_TN.append(tr[0])

	print "Trigram TPs: ", len(tri_TP), "Unigram TNs:", len(tri_TN)
	tri_TP = set(tri_TP)
	tri_TN = set(tri_TN)

	uni_subtrending = resultdoc['unigrams']
	bi_subtrending = resultdoc['bigrams']
	tri_subtrending = resultdoc['trigrams']

	for u in uni_subtrending.keys():
		if u not in uni_TP:
			uni_FP.append(u)

	for b in bi_subtrending.keys():
		if b not in bi_TP:
			bi_FP.append(b)

	for t in tri_subtrending.keys():
		if t not in tri_TP:
			tri_FP.append(t)

	print "Unigrams: True Positives =", len(uni_subtrending.keys()) - len(uni_FP), 
	print "False Positives =", len(uni_FP)
	uniprec = (len(uni_subtrending.keys()) - len(uni_FP))/float(len(uni_subtrending.keys()))
	print "Precision =", float(uniprec)
	unirec = (len(uni_subtrending.keys()) - len(uni_FP))/float(len(uni_TP))
	print "Recall =", unirec

	print "Bigrams: True Positives =", len(bi_subtrending.keys()) - len(bi_FP), 
	print "False Positives =", len(bi_FP)
	biprec = (len(bi_subtrending.keys()) - len(bi_FP))/float(len(bi_subtrending.keys()))
	print "Precision =", biprec
	birec = (len(bi_subtrending.keys()) - len(bi_FP))/float(len(bi_TP))
	print "Recall =", birec

	print "Trigrams: True Positives =", len(tri_subtrending.keys()) - len(tri_FP), 
	print "False Positives =", len(tri_FP)
	triprec = (len(tri_subtrending.keys()) - len(tri_FP))/float(len(tri_subtrending.keys()))
	print "Precision =", triprec
	trirec = (len(tri_subtrending.keys()) - len(tri_FP))/float(len(tri_TP))
	print "Recall =", trirec

	uni_acclerating = resultdoc['accelerating']['unigrams']
	bi_accelerating = resultdoc['accelerating']['bigrams']
	tri_accelerating = resultdoc['accelerating']['trigrams']

	uni_acc_FP = []
	bi_acc_FP = []
	tri_acc_FP = []

	for u in uni_acclerating.keys():
		if u not in uni_TN:
			uni_acc_FP.append(u)

	for b in bi_accelerating.keys():
		if b not in bi_TP:
			bi_acc_FP.append(b)

	for t in tri_accelerating.keys():
		if t not in tri_TP:
			tri_acc_FP.append(t)

	print "\n\nAccelerating Unigrams: True Positives=", len(uni_acclerating.keys()) - len(uni_acc_FP)
	print "Accelerating False Positives =", len(uni_acc_FP)
	uni_acc_prec = (len(uni_acclerating.keys()) - len(uni_acc_FP))/float(len(uni_acclerating.keys()))
	print "Precision =", float(uni_acc_prec)
	uni_acc_rec = (len(uni_acclerating.keys()) - len(uni_acc_FP)) / float(len(uni_TP))
	print "Recall=", float(uni_acc_rec)

	print "Accelerating Bigrams: True Positives =", len(bi_accelerating.keys()) - len(bi_acc_FP), 
	print "Accelerating False Positives =", len(bi_acc_FP)
	bi_acc_prec = (len(bi_accelerating.keys()) - len(bi_acc_FP))/float(len(bi_accelerating.keys()))
	print "Precision =", bi_acc_prec
	bi_acc_rec = (len(bi_accelerating.keys()) - len(bi_acc_FP))/float(len(bi_TP))
	print "Recall =", bi_acc_rec

	print "Accelerating Trigrams: True Positives =", len(tri_accelerating.keys()) - len(tri_acc_FP), 
	print "Accelerating False Positives =", len(tri_acc_FP)
	tri_acc_prec = (len(tri_accelerating.keys()) - len(tri_acc_FP))/float(len(tri_accelerating.keys()))
	print "Precision =", tri_acc_prec
	tri_acc_rec = (len(tri_subtrending.keys()) - len(tri_FP))/float(len(tri_TP))
	print "Recall =", tri_acc_rec

	uni_consistent = resultdoc['consistent']['unigrams']
	bi_consistent = resultdoc['consistent']['bigrams']
	tri_consistent = resultdoc['consistent']['trigrams']

	uni_consis_FP = []
	bi_consis_FP = []
	tri_consis_FP = []

	for u in uni_consistent.keys():
		if u not in uni_TN:
			uni_consis_FP.append(u)

	for b in bi_consistent.keys():
		if b not in bi_TP:
			bi_consis_FP.append(b)

	for t in tri_consistent.keys():
		if t not in tri_TP:
			tri_consis_FP.append(t)

	print "\n\nConsistent Unigrams: True Positives=", len(uni_consistent.keys()) - len(uni_consis_FP)
	print "Consistent False Positives =", len(uni_acc_FP)
	uni_consis_prec = (len(uni_consistent.keys()) - len(uni_consis_FP))/float(len(uni_consistent.keys()))
	print "Precision =", float(uni_consis_prec)
	uni_consis_rec = (len(uni_consistent.keys()) - len(uni_consis_FP)) / float(len(uni_TP))
	print "Consistent Recall=", float(uni_consis_rec)
	
	print "Consistent Bigrams: True Positives =", len(bi_consistent.keys()) - len(bi_consis_FP), 
	print "Consistent False Positives =", len(bi_consis_FP)
	bi_consis_prec = (len(bi_consistent.keys()) - len(bi_consis_FP))/float(len(bi_consistent.keys()))
	print "Precision =", bi_consis_prec
	bi_consis_rec = (len(bi_consistent.keys()) - len(bi_consis_FP))/float(len(bi_TP))
	print "Recall =", bi_consis_rec

	print "Consistent Trigrams: True Positives =", len(tri_consistent.keys()) - len(tri_consis_FP), 
	print "Consistent False Positives =", len(tri_consis_FP)
	tri_consis_prec = (len(tri_consistent.keys()) - len(tri_consis_FP))/float(len(tri_consistent.keys()))
	print "Precision =", tri_consis_prec
	tri_consis_rec = (len(tri_consistent.keys()) - len(tri_consis_FP))/float(len(tri_TP))
	print "Recall =", tri_consis_rec

if __name__ == '__main__':
		main()