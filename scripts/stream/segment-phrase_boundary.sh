#!/bin/bash

INPUT="$1"
KEYFILE="$3"
OUTPUT="$2"
OTHER="$4"


# put segment the input
#perl  /work/stream/scripts/AMIRA_NOTOK_NONORM.pl config=/work/stream/scripts/amiraconfig.atb.bpc.utf8 file=$INPUT

# produce segmentation
python /work/stream/scripts/getPB-LEX.py $INPUT $OTHER

# produce keyfile
mv $INPUT.segs.idx $KEYFILE

# produce textfile
mv $INPUT.segs.txt $OUTPUT
