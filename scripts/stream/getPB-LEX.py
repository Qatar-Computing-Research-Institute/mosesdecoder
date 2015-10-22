
import sys


def getBoundaries(line,index=0):

	indices=[]
	words=[]
	phrase=0
	#memberships=[]
	wordsinline=line.split()
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
			if wordsinline[idx-1][-1]=="]": #if a previous phrase was found, we attach the punctuation to it 
				phrase-=1

		indices.append(phrase)
		
		words.append(lex)
		
	#	print "%d %d %s %s %s"%(index,phrase,lex,tag,word)
		#memberships.append(str(phrase))
		#print idx, word,phrase

		if len(lex) <1: 
			continue
		if lex[-1] in ['#','+']:
			continue
		if tag in ['CC']: #if we have conjunction, we don't change phrase
			continue
		if word[-1]=="]":
			phrase+=1
	
	#print " ".join(memberships)	
	return (words,indices)




def processText(file):
	fh=open(file,'r')
	fout=open(file+'.segs.txt','w')
	fout2=open(file+'.segs.idx','w')
	index=0
	ln=0
	for line in fh:
		[words,indices]=getBoundaries(line,ln)
		windex=0
		current=[]
		for word,idx in zip(words,indices):
			if windex != idx:
				fout.write(" ".join(current) + "\n")
				windex+=1
				current=[]
			current.append(word)
		fout.write(" ".join(current) + "\n")

		index+=windex+1
		ln+=1
		fout2.write(str(index)+"\n")
	fout2.close()
	fout.close()
	fh.close()	


if __name__=="__main__":
	if(len(sys.argv) > 1):

		processText(sys.argv[1])
	else:
		processText("hungary.txt.amirabpc")

