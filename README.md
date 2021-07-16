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

Once the Neo4j download finishes we need to go to /Neo4j-Home/bin and run the following command:

```
./neo4j console

```
This should leave our neo4j server ready to use.

## Create DB

After we have our Neo4j server running, we need to create the graphics database that we will use.

This is as simple as running the following command;

```
CREATE DATABASE osm

```

## Load Map

We use the official OSM loader for Neo4j to load the database. This loader is available [here](https://github.com/neo4j-contrib/osm).

Its necessary to have JDK 11 installed, you can follow this [link](https://docs.oracle.com/en/java/javase/11/install/installation-jdk-macos.html#GUID-7EB4F697-F3D1-40EA-ACDF-07FA90F02D57) to install it.

After the OSM loader is downloaded, its necessary to follow the tutorial (provided in the download link) to extract the to extract the jar files that we will execute when loading the database.

With the load purpouse we will use the `target/osm-0.2.3-neo4j-4.1.3.jar` file and run the following command
```
java -Xms1280m -Xmx1280m \
  -cp "target/osm-0.2.3-neo4j-4.1.3.jar:target/dependency/*" org.neo4j.gis.osm.OSMImportTool \
  --skip-duplicate-nodes --delete --into target/neo4j --database map2 samples/map2.osm.bz2

```

In this example the `target/neo4j` is the Neo4j-Home folder, the database is `map2`, and the OSM file is `map2.osm.bz2`.

**Disclaimer: the osm.bz2 format is the compressed form of the OSM file.**

## Routing Graph and Database plugins

Cnce we load the database with the plugin above, we should see a graph with node types like `OSMNode`, `OSMWay`, `OSMWayNode` and so on.
But this is not a Routing graph, to create a Routing graph we need to do some extra stuff.

1. Put the .jar files of the folder neo4j-plugins of this repository into the plugins folder of out neo4j installation
2. paste this property value into the neo4j.conf file of neo4j 






