import click

from profiler import Profiler


@click.command()
@click.option("--pathfinder", help="Must be one of ['neo4j', 'pgsql'].")
@click.option("--algorithm", help="Must be one of ['dijkstra', 'astar'].")
@click.option(
    "--experiment_name",
    help="Experiment name for the experiments.",
)
@click.option(
    "--num_threads",
    default=1,
    type=int,
    help="Number of concurrent connections.",
)
@click.option(
    "--no_mem",
    is_flag=True,
    help="Track max memory usage.",
)
def main(pathfinder, algorithm, experiment_name, num_threads, no_mem):
    prof = Profiler(measure_mem=not no_mem, num_threads=num_threads)
    prof.run_threaded_experiment(
        pathfinder, algorithm=algorithm, experiment_name=experiment_name
    )


if __name__ == "__main__":
    main()
