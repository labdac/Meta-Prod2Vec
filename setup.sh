#!/usr/bin/env bash

cd data

wget http://static.echonest.com/millionsongsubset_full.tar.gz
tar -xvzf millionsongsubset_full.tar.gz

wget https://crossnox.sytes.net/owncloud/index.php/s/edt1ULkBOeQacul/download -O ThirtyMusic.tar.gz
tar -xvzf ThirtyMusic.tar.gz

#wget http://labrosa.ee.columbia.edu/millionsong/sites/default/files/lastfm/lastfm_train.zip -O lastfm_train.zip
#unzip -q lastfm_train.zip

#wget http://labrosa.ee.columbia.edu/millionsong/sites/default/files/lastfm/lastfm_test.zip
#unzip -q lastfm_test.zip

wget http://mtg.upf.edu/static/datasets/last.fm/lastfm-dataset-1K.tar.gz -O lastfm-dataset-1K.tar.gz
tar -xvzf lastfm-dataset-1K.tar.gz
