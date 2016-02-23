#!/bin/bash
# ./followersgraph-lasttweet.sh '<COLLECTION_NAME>' <UNIX_TIMESTAMP>
# Run with ./followersgraph-lasttweet.sh '2014-12-05' 1417456357000
# Use a unix timestamp generation tool such as http://www.epochconverter.com/ (Timestamp in milliseconds)

OUTPUT_FILES="/Users/antoinebrunel/Downloads"
DBNAME=twitter_extraction
QUERY="{following : {\$ne : [ ]}, dtstatuscreatedat : {\$gte : new Date($2) }}"
MONGO_FIELDS_NODE='screenname,name,topuser,followerscount,listedcount,statusescount,friendscount,lang,statussource,statuscreatedat'
GRAPH_FIELDS_NODE='nodedef>name VARCHAR,label VARCHAR,type VARCHAR, followerscount INT,listedcount INT,statusescount INT,friendscount INT,lang VARCHAR,statussource VARCHAR,statuscreatedat VARCHAR'
MONGO_FIELDS_EDGE='following,screenname'
GRAPH_FIELDS_EDGE='edgedef>node1 VARCHAR,node2 VARCHAR'
FRIENDORFOLLOWER='following'

#echo "OXSI-TUCAT: Starting data export"

#echo "Step 1> Aggregating Mongodb data"
COLLECTION=$(mongo --quiet --eval "var dbname='$DBNAME', colname='$1', ltdate=$2, friendfollower='$FRIENDORFOLLOWER'" $3aggregation.js)

#echo "Step 2> Exporting node data > archivo-node-$1-$COLLECTION.csv"
mongoexport --quiet --db $DBNAME --collection $1 --fields $MONGO_FIELDS_NODE --query "$QUERY" --csv -o "$OUTPUT_FILES/summary-node-$1-$2-$COLLECTION.csv"
mongo --quiet --eval "db.getSiblingDB('$DBNAME')['$COLLECTION'].drop()"

echo "$OUTPUT_FILES/summary-node-$1-$2-$COLLECTION.csv"
