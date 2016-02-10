#!/bin/bash
# ./friendsgraph.sh '<COLLECTION_NAME>' 'PATH'
# Run with ./friendsgraph.sh '2014-12-05' '/Users/blourp/src/tucat/tucat/twitter_extraction/export/'

OUTPUT_FILES="/Users/antoinebrunel/Downloads"
DBNAME=politweaks
QUERY='{follower : { $ne : [ ]}}'
MONGO_FIELDS_NODE='screenname,name,topuser,followerscount,listedcount,statusescount,friendscount,lang,statussource,statuscreatedat'
GRAPH_FIELDS_NODE='nodedef>name VARCHAR,label VARCHAR,type VARCHAR, followerscount INT,listedcount INT,statusescount INT,friendscount INT,lang VARCHAR,statussource VARCHAR,statuscreatedat VARCHAR'
MONGO_FIELDS_EDGE='follower,screenname'
GRAPH_FIELDS_EDGE='edgedef>node1 VARCHAR,node2 VARCHAR'
FRIENDORFOLLOWER='follower'

#echo "OXSI-TUCAT: Starting data export"

#echo "Step 1> Aggregating Mongodb data"
COLLECTION=$(mongo --quiet --eval "var dbname='$DBNAME', colname='$1', friendfollower='$FRIENDORFOLLOWER'" $2aggregation.js)

#echo "Step 2> Exporting node data > archivo-node-$1-$COLLECTION.csv"
mongoexport --quiet --db $DBNAME --collection $1 --fields $MONGO_FIELDS_NODE --query "$QUERY" --csv -o "$OUTPUT_FILES/summary-node-$1-$COLLECTION.csv"
mongo --quiet --eval "db.getSiblingDB('$DBNAME')['$COLLECTION'].drop()"

echo "$OUTPUT_FILES/summary-node-$1-$COLLECTION.csv"