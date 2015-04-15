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


def curvefitting(lastKArr):
	if len(lastKArr) < 2:
		print 'Too less to infer from: Only 1 point.'
		return (0, False)

	npLastKArr = np.array(lastKArr)
	xdata = npLastKArr[:,0]
	ydata = npLastKArr[:,1]

	params = curve_fit(linearKernel, xdata, ydata)
	slope = params[0][0]
	print 'm =', '{0:.3f}'.format(slope), 'X:', xdata, 'Y:', ydata
	return (slope, slope > 0)


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
			st_update = {'$setOnInsert' : {'_id': str(doc['_id']), 'n' : doc['n']}, '$set' : {'trending_window' : time_window, 'latest_window' : doc['latest_window'], 'latest_slope' : slope}, '$push' : {'st_hist': {'$each' : [(time_window, slope)], '$position':0}}}
			if doc['n'] == 1:
				uni_subtrngrams[str(doc['_id'])] = slope
			elif doc['n'] == 2:
				bi_subtrngrams[str(doc['_id'])] = slope
			elif doc['n'] == 3:
				tri_subtrngrams[str(doc['_id'])] = slope
			subtrendsBulk.find(st_query).upsert().update(st_update)
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
		print '\n Exception in bulk updating subtrending collection\n'
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