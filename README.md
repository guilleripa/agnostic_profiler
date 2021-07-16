# Relational

## Set up

We'll be using the official pgrouting Docker image to run our relational database.

First we pull the image for Docker Hub and run it.
```
docker pull pgrouting/pgrouting
docker run --name pgrouting -e POSTGRES_PASSWORD=password -p 5432:5432 pgrouting/pgrouting
```

After we've runned ir once we can leave running. If we ever close it and need to start it up again we do:
```
docker start -i pgrouting
```

### Create DB and extensions

Once our pgsql DB is running we'll need to add some extensions to it.

```
docker exec -ti pgrouting psql -U postgres

# inside postgres
CREATE EXTENSION postgis;
CREATE EXTENSION hstore;
CREATE EXTENSION pgrouting;
```

### Load map

To load our maps we'll be using `osm2pgrouting` which translates an OSM XML file into postgis compatible commands and loads the DB.

To install with homebrew it's just:
```
brew install osm2pgrouting
```

To run the command which loads the pgrouting db you will need a config file. We are using `mapconfig_for_cars.xml` which you can find at the root of this project.

The command to run is:
```
osm2pgrouting --file ~/Downloads/map.osm  --conf mapconfig_for_cars.xml -d postgres -U postgres -W password
```
it will create all necessary tables to load the `.osm` file.

# Graphs

## Set up

We'll be using Neo4j Enterprise in his 4.3.2 version available [here](https://neo4j.com/download-center/).

Once the Neo4j download finishes we need to go to `/Neo4j-Home/bin` and run the following command:

```
./neo4j console

```
This should leave our neo4j server ready to use.

## Create DB

After we have our Neo4j server running, we need to create the graps database that we will use.

This is as simple as running the following command;

```
CREATE DATABASE osm

```

## Load Map

We use the official OSM loader for Neo4j to load the database. This loader is available [here] (https://github.com/neo4j-contrib/osm).

It's necessary to have JDK 11 installed, you can follow this [link](https://docs.oracle.com/en/java/javase/11/install/installation-jdk-macos.html#GUID-7EB4F697-F3D1-40EA-ACDF-07FA90F02D57) to install it, (Maven it's necessary to).

After the OSM loader is downloaded, it's necessary to follow the tutorial (provided in the download link) to extract the jar files that we will excecute to load the database.

With the load purpose we will use the `target/osm-0.2.3-neo4j-4.1.3.jar` file and run the following command
```
java -Xms1280m -Xmx1280m \
  -cp "target/osm-0.2.3-neo4j-4.1.3.jar:target/dependency/*" org.neo4j.gis.osm.OSMImportTool \
  --skip-duplicate-nodes --delete --into target/neo4j --database map2 samples/map2.osm.bz2



```

In this example the `target/neo4j` is the Neo4j-Home folder, the database is `map2`, and the OSM file is `map2.osm.bz2`.

**Disclaimer: the osm.bz2 format is the compressed form of the OSM file.**

## Routing Graph and Database plugins

Since we load the database with the plugin above, we should see a graph with node types like `OSMNode`, `OSMWay`, `OSMWayNode` and so on.
But this is not a Routing graph, to create a Routing graph we need to do some extra stuff.

1. Put the .jar files of the folder neo4j-plugins of this repository into the plugins folder of out neo4j installation
2. Paste this property values into the neo4j.conf file of our neo4j installation.

```
dbms.default_database=osm_database 
dbms.security.procedures.unrestricted=algo.*,apoc.*

```
3. Restart Neo4j 
3. Execute the following queries in the following order:

```
CREATE INDEX ON :OSMTags(amenity);
CREATE INDEX ON :OSMTags(description);
CREATE INDEX ON :OSMTags(food);
CREATE INDEX ON :OSMTags(highway);
CREATE INDEX ON :OSMTags(restaurant);
CREATE INDEX ON :Intersection(location);
CREATE INDEX ON :Routable(location);
CREATE INDEX ON :PointOfInterest(location);
CREATE INDEX ON :OSMNode(location);
CREATE INDEX ON :PointOfInterest(name);

```

```
CALL apoc.periodic.iterate( 
    'MATCH (awn:OSMWayNode)-[r:NEXT]-(bwn:OSMWayNode) WHERE NOT exists(r.distance) RETURN awn,bwn,r',
    'MATCH (awn)-[:NODE]->(a:OSMNode), (bwn)-[:NODE]->(b:OSMNode) SET r.distance = distance(a.location,b.location)',
    {batchSize:10000, parallel: false}
);
```

```
CALL apoc.periodic.iterate(
    'MATCH (n:OSMNode) WHERE NOT (n:Intersection)
    AND size((n)<-[:NODE]-(:OSMWayNode)-[:NEXT]-(:OSMWayNode)) > 2 RETURN n',
    'MATCH (n)<-[:NODE]-(wn:OSMWayNode), (wn)<-[:NEXT*0..100]-(wx),
        (wx)<-[:FIRST_NODE]-(w:OSMWay)-[:TAGS]->(wt:OSMTags)
    WHERE exists(wt.highway) AND NOT n:Intersection
    SET n:Intersection',
    {batchSize:10000, parallel:true}
);
```

```
CALL apoc.periodic.iterate(
'MATCH (x:Intersection) RETURN x',
'CALL spatial.osm.routeIntersection(x,true,false,false)
   YIELD fromNode, toNode, fromRel, toRel, distance, length, count
 WITH fromNode, toNode, fromRel, toRel, distance, length, count
 MERGE (fromNode)-[r:ROUTE {fromRel:id(fromRel),toRel:id(toRel)}]->(toNode)
   ON CREATE SET r.distance = distance, r.length = length, r.count = count
 RETURN count(*)',
{batchSize:100, parallel:false});
```

```
MATCH (x:Intersection) WITH x
  CALL spatial.osm.routeIntersection(x,false,false,false)
  YIELD fromNode, toNode, fromRel, toRel, distance, length, count
WITH fromNode, toNode, fromRel, toRel, distance, length, count
MERGE (fromNode)-[r:ROUTE {fromRel:id(fromRel),toRel:id(toRel)}]->(toNode)
  ON CREATE SET r.distance = distance, r.length = length, r.count = count
RETURN count(*);
```

**Disclaimer: This queries could take a few minutes**

For further information or more detailed info you can follow [this](https://neo4j.com/graphconnect-2018/session/neo4j-spatial-mapping?_gl=1*vdg4vh*_ga*MTk4MzY5NDI1NS4xNjI1MjQ5NjAw*_ga_DL38Q8KGQC*MTYyNjQwNDY5Mi4xNC4xLjE2MjY0MDU0NjguMA..&_ga=2.92762397.1474005215.1626397978-1983694255.1625249600) tutorial.

## Testing

if everything happened as expected, we have a routing graph ready to be used.

Shortest path queries example:

**Dijkstra**

```
match (n:Intersection) 
    where n.node_osm_id = 4158708257
match (p:Intersection) 
    where p.node_osm_id = 279933912
CALL apoc.algo.dijkstra(n,p,'ROUTE','distance')
YIELD path as j
return j;
```

**A***

```
match (n:Intersection) 
    where n.node_osm_id = 4158708257
match (p:Intersection) 
    where p.node_osm_id = 279933912
CALL apoc.algo.aStar(n,p,'ROUTE','distance','lat','lon')
YIELD path as j
return j;
```












