import pymongo
import ngramsplit

def main():
	connection_string = "mongodb://localhost"
	connection = pymongo.MongoClient(connection_string)
	db = connection.subtrendr
	print type(db)

	unigrams = ngrams('But it works for all the n-grams within a word', 1)
	bigrams = ngrams('But it works for all the n-grams within a word', 2)

	

main()