#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2016 Mike Benna

from __future__ import print_function
import argparse
import subprocess
import random
import sys

ignoreCase = False
mixedCase = False	# set to True if we should try to select mixed case words more often
includeSimplePunctuation = False
numWords = 100		# number of words per paragraph to output
numLessons = 1		# number of lessons to output (1=just a word list)
topWords = 100		# number of words to choose from

wordList = []		# tuples of (count, word)
totalWordCount = 0	# total # of words counted

excludedWords = ['asana', 'actiontag', 'basecamp', 'id', 'll', 'nextaction', 'nextactions', 'st', 've']
simplePunctuation = ['.', ',', '\'']

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def outputHistogram():
	wordsSoFar = 0
	wordIndex = 0
	percentage = 0.0
	for word in wordList:
		wordsSoFar += word[0]
		wordIndex += 1
		p = wordsSoFar*100.0/totalWordCount
		if p >= percentage:
			print("%d,%.1f%%" % (wordIndex, p))
			percentage = p+1.0

def generatePracticeWords():
	# Count up how many occurences are in the topWords to choose from
	global topWords
	topWords = min(topWords, len(wordList))
	coverage = 0
	for i in xrange(topWords):
		coverage += wordList[i][0]
	eprint("%d words counted, %d unique words, the top %d words represent %.1f%% occurences of all words\n" % (totalWordCount, len(wordList), topWords, float(coverage)*100.0/float(totalWordCount)))

	if numLessons > 1:	# output lessons instead of just a word list
		for p in xrange(numLessons):
			outputString = ""
			lastIndex = -1
			for i in xrange(numWords):
				if i>0:
					outputString += " "
				retryCount = 0
				while retryCount < 8:
					retryCount += 1
					index = random.randint(0, topWords-1)
					if index == lastIndex:
						continue	# avoid double-words.. try again.
					if mixedCase and wordList[index][1].islower():
						continue	# it's all lowercase... try again.
					break	# found a good one.
				outputString += wordList[index][1]
				lastIndex = index
				if not random.randint(0, 8):
					p = simplePunctuation[random.randint(0,1)]
					outputString += p
			print(outputString + "\n\n")
	else:	# output just a top word list
		outputString = ""
		for i in xrange(topWords):
			if i>0:
				outputString += " "
			outputString += wordList[i][1]
		print(outputString + "\n\n")

def parseWordList(filelist):
	ignoreCaseString = "-i " if ignoreCase else ""
	allFileNames = ' '.join(filelist)
	makeLowerCmd = " | tr A-Z a-z" if ignoreCase else ""
	commandStr = "sed -e \"s/[^A-Za-z']/ /g\" " + allFileNames + " | fmt -1 | sed -e \"s/ *//g\" -e \"s/^[ ']$//g\" -e \"s/^'*//g\" -e \"s/'*$//g\" " + makeLowerCmd + " | sort "+ignoreCaseString+" | uniq -c "+ignoreCaseString+" | sort -nr"
	#print "Command = " + commandStr
	output = subprocess.check_output(commandStr, shell=True)
	lines = output.splitlines()
	global totalWordCount
	global wordList
	totalWordCount = 0
	for line in lines:
		splitLine = line.strip().split(' ')
		if (len(splitLine)>1
			and int(splitLine[0]) > 0
			and len(splitLine[1]) > 0
			and not splitLine[1].lower() in excludedWords
			and (len(splitLine[1]) > 1 or splitLine[1] in ['a','I'])):	# omit single letters except []
			count = int(splitLine[0])
			word = splitLine[1]
			totalWordCount += count
			wordList.append((count, word))
			#print("#%4d: Found %d occurences of '%s'" % (len(wordList), count, word))

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('files', type=str, help='text files to use for data', nargs='*')
	parser.add_argument('--histogram', action="store_true", help='output a histogram')
	parser.add_argument('-i', '--ignorecase', action="store_true", help='ignore case (make everything lower')
	parser.add_argument('-l', '--lessons', type=int, help='number of paragraphs/lessons to output')
	parser.add_argument('-m', '--mixedcase', action="store_true", help='select lots of mixed case words')
	parser.add_argument('-n', '--numwords', type=int, help='number of words per lesson to output')
	parser.add_argument('-p', '--punctuation', action="store_true", help='include simple punctuation')
	parser.add_argument('-t', '--topwords', type=int, help='top number of words to choose from')
	args = parser.parse_args()
	if args.ignorecase:
		ignoreCase = args.ignorecase
	if args.mixedcase:
		mixedCase = args.mixedcase
	if args.punctuation:
		includeSimplePunctuation = args.punctuation
	if args.numwords:
		numWords = args.numwords
	if args.lessons:
		numLessons = args.lessons
	if args.topwords:
		topWords = args.topwords
	parseWordList(args.files)
	if args.histogram:
		outputHistogram()
		exit(0)
	random.seed()
	generatePracticeWords()
