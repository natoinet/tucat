var temp_collection = "temp" + Math.floor(Math.random()*10000)

aggregate()
print(temp_collection)

function aggregate() {
    var unwind = { $unwind : "$" + friendfollower }
    var project
    var query

    if (friendfollower === "follower") {
        project = { $project : { follower:1, screenname:1,_id: 0 } }
    } else if (friendfollower === "following") {
        project = { $project : { following:1, screenname:1,_id: 0 } }        
    }

    if (typeof ltdate !== 'undefined') {
        var last_tweet_date = new Date(ltdate)
        query = {$match : { friendfollower : { $ne : [ ]}, 'dtstatuscreatedat' : {$gte : last_tweet_date}}}
    }
    else {
        query = {$match : { friendfollower : { $ne : [ ] }}}
    }

    db.getSiblingDB(dbname)[colname].aggregate( [ query, project, unwind, { $out : temp_collection } ] ) 
}

