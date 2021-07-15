import psycopg2

QUERIES = {
    "dijkstra": """
SELECT * FROM pgr_dijkstra('
                SELECT gid as id,
                         source_osm::bigint as source,
                         target_osm::bigint as target,
                         cost::double precision as cost
                        FROM ways',
                {}, {}, false);
""",
    "astar": """
SELECT * FROM pgr_astar('
    SELECT gid::integer AS id,
         source_osm::bigint as source,
         target_osm::bigint as target,
         length::double precision AS cost,
         x1, y1, x2, y2
        FROM ways',
    {}, {}, false);
""",
}


class PgSQLPathFinder:
    def __init__(
        self,
        host="localhost",
        database="postgres",
        user="postgres",
        password="password",
        default_algo="dijkstra",
    ):
        self.conn = psycopg2.connect(
            host=host, database=database, user=user, password=password
        )
        self.default_algo = default_algo

    def get_path(self, source_gid, target_gid, algorithm=None):
        algorithm = algorithm if algorithm else self.default_algo

        query = QUERIES[algorithm].format(source_gid, target_gid)

        with self.conn.cursor() as cur:
            cur.execute(query)
            rs = cur.fetchall()

        return rs
