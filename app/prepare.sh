#!/bin/bash

#
# prepare data and library
#
LTR_DOMAIN=http://es-learn-to-rank.labs.o19s.com

## download data
wget ${LTR_DOMAIN}/tmdb.json -P ./demo/data/index

## download ranklib
wget ${LTR_DOMAIN}/RankLibPlus-0.1.0.jar -P ./demo/lib
