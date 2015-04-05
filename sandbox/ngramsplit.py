import re

def ngrams(input, n):
  input = input.split(' ')
  output = {}
  for i in range(len(input)-n+1):
    g = ' '.join(input[i:i+n])
    output.setdefault(g, 0)
    output[g] += 1
  
  return output

print ngrams('But it works for all the n-grams within a word', 2)

def repeatfix(tweet_str):
	repeatgrp1 = re.compile(r"(.)\1{2,}", re.DOTALL)
	repeatgrp2 = re.compile(r"(..)\1{2,}", re.DOTALL)
	repeatsubspat = r"\1\1"
	replacedTokens = []
	word_list = tweet_str.split()
	for token in word_list:
	   	replacedTokens.append(re.sub(repeatgrp1, repeatsubspat, re.sub(repeatgrp2, repeatsubspat, token)))

   	print replacedTokens
   	replacedTokens_str = ' '.join([i for i in replacedTokens])
   	return replacedTokens_str

# print repeatfix("Ohhh Shittt it's missed gym o'clock again...FUCKKKK!!\n*cracks 3rd beer")