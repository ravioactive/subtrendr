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


def recordTimeWindow(trendname):
	print 'recordTimeWindow called at time_window', time_window
	twColl = db[trendname+'_tw']
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
	print 'x:', xdata,
	ydata = npLastKArr[:,1]
	print 'y:', ydata

	params = curve_fit(linearKernel, xdata, ydata)
	slope = params[0][0]
	return (slope, slope > 0)

# (y, x) pairs
def findDerivative(tuparr):
	deriv = []
	for i in xrange(1, len(tuparr)):
		nr = tuparr[i][1]-tuparr[i-1][1]
		dr = tuparr[i][0]-tuparr[i-1][0]
		s = nr/dr
		deriv.append((tuparr[i][0],s))
	return deriv


def qualifyingCriteria(lastKArr):
	# find the rate of change of rate of change
	singlederiv = findDerivative(lastKArr)
	cnr = 0
	dnr = len(singlederiv)
	for sd in singlederiv:
		cnr += sd[1]
	acc = cnr/dnr
	# doublederiv = findDerivative(singlederiv)
	return (acc, acc > 0)


def checkSubtrending(db, trendname, lastk):
	workingset = db[trendname+'_workset']
	subtrendsColl = db[trendname+'_subtrend']
	subtrendsBulk = subtrendsColl.initialize_unordered_bulk_op()
	min_window = 0 if time_window <= lastk else (time_window - lastk)
	query = { 'latest_window' : {'$gte': min_window}}
	filters = { '_id':True, 'latest_window':True, 'ws_hist' : {'$slice' : lastk}}
	workingsetcursor = None
	workingsetcursor = workingset.find(query, filters)
	if workingsetcursor.count() < 1:
		print 'checkSubtrending: Nothing to do'
		return False

	numsubtrupdates = 0
	for doc in workingsetcursor:
		(slope, qualifies) = curvefitting(doc['ws_hist'])
		if qualifies:
			st_query = {'_id' : str(doc['_id'])}
			st_update = {'$setOnInsert' : {'_id': str(doc['_id'])}, '$set' : {'latest_window' : doc['latest_window'], 'latest_slope' : slope}, '$push' : {'st_hist': {'$each' : [(time_window, slope)], '$position':0}}}
			subtrendsBulk.find(st_query).upsert().update(st_update)
			numsubtrupdates += 1

	if numsubtrupdates == 0:
		print '\ncheckSubtrending: No ngram qualified or retrieved...'
		return False

	try:
		result = subtrendsBulk.execute()
	except BulkWriteError as bwe:
		print '\n Exception in bulk updating subtrending collection\n'
		print bwe.details
		return False

	return True



def findcandidates(db, trendname, lasttime, thresh):
	# decide what to return
	#	a cursor over the result set OR the result set itself?
	# working set: {_id: ngram, }
	unigramColl = db[trendname+'_unistate']
	bigramColl = db[trendname+'_bistate']
	unicursor = None
	bicursor = None
	
	workingSetColl = db[trendname+'_workset']
	workingSetCollBulk = workingSetColl.initialize_unordered_bulk_op()
	query = {'last_change':{'$gt':lasttime}}
	filters = { '_id':True, 'total': True }		# ignore history!
	
	unicursor = unigramColl.find(query, filters)
	bicursor = bigramColl.find(query, filters)
	print 'uni:', unicursor.count(), 'bi:', bicursor.count()
	
	numupdates = 0;
	for doc in unicursor:
		print doc['_id'], ':', doc['total'], ',',
		if doc['total'] > thresh:
			ws_query = {'_id': str(doc['_id'])}
			ws_update = {'$setOnInsert' : {'_id': str(doc['_id'])}, '$set' : {'latest_window' : time_window}, '$push': {'ws_hist' : { '$each' : [(time_window, doc['total'])], '$position':0}}}
			workingSetCollBulk.find(ws_query).upsert().update(ws_update)
			numupdates+=1

	for doc in bicursor:
		print doc['_id'], ':', doc['total'], ',',
		if doc['total'] > thresh:
			ws_query = {'_id': str(doc['_id'])}
			ws_update = {'$setOnInsert' : {'_id': str(doc['_id'])}, '$set' : {'latest_window' : time_window}, '$push' : {'ws_hist' : { '$each' : [(time_window, doc['total'])], '$position':0}}}
			workingSetCollBulk.find(ws_query).upsert().update(ws_update)
			numupdates+=1
	
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
	subtrends = db[trendname+'_subtrend']
	st_query = {'latest_window':time_window}
	filters = {'_id':True, 'latest_window':True, 'latest_slope': True, 'st_hist' : {'$slice' : lastk}}
	stcursor = subtrends.find(st_query, filters).limit(20)
	if stcursor.count() < 1:
		print "Nothing to show..."
		return

	print 'SUBTRENDING between ', start_time, 'and', end_time, '( time slot: ', time_window, ')'
	for doc in stcursor:
		lastkSlopes = ''
		for t in doc['st_hist']:
			lastkSlopes += str(t[0])+':'+str(t[1])+', '
		print doc['_id'], '\t', 'd/dx:', doc['latest_slope'], lastkSlopes


def cleanCollections(db, trendname):
	if trendname+'_tw' in db.collection_names():
		preColl = db[trendname+'_tw']
		preColl.drop()
	if trendname+'_workset' in db.collection_names():
		preColl = db[trendname+'_workset']
		preColl.drop()


def findtrending(db, trendname, duration, lastk, thresh):
	print 'Called for the first time.'
	print 'init time window = ', time_window
	cleanCollections(db, trendname)
	while 1:
		global time_window
		time_window += 1
		global start_time
		start_time = end_time
		global end_time
		end_time = datetime.utcnow()
		print "Time Window: ", time_window, "starts:", start_time, "ends:", end_time
		if time_window < 1:
			start_time = end_time - timedelta(seconds = int(duration))
		else:
			recordTimeWindow(trendname)
			ret = findcandidates(db, trendname, start_time, thresh)
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
	ws_thresh = 10
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
			ws_thresh = args[3]
			if not ws_thresh or ws_thresh < 0:
				ws_thresh = 10
				print "Using at least 10 occurrences as threshold"

	print "Calculating stats for trend ", trend, "..."

	try:
		thread.start_new_thread(findtrending, (db, trend, duration, lastk, ws_thresh))
	except:
		print "Error: Unable to start thread."

	print 'SHOULD NOT BE THERE\n'
	while 1:
		pass


if __name__ == '__main__':
    main()