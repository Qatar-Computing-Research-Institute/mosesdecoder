#!/bin/bash

INPUT="$1"
CHUNKED="$2"
KEYFILE="$4"
OUTPUT="$3"
OTHER="$5"


# put segment the input
#perl  /work/stream/scripts/AMIRA_NOTOK_NONORM.pl config=/work/stream/scripts/amiraconfig.atb.bpc.utf8 file=$INPUT

# produce segmentation
python /work/stream/scripts/getPB-LEX.py $CHUNKED $INPUT $OTHER

# produce keyfile
mv $CHUNKED.segs.idx $KEYFILE

# produce textfile
mv $CHUNKED.segs.txt $OUTPUT
