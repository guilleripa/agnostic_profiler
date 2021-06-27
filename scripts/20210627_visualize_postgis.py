# %%
import geopandas
from sqlalchemy import create_engine

# %%
db_connection_url = "postgresql://postgres:password@localhost:5432/postgres"
con = create_engine(db_connection_url)
sql = "SELECT way FROM planet_osm_roads"
df = geopandas.GeoDataFrame.from_postgis(sql, con, geom_col="way")

# %%
df.plot()
# %%
