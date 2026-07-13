"""CLI entry point for the e-commerce sales analytics pipeline.

Usage:
    python main.py generate     # create synthetic raw data
    python main.py clean        # clean raw -> processed
    python main.py load-db      # load processed data into SQLite
    python main.py visualize    # generate chart PNGs into reports/figures
    python main.py run-all      # do all of the above, in order
"""

import argparse

from src import data_cleaning, data_generator, database, visualize


def cmd_generate(_args: argparse.Namespace) -> None:
    data_generator.main()


def cmd_clean(_args: argparse.Namespace) -> None:
    summary = data_cleaning.run_cleaning_pipeline()
    data_cleaning.print_summary(summary)


def cmd_load_db(_args: argparse.Namespace) -> None:
    database.load_warehouse()


def cmd_visualize(_args: argparse.Namespace) -> None:
    visualize.generate_all_figures()


def cmd_run_all(args: argparse.Namespace) -> None:
    cmd_generate(args)
    cmd_clean(args)
    cmd_load_db(args)
    cmd_visualize(args)
    print("\nPipeline complete. Try: streamlit run dashboard/app.py")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="E-commerce sales analytics pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("generate", help="Generate synthetic raw data").set_defaults(
        func=cmd_generate
    )
    subparsers.add_parser("clean", help="Clean raw data into data/processed").set_defaults(
        func=cmd_clean
    )
    subparsers.add_parser("load-db", help="Load processed data into SQLite").set_defaults(
        func=cmd_load_db
    )
    subparsers.add_parser("visualize", help="Generate chart PNGs").set_defaults(
        func=cmd_visualize
    )
    subparsers.add_parser("run-all", help="Run the full pipeline end to end").set_defaults(
        func=cmd_run_all
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
