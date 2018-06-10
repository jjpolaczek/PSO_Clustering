#!/usr/bin/env bash
#Mount library here
sudo ./mountdb.sh

python main.py --library_path=./books/indexes --cluster_retries=1 --no_clusters=20 --lsa=50 --n-features=10000
