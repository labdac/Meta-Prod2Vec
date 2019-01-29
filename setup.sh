#!/usr/bin/env bash

cd data
wget http://static.echonest.com/millionsongsubset_full.tar.gz
tar -xvzf millionsongsubset_full.tar.gz

wget https://crossnox.sytes.net/owncloud/index.php/s/edt1ULkBOeQacul/download -O ThirtyMusic.tar.gz
tar -xvzf ThirtyMusic.tar.gz
