#!/bin/bash

INPUT="$1"
OUTPUT="$2"


# put segment the input
python segment-given-phrases.py /work/stream/ems/evaluation/iwslt_all.gz $INPUT >$OUTPUT



# produce textfile
mv $INPUT.amirabpc $OUTPUT
