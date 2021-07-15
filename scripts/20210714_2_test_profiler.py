# %%
from profiler import Profiler

import scripts

prof = Profiler()

# %%
prof.run_experiments("pgsql")
# %%
from pgsql_pathfinder import PgSQLPathFinder

pgsql = PgSQLPathFinder()
# %%
pgsql.get_path(1051811745, 426930291, algorithm="astar")
# %%
