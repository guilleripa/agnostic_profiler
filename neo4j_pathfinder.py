from neo4j import GraphDatabase

QUERIES = {
    "dijkstra": """
    MATCH (n:Intersection)
        WHERE n.node_osm_id = $source_gid
    MATCH (p:Intersection)
        WHERE p.node_osm_id = $target_gid
    CALL apoc.algo.dijkstra(n,p,'ROUTE','distance')
    YIELD path AS j
    RETURN j
    """,
    "astar": """
    MATCH (n:Intersection)
       WHERE n.node_osm_id = $source_gid
    MATCH (p:Intersection)
        WHERE p.node_osm_id = $target_gid
    CALL apoc.algo.aStar(n,p,'ROUTE','distance','lat','lon')
    YIELD path AS j
    RETURN j
    """,
}


class Neo4jPathFinder:
    def __init__(
        self,
        host="localhost",
        port="7687",
        user="neo4j",
        password="pass",
        default_algorithm="dijkstra",
    ):
        self.driver = GraphDatabase.driver(
            "bolt://" + host + ":" + port, auth=(user, password)
        )
        self.default_algorithm = default_algorithm

    def close(self):
        self.driver.close()

    def get_path(self, source_gid, target_gid, algorithm=None):
        algorithm = algorithm if algorithm else self.default_algorithm
        query = QUERIES[algorithm]
        with self.driver.session() as session:
            with session.begin_transaction() as tx:
                aux = tx.run(query, source_gid=source_gid, target_gid=target_gid)
                for record in aux:
                    result = record.data()
                    print(result)
        return result


# TEST
if __name__ == "__main__":
    greeter = Neo4jPathFinder()
    coso = greeter.get_path(287752964, 259017838)
    greeter.close()
