#!/bin/bash

INPUT="$1"
CHUNKED="$2"
OUTPUT="$3"
KEYFILE="$4"
OTHER="$5"


# put segment the input
#perl  /work/stream/scripts/AMIRA_NOTOK_NONORM.pl config=/work/stream/scripts/amiraconfig.atb.bpc.utf8 file=$INPUT

# produce segmentation
python /work/moses-stream/scripts/stream/getPB-LEX.py $CHUNKED $INPUT $OTHER

# produce keyfile
mv $CHUNKED.segs.idx $KEYFILE

# produce textfile
mv $CHUNKED.segs.txt $OUTPUT
