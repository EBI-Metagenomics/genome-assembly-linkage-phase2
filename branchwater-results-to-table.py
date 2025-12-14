#!/usr/bin/env python3

import argparse
import os
import csv
from tqdm import tqdm


def main():
    parser = argparse.ArgumentParser(description="Process containment CSV files.")
    parser.add_argument("--input_folder", required=True, help="Path to the input folder containing CSV files")
    parser.add_argument("--outfile", required=True, help="Path to the output tab-delimited file")
    args = parser.parse_args()

    input_folder = args.input_folder
    outfile_path = args.outfile

    csv_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".csv")]

    # Prepare output file
    with open(outfile_path, "w", newline="") as outfile:
        writer = csv.writer(outfile, delimiter="\t")
        writer.writerow(["Run", "Genome_Mgnify_accession", "Containment", "cANI"])

        # Loop through all CSV files
        for fname in tqdm(csv_files, desc="Processing files", unit="file"):
            if not fname.lower().endswith(".csv"):
                continue

            fpath = os.path.join(input_folder, fname)

            with open(fpath, newline="") as infile:
                reader = csv.DictReader(infile)

                for row in reader:
                    try:
                        containment = float(row["containment"])
                    except (ValueError, KeyError):
                        continue

                    # Filter on containment >= 0.5
                    if containment < 0.5:
                        continue

                    run = row["match_name"]
                    genome = row["query_name"].split("_")[0]  # remove underscore and everything after
                    cani = row.get("query_containment_ani")

                    writer.writerow([run, genome, containment, cani])


if __name__ == "__main__":
    main()
