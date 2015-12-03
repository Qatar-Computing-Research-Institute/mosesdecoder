#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python port of client.perl

import xmlrpclib
import datetime
import regex 
import time

def findMaxIntersect(old,new):
    if len(old)==0:
        return -1

    #print old,"}}}",new
    for i,ab in enumerate(zip(old.split(),new.split())):
        if ab[0]!=ab[1]:
            return i+1
    return len(old.split())

def pruneNbest(nbest,to_end):
    dic={}
    for string in nbest:
        words=string.split()
        dic[" ".join(words[to_end:])]=1
    return dic.keys()

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


def getFinal(nbest,length):
    diff={}
    for n in nbest[:100]:
        string=" ".join([ x.split("|")[0] for x in n['hyp'].split()[-(length):] ]).encode("utf-8")
        try:
            diff[string]+=1
        except KeyError:
            diff[string]=1

    return diff.keys()

def translate(proxy,params,string,to_keep=0):
    
    params['text']=string
    print "before translating::::: %s "%(string)
    result = proxy.translate(params)
    
    res= clean(result['text'].encode("utf-8"))
    print "translated:::: %s"%(res)
    if 'nbest' in result:
        nbest=getFinal(result['nbest'],to_keep)
    else:
        nbest=[res]
    return (res,nbest)
    

def clean(text):
    return " ".join([x.split("|")[0] for x in text.split()]) 

url = "http://localhost:8080/RPC2"
print "before connecting"
proxy = xmlrpclib.ServerProxy(url)
print "connected"

model=loadPTSources("/Users/guzmanhe/Projects/streamed_decoder/sample-models/phrase-model/phrase-table")



text = u"das ist ein klein haus und das ist ein alt haus und die haus gibt ein klein"

params = {"text":"", "align":"false", "report-all-factors":"false", "xml-input":"exclusive","nbest-size":"0"}
prev_res=""
prev_to_trans=""
prev_to_trans_xml=''
current=""
cur_res=""
result=[]
window=3

now=time.time()
print "transating::%s"%(text)
for word in text.split():

    if current != "":
        if  current +" " + word  not in model:
            

            if prev_to_trans!="":
                prev_to_trans_xml= "<np translation=\"%s\">%s</np> <wall/> "%("||".join(prev_nbest),prev_to_trans)

            (cur_res,prev_nbest)=translate(proxy,params,prev_to_trans_xml + current)
            if (prev_nbest==""):
                prev_nbest=cur_res


            intersect=findMaxIntersect(prev_res,cur_res)
            #intersect= intersect-3
            #print intersect
            if intersect > window:
                #update result     

                cur_words=cur_res.split()
                cutoff = min (intersect,len(cur_words)-window)

                stable = " ".join(cur_words[:cutoff])
                result.append(stable)
                prev_res=" ".join(cur_words[cutoff:])
                prev_nbest = pruneNbest(prev_nbest,cutoff) #prune nbest
                print "stable_hyp (%d)::%s"%(cutoff, stable)
                #print "unstable_hyp %d::: %s"%(intersect,prev_res)
                
                #print "current_result :::%s" %(result)
            else:
                prev_res=cur_res
            
            prev_to_trans=current
            current = word
            #result+=" "+prev_res
        else:
            current+=" " + word 

    else:
        current=word
        
if prev_to_trans!="":
    prev_to_trans_xml= "<np translation=\"%s\">%s</np> "%(prev_res,prev_to_trans)

(cur_res,prev_nbest)=translate(proxy,params,prev_to_trans_xml + current)

result.append(cur_res)

print"(%0.3f secs) translated::%s"%(time.time()-now," ".join(result))


params = {"text":text, "align":"false", "report-all-factors":"false", "xml-input":"exclusive","nbest-size":"0"}

#print params
# try:
#      result = proxy.translate(params)
# except xmlrpclib.ProtocolError:
#      result={'text':'no_translation'}

# print clean(result['text'].encode("utf-8"))

#if 'align' in result:
#    print "Phrase alignments:"
#    aligns = result['align']
#    for align in aligns:
#        print "%s,%s,%s" %(align['tgt-start'], align['src-start'], align['src-end'])
