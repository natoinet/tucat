#!/bin/bash
# ./friendsgraph.sh '<COLLECTION_NAME>' 'PATH'
# Run with ./friendsgraph.sh '2014-12-05' '/Users/blourp/src/tucat/tucat/twitter_extraction/export/'

DBNAME=$1
COLNAME=$2
EXP_PATH=$3
OUTPUT_FILES=$4

#OUTPUT_FILES="/Users/antoinebrunel/Downloads"
#DBNAME=tucat_twitter_extraction
QUERY='{follower : { $ne : [ ]}}'
MONGO_FIELDS_NODE='screenname,name,topuser,followerscount,listedcount,statusescount,friendscount,lang,statussource,statuscreatedat'
GRAPH_FIELDS_NODE='nodedef>name VARCHAR,label VARCHAR,type VARCHAR, followerscount INT,listedcount INT,statusescount INT,friendscount INT,lang VARCHAR,statussource VARCHAR,statuscreatedat VARCHAR'
MONGO_FIELDS_EDGE='follower,screenname'
GRAPH_FIELDS_EDGE='edgedef>node1 VARCHAR,node2 VARCHAR'
FRIENDORFOLLOWER='follower'

#echo "OXSI-TUCAT: Starting data export"

#echo "Step 1> Aggregating Mongodb data"
COLLECTION=$(mongo --quiet --host $MONGOHOST --eval "var dbname='$DBNAME', colname='$COLNAME', friendfollower='$FRIENDORFOLLOWER'" "$EXP_PATH"aggregation.js)

#echo "Step 2> Exporting node data > archivo-node-$1-$COLLECTION.csv"
mongoexport --quiet --host $MONGOHOST --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin --db $DBNAME --collection $COLNAME --fields $MONGO_FIELDS_NODE --query "$QUERY" --csv -o "$OUTPUT_FILES/archivo-node-$COLNAME-$COLLECTION.csv"
sed "1s/.*/$GRAPH_FIELDS_NODE/" "$OUTPUT_FILES/archivo-node-$COLNAME-$COLLECTION.csv" > "$OUTPUT_FILES/archivo-node-mod-$COLNAME-$COLLECTION.csv"

#echo "Step 3> Exporting edge data > archivo-ejes-edge-$1-$COLLECTION.csv"
mongoexport --quiet --host $MONGOHOST --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin --db $DBNAME --collection $COLLECTION --fields $MONGO_FIELDS_EDGE --csv -o "$OUTPUT_FILES/archivo-edge-$COLNAME-$COLLECTION.csv"
sed "1s/.*/$GRAPH_FIELDS_EDGE/" "$OUTPUT_FILES/archivo-edge-$COLNAME-$COLLECTION.csv" > "$OUTPUT_FILES/archivo-edge-mod-$COLNAME-$COLLECTION.csv"

#echo "Step 4> Merging node & edge files"
cat "$OUTPUT_FILES/archivo-node-mod-$COLNAME-$COLLECTION.csv" "$OUTPUT_FILES/archivo-edge-mod-$COLNAME-$COLLECTION.csv" >> "$OUTPUT_FILES/grafo-friends-$COLNAME-$COLLECTION.gdf"

mongo --quiet --host $MONGOHOST --username $MONGO_INITDB_ROOT_USERNAME --password $MONGO_INITDB_ROOT_PASSWORD admin --eval "db.getSiblingDB('$DBNAME')['$COLLECTION'].drop()"

#echo "Finished> $OUTPUT_FILES/grafo-friends-$1-$COLLECTION.gdf - Thank you for your patience."
echo "grafo-friends-$COLNAME-$COLLECTION.gdf"
