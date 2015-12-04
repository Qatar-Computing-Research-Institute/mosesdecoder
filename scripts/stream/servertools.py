#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python port of client.perl

import xmlrpclib
import datetime
import regex 
import time
import sys
import operator
import math
import subprocess
import shlex
import gzip


class MosesServer:
    def __init__(self,mosesexec,args):
        self.exe =mosesexec
        self.args = args
        self.stream=None

    def launch(self):
        string="%s %s --server "%(self.exe,self.args)
        #print string
        args=shlex.split(string)
        #print args
        sys.stderr.write("launching moses with arguments %s\n"%(string))
        self.stream = subprocess.Popen(args,shell=False)

    def isopen(self):
        return self.stream != None

    def close(self):
        if self.isopen():
            self.stream.kill()
    
    def __del__(self):
        self.close()


def findMaxIntersect(old,new):
    if len(old)==0:
        return -1

    #print old,"}}}",new
    for i,ab in enumerate(zip(old.split(),new.split())):
        if ab[0]!=ab[1]:
            return i+1
    return len(old.split())

def pruneNbest(nbest,window):
    dic={}
    for pair in nbest:
        (string,prob)=pair
        words=string.split()
        string=" ".join(words[window:])
        try:
            dic[string]+=prob
        except KeyError:
            dic[string]=prob

    sorted_diff = sorted(dic.items(), key=operator.itemgetter(1),reverse=True)

    #print sorted_diff
    return sorted_diff

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


def getFinal(nbest,nbest_size=100,length=0):
    diff={}
    #print nbest[0]
    total=0
    for n in nbest[:nbest_size]:
        #print n['hyp']
        string=" ".join([ x.split("|")[0] for x in n['hyp'].split()[-(length):] ]).encode("utf-8")
        score=float(n['totalScore'])
        total+=math.exp(score)
        try:
            diff[string]+=math.exp(score)
        except KeyError:
            diff[string]=math.exp(score)

    #sorted_diff = sorted(diff.items(), key=operator.itemgetter(1),reverse=True)
    #print total
    for item in diff:
        #print diff[item]
        diff[item] = diff[item]/total

    #print diff
    return diff.items()

def translate(proxy,params,string,nbest_size,to_keep=0,retry=0): #to_keep=0 means all words are kept
    if retry > 10:
        return ("no_translation_possible",None)

    params['text']=string
    #print "before translating::::: %s "%(string)
    try: 
        result = proxy.translate(params)
    except xmlrpclib.ProtocolError:
        sys.stderr("problem translating %s, retrying")%(string)
        return translate(proxy,params,string,nbest_size,to_keep,retry+1)
    
    res= clean(result['text'].encode("utf-8"))
    #print "translated:::: %s"%(res)
    if 'nbest' in result:
        nbest=getFinal(result['nbest'],nbest_size,to_keep)
        #nbest.append((res,0.05))
    else:
        (nres,nnbest)=translate(proxy,params,string,nbest_size,to_keep,retry+1)
        if nnbest==None:
            nbest=[(res,0.05)]
        else:
            nbest=nnbest
        #nbest=[(res,0.8)]
    return (res,nbest)
    

def clean(text):
    return " ".join([x.split("|")[0] for x in text.split()]) 

def connect():
    url = "http://localhost:8080/RPC2"
    sys.stderr.write("before connecting\n")
    proxy = xmlrpclib.ServerProxy(url)
    try: 
        proxy._()
    except xmlrpclib.Fault:
        pass
    except xmlrpclib.socket.error, er:
        raise er

    sys.stderr.write("connected\n")
    return proxy




def createprevXML(prev_nbest,prev_to_trans,prev_res):
    if prev_to_trans=="":
        return ""
    elif len(prev_nbest) ==0:
        string="<zone><np translation=\"%s\">%s</np> <wall /></zone>"%(prev_res.replace('"',"&quot;"),prev_to_trans.replace('"',"&quot;"))
    else: 
        string= "<zone><np translation=\"%s\" prob=\"%s\">%s</np> <wall /> </zone>"%("||".join([x[0] for x in prev_nbest]).replace('"',"&quot;"),"||".join(["%0.5f"%(x[1]) for x in prev_nbest]),prev_to_trans.replace('"',"&quot;"))
    return string

def translateInParts(proxy,seg_model,text,nbest_size=100,window=3):

    

    params = {"text":"", "align":"false", "report-all-factors":"false", "xml-input":"exclusive","nbest-size":nbest_size}
    
    prev_res=cur_res=prev_to_trans=prev_to_trans_xml=current=""
    prev_nbest=None
    result=[]

    now=time.time()
    #print "transating::%s"%(text)
    for word in text.split():

        if current != "":
            if  current +" " + word  not in seg_model:
                
                
                prev_to_trans_xml= createprevXML(prev_nbest,prev_to_trans,prev_res)

                (cur_res,prev_nbest)=translate(proxy,params,prev_to_trans_xml + current,nbest_size)
                if (prev_nbest==None):
                    prev_nbest=[(cur_res,1.0)]

                #print "cur res::",cur_res
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
                    #print "stable_hyp (%d)::%s"%(cutoff, stable)
                    #print "unstable_hyp %d::: %s"%(intersect,prev_res)
                    
                    #print "current_result :::%s" %(result)
                    prev_to_trans=" ".join((prev_to_trans+" "+current).split()[cutoff:])
                else:
                    prev_res=cur_res
                    prev_to_trans=prev_to_trans+" "+current
                
                
                current = word
                #result+=" "+prev_res
            else:
                current+=" " + word 

        else:
            current=word
            
    
    prev_to_trans_xml= createprevXML(prev_nbest,prev_to_trans,prev_res)

    (cur_res,prev_nbest)=translate(proxy,params,prev_to_trans_xml + current,nbest_size,window)

    result.append(cur_res)
    #print"(%0.3f secs) translated::%s"%(time.time()-now," ".join(result))
    return " ".join(result)

def testSegment(text=None):
    if text ==None:
        text = u"das ist ein klein haus und das ist ein alt haus und die haus gibt ein klein<wall/>"

    seg_model=loadPTSources("/Users/guzmanhe/Projects/streamed_decoder/sample-models/phrase-model/phrase-table")
    proxy=connect()
    trans={}
    trials=100
    timestart=time.time()
    for i in range(trials):
        hyp=translateInParts(proxy,seg_model,text)
        print hyp
        try:
            trans[hyp]+=1.0
        except KeyError:
            trans[hyp]=1.0
    most_consistent=max(trans.values())
    totaltime=time.time()-timestart
    print "Consistency is %0.1f pct "%(most_consistent*100.0/float(trials))
    print "Total time was %0.1f secs, %0.5f per transl"%(totaltime,totaltime/float(trials))




def test(text=None):
    if text ==None:
        text = u"das ist ein klein haus und das ist ein alt haus und die haus gibt ein klein"
    

    params = {"text":text, "align":"false", "report-all-factors":"false", "xml-input":"exclusive","nbest-size":"1"}
    proxy=connect()

    print params
    for i in range(10):
        try:
             result = translate(proxy,params,text)
        except xmlrpclib.ProtocolError:
             result={'text':'no_translation'}
             result=proxy.translate(params)
        print result[0]




if __name__ == '__main__':
    testSegment()
    #test()
# print clean(result['text'].encode("utf-8"))

#if 'align' in result:
#    print "Phrase alignments:"
#    aligns = result['align']
#    for align in aligns:
#        print "%s,%s,%s" %(align['tgt-start'], align['src-start'], align['src-end'])
