#/usr/bin/python

import regex

 

totalstats=5
def getTotalStats():
  return totalstats

def split(string):
  source,target,pscores,align,pcount=regex.ptSplit(string.rstrip())
  return (source,target,pscores,align,pcount)
  
def oldformatsplit(string):
#! ! ! ||| . ||| (0) () () ||| (0) ||| 2.11894e-06 3.0268e-11 0.2 0.184819 2.718
  source,target,oldSourceAl,oldTargetAl,pscores =regex.ptSplit(string.rstrip())
  
  return (source,target,pscores,oldSourceAl)
