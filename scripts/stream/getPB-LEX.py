
import sys

def flatten(seq,container=None):
    if container is None:
        container = []
    for s in seq:
        if hasattr(s,'__iter__'):
            flatten(s,container)
        else:
            container.append(s)
    return container

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
		if lex[-1] in ['#','+']:
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




def processText(chunks,original):
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
		
		for phrase in phrases:	
			try:		
				fout.write(" ".join([words[counter+x] for x in range(len(phrase))]) + "\n")
			except:
				print phrase, len(words)

			counter += len(phrase)
		
		#	

		index+=len(phrases)
		if counter < len(words):
			fout.write(" ".join([words[x] for x in range(counter,len(words))]) + "\n")
			index +=1
		#ln+=1
		fout2.write(str(index)+"\n")
	fout2.close()
	fout.close()
	fh.close()	


if __name__=="__main__":
	if(len(sys.argv) > 1):

		processText(sys.argv[1],sys.argv[2])
	else:
		processText("tst/tst2010.input.chunks.3","tst/tst2010.input.tok.1")

