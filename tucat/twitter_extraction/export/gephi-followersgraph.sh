#!/bin/bash
# ./followersgraph.sh '<COLLECTION_NAME>' 'PATH'
# Run with ./followersgraph.sh '2014-12-05' '/Users/blourp/src/tucat/tucat/twitter_extraction/export/'

OUTPUT_FILES="/Users/antoinebrunel/Downloads"
DBNAME=tucat_twitter_extraction
QUERY='{following : { $ne : [ ]}}'
MONGO_FIELDS_NODE='screenname,name,topuser,followerscount,listedcount,statusescount,friendscount,lang,statussource,statuscreatedat'
GRAPH_FIELDS_NODE='nodedef>name VARCHAR,label VARCHAR,type VARCHAR, followerscount INT,listedcount INT,statusescount INT,friendscount INT,lang VARCHAR,statussource VARCHAR,statuscreatedat VARCHAR'
MONGO_FIELDS_EDGE='following,screenname'
GRAPH_FIELDS_EDGE='edgedef>node1 VARCHAR,node2 VARCHAR'
FRIENDORFOLLOWER='following'

#echo "OXSI-TUCAT: Starting data export"

#echo "Step 1> Aggregating Mongodb data"
COLLECTION=$(mongo --quiet --eval "var dbname='$DBNAME', colname='$1', friendfollower='$FRIENDORFOLLOWER'" $2aggregation.js)

#echo "Step 2> Exporting node data > archivo-node-$1-$COLLECTION.csv"
mongoexport --quiet --db $DBNAME --collection $1 --fields $MONGO_FIELDS_NODE --query "$QUERY" --csv -o "$OUTPUT_FILES/archivo-node-$1-$COLLECTION.csv"
sed "1s/.*/$GRAPH_FIELDS_NODE/" "$OUTPUT_FILES/archivo-node-$1-$COLLECTION.csv" > "$OUTPUT_FILES/archivo-node-mod-$1-$COLLECTION.csv"

#echo "Step 3> Exporting edge data > archivo-ejes-edge-$1-$COLLECTION.csv"
mongoexport --quiet --db $DBNAME --collection $COLLECTION --fields $MONGO_FIELDS_EDGE --csv -o "$OUTPUT_FILES/archivo-edge-$1-$COLLECTION.csv"
sed "1s/.*/$GRAPH_FIELDS_EDGE/" "$OUTPUT_FILES/archivo-edge-$1-$COLLECTION.csv" > "$OUTPUT_FILES/archivo-edge-mod-$1-$COLLECTION.csv"

#echo "Step 4> Merging node & edge files"
cat "$OUTPUT_FILES/archivo-node-mod-$1-$COLLECTION.csv" "$OUTPUT_FILES/archivo-edge-mod-$1-$COLLECTION.csv" >> "$OUTPUT_FILES/grafo-followers-$1-$COLLECTION.gdf"

mongo --quiet --eval "db.getSiblingDB('$DBNAME')['$COLLECTION'].drop()"

#echo "Finished> $OUTPUT_FILES/grafo-followers-$1-$COLLECTION.gdf - Thank you for your patience."
echo "$OUTPUT_FILES/grafo-followers-$1-$COLLECTION.gdf"
