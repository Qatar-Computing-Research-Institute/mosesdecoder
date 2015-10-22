#!/bin/bash

INPUT="$1"
OUTPUT="$2"


# put segment the input
perl  /work/stream/scripts/AMIRA_NOTOK_NONORM.pl config=/work/stream/scripts/amiraconfig.atb.bpc.utf8 file=$INPUT



# produce textfile
mv $INPUT.amirabpc $OUTPUT
