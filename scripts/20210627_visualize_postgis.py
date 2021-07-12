# %%
import geopandas
from sqlalchemy import create_engine

import scripts

# %%
db_connection_url = "postgresql://postgres:password@localhost:5432/postgres"
con = create_engine(db_connection_url)
# %%
sql = "SELECT the_geom FROM ways"
df = geopandas.GeoDataFrame.from_postgis(sql, con, geom_col="the_geom")

# %%
df.plot()
# %%
DIJKSTRA_QUERY = """
SELECT * FROM pgr_dijkstra('
                SELECT gid as id,
                         source::integer,
                         target::integer,
                         cost::double precision as cost
                        FROM ways',
                {}, {}, false);
"""

ASTAR_QUERY = """
SELECT * FROM pgr_astar('
    SELECT gid::integer AS id,
         source::integer,
         target::integer,
         length::double precision AS cost,
         x1, y1, x2, y2
        FROM ways',
    {}, {}, false);
"""
# %%
df = geopandas.GeoDataFrame.from_postgis(sql, con, geom_col="the_geom")
# %%
from pgsql_pathfinder import PgSQLPathFinder

path_finder = PgSQLPathFinder()
# %%
path_finder.get_path(1, 300)
# %%
