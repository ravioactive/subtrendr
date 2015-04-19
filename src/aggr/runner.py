import thread
import sys
import datetime
import time
import pprint
from datetime import datetime
from datetime import timedelta
import pymongo
from pymongo.errors import BulkWriteError
import numpy as np
from scipy.optimize import curve_fit

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
global db
db = connection.subtrendr
print type(db)

global time_window
time_window = -1
global start_time
start_time = datetime.utcnow()
global end_time
end_time = datetime.utcnow()


def recordTimeWindow(trendname, lastk):
	print 'recordTimeWindow called at time_window', time_window
	twColl = db[trendname+'_tw_'+str(lastk)]
	twColl.insert({'_id':time_window, 'start':start_time, 'end':end_time})
	return


def linearKernel(x, a, b):
	return a*x + b


def quadraticKernel(x, a, b, c):
	return a*x*x + b*x + c


def curvefitting(lastKArr, slope_thresh = 0):
	if len(lastKArr) < 2:
		print 'Too less to infer from: Only 1 point.'
		return (0, False)

	npLastKArr = np.array(lastKArr)
	xdata = npLastKArr[:,0]
	ydata = npLastKArr[:,1]

	print 'X:', xdata, 'Y:', ydata,
	params = []
	slope = -1
	try:
		params = curve_fit(linearKernel, xdata, ydata)
		slope = params[0][0]
	except RuntimeError as rte:
		print rte
		slope = -1
		pass

	print 'm =', '{0:.3f}'.format(slope)
	return (slope, slope > slope_thresh)


def findInsertPosition(tuplearr, newval):
	size = len(tuplearr)
	if size == 0:
		return 0
	if size == 1:
		if newval >= tuplearr[0][1]:
			return 0
		else:
			return 1
	else:
		pos = -1
		for i in range(0, size):
			if tuplearr[i][1] < newval:
				pos = i
				break
		if pos == -1:
			pos = i
		return pos


def checkAcceleratingConsistent(db, trendname, lastk, lastk_accel, accel_thresh = 0, consistent_fraction = 3):
	subtrendsColl = db[trendname+'_subtrend_'+str(lastk)]
	subtrendsBulk = subtrendsColl.initialize_unordered_bulk_op()
	query = {'trending_window' : time_window}
	filters = {'_id':True, 'n':True, 'sos':True, 'sos_stats':True, 'trend_count' : True, 'st_hist' : {'$slice' : lastk_accel}}

	subtrendCursor = subtrendsColl.find(query, filters)
	if subtrendCursor.count() < 1:
		print 'checkAcceleratingConsistent: Nothing to do'
		return False

	accel_unigrams = {}
	accel_bigrams = {}
	accel_trigrams = {}
	consistent_unigrams = []
	consistent_bigrams = []
	consistent_trigrams = []
	num_accel_updates = 0
	for doc in subtrendCursor:
		(slope, _) = curvefitting(doc['st_hist'], accel_thresh)
		insertpos = findInsertPosition(doc['sos_stats'], slope)
		is_consistent = True if (int(doc['trend_count'])+1) >= (time_window/consistent_fraction) else False
		accel_inc = 0 if slope <= accel_thresh else 1
		acc_query = {'_id' : str(doc['_id'])}
		acc_update = {
		'$set' : {'sos' : slope, 'consistent' : is_consistent}, 
		'$inc': {'accel_count' : accel_inc, 'trend_count' : 1},
		'$push': {'sos_stats' : {'$each' : [(time_window, slope)], '$position' : insertpos, '$slice': 5}}
		}
		# make this a dictionary
		if is_consistent == True:
			if doc['n'] == 1:
				consistent_unigrams.append((str(doc['_id']), doc['trend_count'])+1))
			if doc['n'] == 2:
				consistent_bigrams.append((str(doc['_id']), doc['trend_count'])+1))
			if doc['n'] == 3:
				consistent_trigrams.append((str(doc['_id']), doc['trend_count'])+1))
		if slope > accel_thresh:
			if doc['n'] == 1:
				accel_unigrams[str(doc['_id'])] = slope
			if doc['n'] == 2:
				accel_bigrams[str(doc['_id'])] = slope
			if doc['n'] == 3:
				accel_trigrams[str(doc['_id'])] = slope
		subtrendsBulk.find(acc_query).update(acc_update)
		num_accel_updates += 1

	if num_accel_updates < 1:
		print 'Not a single ngram accelerating for time window', time_window
		return False

	rec_consistent_ngrams = {'unigrams' : consistent_unigrams, 'bigrams': consistent_bigrams, 'trigrams': consistent_trigrams}
	rec_consistent_counts = {'uni':len(consistent_unigrams), 'bi':len(consistent_bigrams), 'tri':len(consistent_trigrams), 'total':len(consistent_unigrams)+len(consistent_bigrams)+len(consistent_trigrams)}
	rec_accel_ngrams = { 'unigrams' : accel_unigrams, 'bigrams' : accel_bigrams, 'trigrams' : accel_trigrams }
	rec_accel_counts = { 'uni':len(accel_unigrams), 'bi':len(accel_bigrams), 'tri':len(accel_trigrams), 'total' : len(accel_unigrams)+len(accel_bigrams)+len(accel_trigrams)}
	subtrendRecordColl = db[trendname+'_subtrec_'+str(lastk)]
	rec_query = {'_id' : time_window}
	rec_update = {'$set' : {'accelerating' : rec_accel_ngrams, 'accel_count' : rec_accel_counts, 'consistent':rec_consistent_ngrams, 'consistent_count':rec_consistent_counts}}
	subtrendRecordColl.update(rec_query, rec_update);
	
	try:
		result = subtrendsBulk.execute()
	except BulkWriteError as bwe:
		print '\n checkAcceleratingConsistent: Exception in bulk updating subtrending collection\n'
		print bwe.details
		return False

	return True


def checkSubtrending(db, trendname, lastk):
	workingset = db[trendname+'_workset_'+str(lastk)]
	subtrendsColl = db[trendname+'_subtrend_'+str(lastk)]
	subtrendRecordColl = db[trendname+'_subtrec_'+str(lastk)]

	subtrendsBulk = subtrendsColl.initialize_unordered_bulk_op()
	min_window = 0 if time_window <= lastk else (time_window - lastk)
	print 'Min window : ', min_window
	query = { 'latest_window' : {'$gte': min_window}}
	filters = { '_id':True, 'n':True, 'latest_window':True, 'ws_hist' : {'$slice' : lastk}}
	workingsetcursor = None
	workingsetcursor = workingset.find(query, filters)
	if workingsetcursor.count() < 1:
		print 'checkSubtrending: Nothing to do'
		return False

	numsubtrupdates = 0
	subtrec = {'_id' : time_window}
	subtrngrams = {}
	uni_subtrngrams = {}
	bi_subtrngrams = {}
	tri_subtrngrams = {}
	print 'ngram for time window', time_window, ':'

	for doc in workingsetcursor:
		print doc['_id'], ':', doc['n'], ':'
		(slope, qualifies) = curvefitting(doc['ws_hist'])
		if qualifies:
			st_query = {'_id' : str(doc['_id'])}
			st_update = {
			'$setOnInsert' : {'_id': str(doc['_id']), 'n' : doc['n'], 'sos' : -1, 'sos_stats' :[], 'trend_count': 1, 'consistent' : False, 'accel_count' : 0 }, 
			'$set' : {'trending_window' : time_window, 'latest_window' : doc['latest_window'], 'latest_slope' : slope}, 
			'$push' : {'st_hist': {'$each' : [(time_window, slope)], '$position':0}}
			}
			subtrendsBulk.find(st_query).upsert().update(st_update)
			if doc['n'] == 1:
				uni_subtrngrams[str(doc['_id'])] = slope
			elif doc['n'] == 2:
				bi_subtrngrams[str(doc['_id'])] = slope
			elif doc['n'] == 3:
				tri_subtrngrams[str(doc['_id'])] = slope
			numsubtrupdates += 1
			print 'QUALIFIES'
		else:
			print 'NOT QUALIFY'

	if numsubtrupdates == 0:
		print '\ncheckSubtrending: No ngram qualified or retrieved...'
		return False

	subtrec['unigrams'] = uni_subtrngrams
	subtrec['bigrams'] = bi_subtrngrams
	subtrec['trigrams'] = tri_subtrngrams
	subtrec['count'] = { 'uni' : len(uni_subtrngrams), 'bi':len(bi_subtrngrams), 'tri':len(tri_subtrngrams), 'total' : len(uni_subtrngrams)+len(bi_subtrngrams)+len(tri_subtrngrams) }
	subtrendRecordColl.insert(subtrec)

	try:
		result = subtrendsBulk.execute()
	except BulkWriteError as bwe:
		print '\n checkSubtrending: Exception in bulk updating subtrending collection\n'
		print bwe.details
		return False

	return True


def findcandidates(db, trendname, lasttime, lastk, uni_thresh, bi_thresh, tri_thresh):
	unigramColl = db[trendname+'_unistate']
	bigramColl = db[trendname+'_bistate']
	trigramColl = db[trendname+'_tristate']
	unicursor = None
	bicursor = None
	
	workingSetColl = db[trendname+'_workset_'+str(lastk)]
	workingSetCollBulk = workingSetColl.initialize_unordered_bulk_op()
	query = {'last_change':{'$gt':lasttime}}
	filters = { '_id':True, 'total': True }		# ignore history!
	
	unicursor = unigramColl.find(query, filters)
	bicursor = bigramColl.find(query, filters)
	tricursor = trigramColl.find(query, filters)
	print 'uni:', unicursor.count(), 'bi:', bicursor.count(), 'tri:', tricursor.count()
	
	numupdates = 0;
	print 'UNI >=', uni_thresh, ':'
	for doc in unicursor:
		print doc['_id'], ':', doc['total'], ',',
		if doc['total'] > uni_thresh:
			ws_query = {'_id': str(doc['_id'])}
			ws_update = {'$setOnInsert' : {'_id': str(doc['_id']), 'n' : 1 }, '$set' : {'latest_window' : time_window}, '$push': {'ws_hist' : { '$each' : [(time_window, doc['total'])], '$position':0}}}
			workingSetCollBulk.find(ws_query).upsert().update(ws_update)
			numupdates+=1

	print '\nBI >=', bi_thresh, ':'
	
	for doc in bicursor:
		print doc['_id'], ':', doc['total'], ',',
		if doc['total'] > bi_thresh:
			ws_query = {'_id': str(doc['_id'])}
			ws_update = {'$setOnInsert' : {'_id': str(doc['_id']), 'n' : 2 }, '$set' : {'latest_window' : time_window}, '$push' : {'ws_hist' : { '$each' : [(time_window, doc['total'])], '$position':0}}}
			workingSetCollBulk.find(ws_query).upsert().update(ws_update)
			numupdates+=1
	
	print '\nTRI >=', tri_thresh, ':'

	for doc in tricursor:
		print doc['_id'], ':', doc['total'], ',',
		if doc['total'] > tri_thresh:
			ws_query = {'_id': str(doc['_id'])}
			ws_update = {'$setOnInsert' : {'_id': str(doc['_id']), 'n' : 3 }, '$set' : {'latest_window' : time_window}, '$push' : {'ws_hist' : { '$each' : [(time_window, doc['total'])], '$position':0}}}
			workingSetCollBulk.find(ws_query).upsert().update(ws_update)
			numupdates+=1

	print '\n'
	if numupdates == 0:
		print '\nfindcandidates: No updates found'
		return False
	
	try:
		result = workingSetCollBulk.execute()
	except BulkWriteError as bwe:
		print '\n Exception in bulk updating working set\n'
		print bwe.details
		return False
	
	return True


def printSubtrending(db, trendname, lastk):
	subtrends = db[trendname+'_subtrend_'+str(lastk)]
	st_query = {'trending_window':time_window}
	filters = {'_id':True, 'n':True, 'trending_window':True, 'latest_window':True, 'latest_slope': True, 'st_hist' : {'$slice' : lastk}}
	stcursor = subtrends.find(st_query, filters)
	print 'No. of trending NGrams = ', stcursor.count()
	if stcursor.count() < 1:
		print "Nothing to show..."
		return

	print 'SUBTRENDING between ', start_time, 'and', end_time, '( time slot: ', time_window, ')'
	unislopes = ''
	bislopes = ''
	trislopes = ''
		
	for doc in stcursor:
		info = doc['_id'] + '\t' + 'latest:' + '{0:.3f}'.format(doc['latest_slope']) + '\t'
		for t in doc['st_hist']:
			 info += str(t[0])+'@'+'{0:.3f}'.format(t[1])+', '
		info += '\n'
		if doc['n'] == 1:
			unislopes += info
		elif doc['n'] == 2:
			bislopes += info
		elif doc['n'] == 3:
			trislopes += info

	print 'Trending 1GRAMs\n---------------\n', unislopes
	print 'Trending 2GRAMs\n---------------\n', bislopes
	print 'Trending 3GRAMs\n---------------\n', trislopes

	subtrendRecordColl = db[trendname+'_subtrec_'+str(lastk)]
	subtrec_query = {'_id':time_window}
	subtrec_filters = {'accelerating':True, 'accel_count':True, 'consistent':True, 'consistent_count':True}
	subtrec_cursor = subtrendRecordColl.find(subtrec_query, subtrec_filters)

	if subtrec_cursor.count() < 1:
		print "Record collection has nothing, Weird!"
		return

	for doc in subtrec_cursor:
		acceleratingCount = doc['accel_count']
		acc_str = 'Total accelerating Ngrams = ' + str(acceleratingCount['total']) + '\n'
		acc_unigramstr = 'Accelerating unigrams = ' + str(acceleratingCount['uni'])
		acc_bigramstr = 'Accelerating bigrams = ' + str(acceleratingCount['bi'])
		acc_trigramstr = 'Accelerating trigrams = ' + str(acceleratingCount['tri'])
		if acceleratingCount['total'] > 0:
			acceleratingNgrams = doc['accelerating']
			# Unigrams
			if acceleratingCount['uni'] > 0:
				acc_unigramstr += '\n'
				acceleratingUnigrams = acceleratingNgrams['unigrams']
				for unigram in acceleratingUnigrams.keys():
					acc_unigramstr += unigram + ':' + '{0:.3f}'.format(acceleratingUnigrams[unigram])+ ', '
			
			# Bigrams
			if acceleratingCount['bi'] > 0:
				acc_bigramstr += '\n'
				acceleratingBigrams = acceleratingNgrams['bigrams']
				for bigram in acceleratingBigrams.keys():
					acc_bigramstr += bigram + ':' + '{0:.3f}'.format(acceleratingBigrams[bigram])+ ', '

			# Trigrams
			if acceleratingCount['tri'] > 0:
				acc_trigramstr += '\n'
				acceleratingTrigrams = acceleratingNgrams['trigrams']
				for trigram in acceleratingTrigrams.keys():
					acc_trigramstr += trigram + ':' + '{0:.3f}'.format(acceleratingTrigrams[trigram])+ ', '
	
		acc_unigramstr += '\n'
		acc_bigramstr += '\n'
		acc_trigramstr += '\n'
		print "Accelerating Ngrams: ", acc_str, acc_unigramstr, acc_bigramstr, acc_trigramstr
		
		consistentCounts = doc['consistent_count']
		cons_str = 'Total consistent Ngrams = ' + str(consistentCounts['total']) + '\n'
		cons_unigramstr = 'Consistent unigrams = ' + str(consistentCounts['uni'])
		cons_bigramstr = 'Consistent bigrams = ' + str(consistentCounts['bi'])
		cons_trigramstr = 'Consistent trigrams = ' + str(consistentCounts['tri'])
		if consistentCounts['total'] > 0:
			consistentNgrams = doc['consistent']
			# Unigrams
			if consistentCounts['uni'] > 0:
				cons_unigramstr += '\n'
				consistentUnigrams = consistentNgrams['unigrams']
				for unigram in consistentUnigrams:
					cons_unigramstr += unigram[0] + ','
			
			# Bigrams
			if consistentCounts['bi'] > 0:
				cons_bigramstr += '\n'
				consistentBigrams = consistentNgrams['bigrams']
				for bigram in consistentBigrams:
					cons_bigramstr += bigram[0] + ','

			# Trigrams
			if consistentCounts['tri'] > 0:
				cons_trigramstr += '\n'
				consistentTrigrams = consistentNgrams['trigrams']
				for trigram in consistentTrigrams:
					cons_trigramstr += trigram[0] + ','
	
		cons_unigramstr += '\n'
		cons_bigramstr += '\n'
		cons_trigramstr += '\n'
		print "Consistent Ngrams: ", cons_str, cons_unigramstr, cons_bigramstr, cons_trigramstr
		


def cleanCollections(db, trendname, lastk):
	if trendname+'_tw_'+str(lastk) in db.collection_names():
		preColl = db[trendname+'_tw_'+str(lastk)]
		preColl.drop()
	if trendname+'_workset'+str(lastk) in db.collection_names():
		preColl = db[trendname+'_workset_'+str(lastk)]
		preColl.drop()
	if trendname+'_subtrend_'+str(lastk) in db.collection_names():
		preColl = db[trendname+'_subtrend_'+str(lastk)]
		preColl.drop()
	if trendname+'_subtrec_'+str(lastk) in db.collection_names():
		preColl = db[trendname+'_subtrec_'+str(lastk)]
		preColl.drop()


def findtrending(db, trendname, duration, lastk, uni_thresh, bi_thresh, tri_thresh):
	print 'Called for the first time.'
	print 'init time window = ', time_window
	cleanCollections(db, trendname, lastk)
	while 1:
		global time_window
		time_window += 1
		global start_time
		start_time = end_time
		global end_time
		end_time = datetime.utcnow()
		print "Time Window: ", time_window, "starts:", str(start_time), "ends:", str(end_time)
		if time_window < 1:
			start_time = end_time - timedelta(seconds = int(duration))
		else:
			recordTimeWindow(trendname, lastk)
			ret = findcandidates(db, trendname, start_time, lastk, uni_thresh, bi_thresh, tri_thresh)
			if ret == True:
				ret = checkSubtrending(db, trendname, lastk)
				if ret == True:
					ret = checkAcceleratingConsistent(db, trendname, lastk, lastk/2)
			else:
				print 'Nothing changed.'

			printSubtrending(db, trendname, lastk)
		print 'sleeping now...'
		time.sleep(int(duration))
	

def main():
	args = sys.argv[1:]

	if len(args) < 1:
		print "runner.py USAGE: python -m aggr.runner trendname duration lastk ws_thresh"
		print "mandatory args: trendname \noptional args with defaults:"
		print "\t duration: 60 sec \n\t lastk: 10 \n\t ws_thresh: 10"
		sys.exit(1)

	trend = args[0]
	if not trend or trend == '':
		print "Value for argument <trendname> is either blank or null"
		sys.exit(1)

	duration = 60
	lastk = 10
	ws_thresh_uni = 10
	ws_thresh_bi = 7
	ws_thresh_tri = 5
	if len(args) > 1:
		duration = args[1]
		if not duration or duration < 0:
			duration = 60
    		print "Duration (in sec) not found in arguments. Using default: 60 seconds\n"

		if len(args) > 2:
			lastk = args[2]
			if not lastk or lastk < 0:
				lastk = 10
				print "Using last 10 stats\n"

			if len(args) > 3:
				ws_thresh_uni = args[3]
				if not ws_thresh_uni or ws_thresh_uni < 0:
					ws_thresh_uni = 10
					print "Unigram threshold = 10"

					if len(args) > 4:
						ws_thresh_bi = args[4]
						if not ws_thresh_bi or ws_thresh_bi < 0:
							ws_thresh_bi = 7
							print "Bigram threshold = 7"

						if len(args) > 5:
							ws_thresh_tri = args[5]
							if not ws_thresh_tri or ws_thresh_tri < 0:
								ws_thresh_tri = 5
								print "Trigram threshold = 5"
							

	print "Calculating stats for trend ", trend, "..."

	try:
		thread.start_new_thread(findtrending, (db, trend, duration, lastk, ws_thresh_uni, ws_thresh_bi, ws_thresh_tri))
	except:
		print "Error: Unable to start thread."

	# print 'SHOULD NOT BE THERE\n'
	while 1:
		pass


if __name__ == '__main__':
    main()