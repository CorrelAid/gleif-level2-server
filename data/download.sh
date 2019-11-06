#!/usr/bin/env bash

set -u
set -e

wget https://leidata-preview.gleif.org/storage/golden-copy-files/2019/07/19/211553/20190719-0000-gleif-goldencopy-lei2-golden-copy.csv.zip
wget https://leidata-preview.gleif.org/storage/golden-copy-files/2019/07/19/211598/20190719-0000-gleif-goldencopy-rr-golden-copy.csv.zip
unzip 20190719-0000-gleif-goldencopy-lei2-golden-copy.csv.zip
unzip 20190719-0000-gleif-goldencopy-rr-golden-copy.csv.zip

cat 20190719-0000-gleif-goldencopy-lei2-golden-copy.csv | cut -d',' -f1,2 | sed 's/"//g' > gleif_lei.csv
mv 20190719-0000-gleif-goldencopy-rr-golden-copy.csv gleif_rr.csv

rm *.zip
