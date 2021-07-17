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
    "--no_mem",
    is_flag=True,
    help="Experiment name for the experiments.",
)
def main(pathfinder, algorithm, experiment_name, no_mem):
    prof = Profiler(measure_mem=not no_mem)
    prof.run_experiments(
        pathfinder, algorithm=algorithm, experiment_name=experiment_name
    )


if __name__ == "__main__":
    main()
