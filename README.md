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

To load our maps we'll be using `osm2pgsql` which translates an OSM XML file into postgis compatible commands and loads the DB.

To install with homebrew it's just:
```
brew install osm2pgsql
```

The command to run is:
```
osm2pgsql -U postgres -W -d postgres -H localhost -P 5432 --hstore --hstore-add-index ~/Downloads/map.osm
```
it will prompt for the DB's password and load the `.osm` file.
