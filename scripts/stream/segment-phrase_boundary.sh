#!/bin/bash

INPUT = "$1"
KEYFILE= "$2"
OUTPUT = "$3"
ARGS = "$4"
my $rN = rand();


# put segment the input
perl  /work/stream/scripts/AMIRA_NOTOK_NONORM.pl config=/work/stream/scripts/amiraconfig.atb.bpc.utf8 file=$INPUT

# produce segmentation
python /work/stream/scripts/getPB-LEX.py $INPUT.amirapbc $ARGS

# produce keyfile
mv $INPUT.amirapbc.segs.idx $KEYFILE

# produce textfile
mv $INPUT.amirapbc.segs.txt $OUTPUT
