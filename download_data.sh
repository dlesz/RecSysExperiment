#!/bin/bash


fileid="1vug_nZfSbFy9TneLk_hnFgVo5NbwMgh6"
filename="recsys_data.tar.gz"
curl -c ./cookie -s -L "https://drive.google.com/uc?export=download&id=${fileid}" > /dev/null
curl -Lb ./cookie "https://drive.google.com/uc?export=download&confirm=`awk '/download/ {print $NF}' ./cookie`&id=${fileid}" -o ${filename}

tar -xvf recsys_data.tar.gz -C ./flaskapp/data

rm recsys_data.tar.gz cookie

wget -P flaskapp/data/ https://github.com/benfred/recommender_data/releases/download/v1.0/lastfm_360k.hdf5
