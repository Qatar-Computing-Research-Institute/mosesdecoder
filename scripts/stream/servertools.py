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
import re
import logging

number=re.compile('\d+')
import os

#os.environ['DEBUG']="1"

if 'DEBUG' in os.environ:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stderr, level=logging.ERROR)


class Result:
    def __init__(self,flush=False):
        self.result=[]
        self.flush=flush

    def append(self,item):



        if self.flush:
            if len(self.result) >0:
                sys.stdout.write(" ")
            if type(item)==list:
                sys.stdout.write(" ".join(item))
            else:
                sys.stdout.write(item)
            sys.stdout.flush()

        if type(item)==list:
            self.result += item
        else:
            self.result.append(item)

        #self.result.append(item)
    def asString(self):
        return " ".join(self.result)
    def __str__(self):
        if self.flush:
            return ""
        else:
            return " ".join(self.result)
        

    def __repr__(self):
        if self.flush:
            return ""
        else:
            return str(self)
        #sys.stdout.flush()   
        #return 

class MosesServer:
    def __init__(self,mosesexec,args):
        self.exe =mosesexec
        self.args = args
        self.stream=None

    def launch(self):
        string="%s %s --server"%(self.exe,self.args)
        #print string
        args=shlex.split(string)
        #print args
        FNULL = open(os.devnull, 'w')
        sys.stderr.write("launching moses with arguments %s\n"%(string))
        self.stream = subprocess.Popen(args,shell=False,stdout=FNULL)

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
            return i

    return len(old.split())
def findMaxIntersectRev(old,new):
    if len(old)==0:
        return -1

    #print old,"}}}",new
    for i,ab in enumerate(zip(reversed(old.split()),reversed(new.split()))):
        if ab[0]!=ab[1]:
            return i
    return len(old.split())

def pruneNbest(nbest,stable,unstable):
    dic={}
    for pair in nbest:
        (string,prob)=pair
        words=string.split()
        intersect=findMaxIntersect(stable,string)
        #print stable,"|" ,string,"|" ,intersect
        intersect2=findMaxIntersectRev(unstable,string)
        #print unstable,"|" ,string,"|" ,intersect2
        cutoff=0
        if intersect == len(stable.split()):
            cutoff=intersect
        elif intersect2 == len(unstable.split()):
            cutoff=len(words)-len(unstable.split())
        else:
            #incompatible hyp
            #print "incompatible hyp %s"%(string)
            continue
            #cutoff=len(stable.split())


        
        string=" ".join(words[cutoff:])
        #print string
        try:
            dic[string]+=prob
        except KeyError:
            dic[string]=prob
    #print dic.keys()
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
    total=0.0
    for n in nbest[:nbest_size]:
        #print n['hyp']
        string=" ".join([ x.split("|")[0] for x in n['hyp'].split()[-(length):] ]).encode("utf-8")
        score=float(n['totalScore'])
        total+=math.exp(score)
        try:
            diff[string]+=math.exp(score)
        except KeyError:
            diff[string]=math.exp(score)

    if total<=0.0:
      total=1.0
    #sorted_diff = sorted(diff.items(), key=operator.itemgetter(1),reverse=True)
    #print total
    for item in diff:
        #print diff[item]
        diff[item] = diff[item]/total

    #print diff
    return diff.items()

def translate(proxy,params,string,nbest_size,to_keep=0,retry=0): #to_keep=0 means all words are kept
    if retry > 3:
        logging.warning('No translation found after %d trials'%retry)
        return ("no_translation_possible",None)

    params['text']=string
    logging.debug("before translating::%d::: %s "%(retry+1,string))
    try: 
        result = proxy.translate(params)
    except xmlrpclib.ProtocolError:
        sys.stderr("problem translating %s, retrying")%(string)
        return translate(proxy,params,string,nbest_size,to_keep,retry+1)
    
    res= clean(result['text'].encode("utf-8"))
    logging.debug( "translated:::: %s"%(res))
    nbest=None
    if 'nbest' in result:
        nbest=getFinal(result['nbest'],nbest_size,to_keep)
        #nbest.append((res,0.05))
    else:
        if nbest_size > 0:
            logging.warning('retying translation')
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
    if prev_to_trans=="" or prev_res=="":
        return ""
    elif len(prev_nbest) ==0:
        string="<p translation=\"%s\">%s</p> <wall /> "%(prev_res.replace('"',"&quot;"),prev_to_trans.replace('"',"&quot;"))
    else: 
        string= "<p translation=\"%s\" prob=\"%s\">%s</p> <wall /> "%("||".join([x[0] for x in prev_nbest]).replace('"',"&quot;"),"||".join(["%0.5f"%(x[1]) for x in prev_nbest]),prev_to_trans.replace('"',"&quot;"))
    #print string
    return string

def translateInParts(proxy,seg_model,text,nbest_size=10,window=3,segments=1):

    #print proxy,seg_model,text,nbest_size,window,segments

    params = {"text":"", "align":"false", "report-all-factors":"false", "xml-input":"exclusive","nbest-size":nbest_size}
    
    prev_res=cur_res=prev_to_trans=prev_to_trans_xml=current=""
    prev_nbest=None
    result=Result(flush=False)

    now=time.time()
    scounter=0
    #print "transating::%s"%(text)
    for word in text.split():

        if current != "":
            if  current +" " + word  not in seg_model: #is the concatenation in the PT?

                scounter +=1 #count it

                if scounter >= segments:
                    scounter=0
                    if nbest_size >0 and window>0:

                        prev_to_trans_xml= createprevXML(prev_nbest,prev_to_trans,prev_res)
                    else:
                        prev_to_trans_xml=""

                    if number.match(current) and " " not in current:
                      current="<n translation=\"%s\">%s</n>"%(current,current)

                    (cur_res,prev_nbest)=translate(proxy,params,prev_to_trans_xml + current,nbest_size)
                    #print cur_res
                    #print prev_nbest
                    if (prev_nbest==None):
                        prev_nbest=[(cur_res,1.0)]

                    #print "cur res::",cur_res
                    if  window > 0 and nbest_size >0:
                        intersect=findMaxIntersect(prev_res,cur_res)
                    else:
                        intersect=len(cur_res)
                    #intersect= intersect-3
                    #print intersect
                    if intersect > window:
                        #update result     

                        cur_words=cur_res.split()
                        cutoff = min (intersect,len(cur_words)-window)

                        stable = " ".join(cur_words[:cutoff])
                        result.append(stable.replace("&quot;","\""))
                        prev_res=" ".join(cur_words[cutoff:])
                        prev_nbest = pruneNbest(prev_nbest,stable,prev_res) #prune nbest
                        logging.debug("stable_hyp (%d)::%s"%(cutoff, stable))
                        logging.debug("unstable_hyp %d::: %s"%(intersect,prev_res))
                        #print prev_nbest 
                        #print "current_result :::%s" %(result)
                        prev_to_trans=current
                    else:
                        prev_res=cur_res
                        prev_to_trans=prev_to_trans+" "+current
                
                
                    current = word
                else:
                    current+=" " + word
                #result+=" "+prev_res
            else:
                current+=" " + word 

        else:
            current=word
            
    
    prev_to_trans_xml= createprevXML(prev_nbest,prev_to_trans,prev_res)

    (cur_res,prev_nbest)=translate(proxy,params,prev_to_trans_xml + current,nbest_size,window)

    result.append(cur_res.replace("&quot;","\""))
    #print"(%0.3f secs) translated::%s"%(time.time()-now," ".join(result))
    return result

def testSegment(text=None):
    if text ==None:
        text = u"das ist ein klein haus und das ist ein alt haus und die haus gibt ein klein<wall/>"

    seg_model=loadPTSources("/Users/guzmanhe/Projects/streamed_decoder/sample-models/phrase-model/phrase-table")
    proxy=connect()
    trans={}
    trials=10
    timestart=time.time()
    window=1
    nbest=1
    segments=3
    for i in range(trials):
        hyp=translateInParts(proxy,seg_model,text,nbest,window,segments)
        print hyp
        try:
            trans[hyp.asString()]+=1.0
        except KeyError:
            trans[hyp.asString()]=1.0
    #print trans.values()
    most_consistent=max(trans.values())
    totaltime=time.time()-timestart
    print "Consistency is %0.1f pct "%(most_consistent*100/float(trials))
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
