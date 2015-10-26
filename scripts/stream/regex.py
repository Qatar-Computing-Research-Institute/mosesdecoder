#!/usr/bin/python
import re

ptregex=re.compile('\s+\|\|\|\s*')
scregex=re.compile('\s?\w+\:\s+')

def ptSplit(string):
  return ptregex.split(string)

def nbSplit(string):
  return scregex.split(string)

