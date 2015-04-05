import thread
import sys
import datetime
from datetime import timedelta
from pymongo.errors import BulkWriteError
import numpy as np
from scipy.optimize import curve_fit

connection_string = "mongodb://localhost"
connection = pymongo.MongoClient(connection_string)
global db
db = connection.subtrendr
print type(db)

time_window = -1
start_time = datetime.utcnow()
end_time = datetime.utcnow()


def recordTimeWindow(trendname):
	twColl = db[trendname+'_tw']
	tw.insert({'_id':time_window, 'start':start_time, 'end':end_time})
	return

def linearKernel(x, a, b):
	return a*x + b

def quadraticKernel(x, a, b, c):
	return a*x*x + b*x + c

def curvefitting(lastKArr):
	npLastKArr = np.array(lastKArr)
	xdata = npLastKArr[:,0]
	ydata = npLastKArr[:,1]

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
	cnr = 0, dnr=len(singlederiv)
	for sd in singlederiv:
		cnr += sd[1]
	acc = cnr/dnr
	# doublederiv = findDerivative(singlederiv)
	return (acc, acc > 0)


def checkSubtrending(db, trendname, lastk):
	workingset = db[trendname+'_workset']
	subtrendsBulk = db[trendname+'_subtrend'].initialize_unordered_bulk_op()
	min_window = 0 if time_window <= lastk else (time_window - lastk)
	query = { 'latest_window' : {'$gte': min_window}}
	filters { '_id':True, 'latest_window':True, 'ws_hist' : {'$slice' : lastk}}
	workingsetcursor = None
	workingsetcursor = workingset.find(query, filters)

	for doc in workingsetcursor:
		(slope, qualifies) = curvefitting(doc['ws_hist'])
		if qualifies:
			st_query = {'_id' : doc['_id']}
			st_update = {'latest_window' : doc['latest_window'], 'latest_slope' : slope, '$push' : {'st_hist':(time_window, slope), '$position':0}}
			subtrendsBulk.update(st_query, st_update, {'upsert':True})
	try:
		subtrendsBulk.execute()
	except BulkWriteError as bwe:
		pprint(bwe.details)


def findcandidates(db, trendname, lasttime, thresh):
	# decide what to return
	#	a cursor over the result set OR the result set itself?
	# working set: {_id: ngram, }
	unigramColl = db[trendname+'_unistate']
	bingramColl = db[trendname+'_bistate']
	unicursor = None
	bicursor = None
	
	workingSetCollBulk = db[trendname+'_workset'].initialize_unordered_bulk_op()
	
	query = {'last_change':{'$gt':lasttime}}
	filters = { '_id':True, 'total': True }		# ignore history!
	unicursor = unigramColl.find(query, filters)

	for doc in unicursor:
		if doc['total'] > thresh == True:
			ws_query = {'id':doc['_id']}
			ws_update = {'latest_window' : time_window,'$push': {'ws_hist' : (time_window, doc['total']), '$position':0}}
			workingSetCollBulk.update(ws_query, ws_update, {'upsert':True})

	bicursor = bigramColl.find(query, filters)
	for doc in bicursor:
		if doc['total'] > thresh == True:
			ws_query = {'id':doc['_id']}
			ws_update = {'$push': {'ws_hist' : (time_window, doc['total']), '$position':0}}
			workingSetCollBulk.update(ws_query, ws_update, {'upsert':True})
	try:
		workingSetCollBulk.execute()
	except BulkWriteError as bwe:
		pprint(bwe.details)


def printSubtrending(db, trendname, lastk):
	subtrends = db[trendname+'_subtrend']
	query = {'latest_window':time_window}
	filters = {'_id':True, 'latest_window':True, 'latest_slope': latest_slope, 'st_hist' : {'$slice' : lastk}}
	stcursor = subtrends.find(query, filters).limit(20)
	print 'SUBTRENDING between ', start_time, 'and', end_time, '( time slot: ', time_window, ')'
	for doc in stcursor:
		lastkSlopes = ''
		for t in doc['st_hist']:
			lastkSlopes += str(t[0])+':'+str(t[1])+', '
		print doc['_id'], '\t', 'd/dx:', doc['latest_slope'], lastkSlopes


def findtrending(db, trendname, duration, lastk, thresh):
	time_window += 1
	start_time = end_time
	end_time = datetime.utcnow()
	if time_window < 1:
		start_time = endtime - timedelta(seconds = duration)
		return
	recordTimeWindow()
	findcandidates(db, trendname, start_time, thresh)
	checkSubtrending(db, trendname, lastk)
	printSubtrending(db, trendname)

	
def main():
	# parse args: trend, duration
	# find ngram collection with trendname 
	# start monitoring
	# resume after every duration
	args = sys.args[1:]

	if len(args) < 1:
		print "Runner usage: [Critical] missing \'trendname\' argument. \nmissing \'duration\' (in sec) argument (default 300s)."

	trend = args[0]
	if not trend or trend == '':
		print "Value for argument \'trend\' is either blank or d.n.e."
        sys.exit(1)

    duration = -1
    lastk = -1
    ws_thresh = -1
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

	while 1:
		pass