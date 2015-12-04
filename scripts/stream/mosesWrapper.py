import sys
import servertools
import xmlrpclib
import time

mosesexec="/Users/guzmanhe/Projects/streamed_decoder/mosesdecoder/bin/moses"
conf="/Users/guzmanhe/Projects/streamed_decoder/sample-models/phrase-model/moses.ini"
globalargs="--xml-input inclusive "
mypt="/Users/guzmanhe/Projects/streamed_decoder/sample-models/phrase-model/phrase-table"

launcher = servertools.MosesServer(mosesexec,conf,globalargs)

def launchmoses():
    sys.stderr.write('No intance of moses found. Launching a new one\n')
    launcher.launch()

    connected=False

    while connected==False:
        try: 
            servertools.connect()
            connected=True
        except Exception as ex:
            #print ex
            time.sleep(1)
            pass

    

    

def connect(retry=0):
    if retry >1:
        raise IOError
    try:
        
        proxy=servertools.connect()
        sys.stderr.write('found running instance of moses\n')

    except xmlrpclib.socket.error: 
        launchmoses()
        proxy=servertools.connect()
        #return connect(retry+1)

    return proxy



def main(args):

    try:
        proxy = connect()
    except IOError:
        sys.stderr.write("Could not connect to moses server\n")
        exit()

    ptsources=servertools.loadPTSources(mypt)
    #servertools.testSegment()
    for line in sys.stdin:
        trans=servertools.translateInParts(proxy,ptsources,line)
        sys.stdout.write(trans+"\n")
        sys.stdout.flush()

    if launcher.isopen():
        launcher.close()


if __name__ == '__main__':
    main(sys.argv[1:])


