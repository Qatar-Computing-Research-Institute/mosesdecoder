from itertools import izip_longest, chain
from itertools import chain
import sys


def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

def grouper( n,iterable, fillvalue=[]):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def getBoundaries(line,index=0):

	#indices=[]
	words=[[]]
	#phrase=0
	#memberships=[]
	wordsinline=line.split()
	wordid =0
	for idx,word in enumerate(wordsinline):
		
		if word[0]=="[":
			continue
		if len(word.split("/")) > 2:
			lex="/"
			tag="PUNC"
		else:
			(lex,tag)=word.split("/")
		tag=tag.replace(']','');
			
		if tag == 'PUNC': #TODO use regex to make efficient
			if not len(words[-1]) and len(words) >1:
				words.pop()

		#indices.append(phrase)
		
		words[-1].append(lex)
		#wordid +=1
		#print "%d %d %s %s %s"%(index,phrase,lex,tag,word)
		#memberships.append(str(phrase))
		#print idx, word,phrase

		if len(lex) <1: 
			continue
		if lex[-1] in ['#','+'] or lex[0] in ['#','+'] : #we want to keep morphemes together
			continue
		if tag in ['CC']: #if we have conjunction, we don't change phrase
			continue
		if word[-1]=="]":  #we create a new phrase
			#phrase+=1
			words.append([])
	if len(words[-1]) ==0:
		words.pop()
	if words[-1][-1] =="":
		words[-1].pop()
	#print " ".join(memberships)
	#for i in range(len(words)):
	#	if len(word)	
	return words




def processText(chunks,original,nchunks=1):
	fh=open(chunks,'r')
	fh2=open(original,'r')

	fout=open(chunks+'.segs.txt','w')
	fout2=open(chunks+'.segs.idx','w')
	index=0
	ln=0
	for line, oline in zip(fh,fh2):
		phrases=getBoundaries(line,0)
		current=[]
		#print "---"+str(ln)+":"+ line
		#print "---"+str(ln)+":" + str(phrases)+"\n"

		words = oline.split()
		counter=0

		total=len(list(flatten(phrases))) #check how many words do we have
		if total < len(words): # if we have less, then we add the remaining ones
			phrases.append(range(total,len(words)))


		merged_phrases = list(grouper(nchunks,phrases))

		for phrase in merged_phrases:	
			flat=list(flatten(phrase))
			try:		
				fout.write(" ".join([words[counter+x] for x in range(len(flat))]) + "<wall/> ")
			except:
				print flat, len(words)

			counter += len(flat)
		fout.write("\n")
		#	

		index+=len(merged_phrases)
		#if counter < len(words):
		#	fout.write(" ".join([words[x] for x in range(counter,len(words))]) + "\n")
		#	index +=1
		#ln+=1
		fout2.write(str(index)+"\n")
	fout2.close()
	fout.close()
	fh.close()	


if __name__=="__main__":
	chunks=1

	if (len(sys.argv)>3):
		chunks=int(sys.argv[3])
	#print "running with chunks " + str(chunks)
	if(len(sys.argv) > 2):
		processText(sys.argv[1],sys.argv[2],chunks)
	else:
		processText("tst/tst2010.input.chunks.3","tst/tst2010.input.tok.1",chunks)

