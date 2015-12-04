import sys
import servertools
import xmlrpclib
import time



def launchmoses(launcher):
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

    

    

def connect(launcher,retry=0):
    if retry >1:
        raise IOError
    try:
        
        proxy=servertools.connect()
        sys.stderr.write('found running instance of moses\n')

    except xmlrpclib.socket.error: 
        launchmoses(launcher)
        proxy=servertools.connect()
        #return connect(retry+1)

    return proxy



def main(launcher,ptsources):

    try:
        proxy = connect(launcher)
    except IOError:
        sys.stderr.write("Could not connect to moses server\n")
        exit()

    
    #servertools.testSegment()
    for line in sys.stdin:
        trans=servertools.translateInParts(proxy,ptsources,line)
        sys.stdout.write(trans+"\n")
        sys.stdout.flush()

    if launcher.isopen():
        launcher.close()


if __name__ == '__main__':
    
    if len(sys.argv) <3:

        mosesexec="/Users/guzmanhe/Projects/streamed_decoder/mosesdecoder/bin/moses"
        mypt="/Users/guzmanhe/Projects/streamed_decoder/sample-models/phrase-model/phrase-table"
        mosesargs="-f /Users/guzmanhe/Projects/streamed_decoder/sample-models/phrase-model/moses.ini --xml-input exclusive"
    else:
        mosesexec=sys.argv[1]
        mypt=sys.argv[2]
        mosesargs=" ".join(sys.argv[3:])


    launcher = servertools.MosesServer(mosesexec,mosesargs)
    ptsources= servertools.loadPTSources(mypt)
    main(launcher,ptsources)


