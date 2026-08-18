"""make eval entrypoint: retrieval evaluation against the curated set."""

import logging

from app.evaluation.harness import run_retrieval_eval

logging.basicConfig(level=logging.INFO)


def main():
    results = run_retrieval_eval("curated")
    print("RETRIEVAL EVAL")
    for metric, value in results.items():
        print(f"  {metric}: {value:.3f}")


if __name__ == "__main__":
    main()