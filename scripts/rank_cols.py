import os
import csv
import sys
from collections import defaultdict
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TSV_PATH = os.path.join(BASE_DIR, "../data/processed/spreadsheet/wikipedia_metadata3.tsv")
OUTPUT_PATH = os.path.join(BASE_DIR, "../data/processed/spreadsheet/rank_cols_output.txt")

csv.field_size_limit(min(sys.maxsize, 2**31 - 1)) # try to increase max buffer so it doesn't fail
#https://stackoverflow.com/questions/53538888/counting-csv-column-occurrences-on-the-fly-in-python

def main():
    lines = []

    def log(msg=""):
        print(msg)
        lines.append(str(msg))

    log(f"Reading: {TSV_PATH}")

    file_size = os.path.getsize(TSV_PATH)
    col_filled = defaultdict(int)
    row_count = 0

    with open(TSV_PATH, encoding="utf-8", buffering=4 * 1024 * 1024) as f:
        reader = csv.reader(f, delimiter="\t")
        headers = next(reader)
        num_cols = len(headers)

        with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024, desc="Processing") as pbar:
            for row in reader:
                row_count += 1
                for i, val in enumerate(row):
                    if val and val.strip():
                        col_filled[headers[i]] += 1
                pbar.update(sum(map(len, row)) + num_cols) #progress bar

    log(f"\nTotal rows: {row_count:,}")
    log(f"Total columns: {num_cols}\n")

    ranked = sorted(
        headers,
        key=lambda c: col_filled.get(c, 0) / row_count,
        reverse=True,
    )

    log(f"{'#':<5} {'Column':<40} {'Filled':>10} {'Total':>10} {'Fill %':>8}")
    log("-" * 75)
    for i, col in enumerate(ranked, 1):
        filled = col_filled.get(col, 0)
        pct = filled / row_count * 100
        log(f"{i:<5} {col:<40} {filled:>10,} {row_count:>10,} {pct:>7.1f}%")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))

    print(f"\nOutput written to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()