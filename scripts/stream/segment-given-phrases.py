#!/usr/bin/python
import sys
import gzip
import regex

def loadPTSources(phrase_table):
	model={}
	if ".gz" in phrase_table:
		fh=gzip.open(phrase_table)
	else:
		fh=open(phrase_table)

	for phrase in fh:
		source= regex.ptSplit(phrase.rstrip())[0]
		if source in model:
			continue
		else:
			model[source]=True
	fh.close()
	return model

def main(phrase_table,file):
	model=loadPTSources(phrase_table)

	fh = open(file)
	for line in fh:
		cur=None
		for word in line.split():
			if cur==None:
				cur=word
				continue
			
			#print " ".join([x+"/WORD" for x in cur.split()])
			#print [x+"/WORD" for x in cur.split()]
			if  (cur+" "+word)  not in model :
				sys.stdout.write("[PX %s] "%(" ".join([x+"/WORD" for x in cur.split()])))
				cur=word
			else:
				cur = cur+" "+word
		if cur!="":
			sys.stdout.write("[PX %s]\n"%(" ".join([x+"/WORD" for x in cur.split()])))



if __name__ == '__main__':

	if len(sys.argv) > 2:
		main(sys.argv[1],sys.argv[2])

	else:
		main('tst/iwslt_all.gz','tst/tst2010.input.tok.1')
