import csv
import pytest

import branchwater_results_to_table as mod


# -------------------------
# Helpers
# -------------------------

def write_csv(path, header, rows, delimiter=","):
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, delimiter=delimiter)
        writer.writerow(header)
        writer.writerows(rows)


def read_tsv(path):
    with path.open(newline="") as fh:
        return list(csv.reader(fh, delimiter="\t"))


# -------------------------
# load_metadata_table
# -------------------------

def test_load_metadata_table(tmp_path):
    meta = tmp_path / "metadata.tsv"
    write_csv(
        meta,
        header=["Species_rep", "GC_content"],
        rows=[
            ["MGYG0001", "66.4"],
            ["MGYG0002.1", "53.4"],
            ["MGYG0001", "43.1"],  # duplicate should be deduplicated
        ],
        delimiter="\t",
    )

    reps = mod.load_metadata_table(meta)

    assert reps == {"MGYG0001", "MGYG0002.1"}


# -------------------------
# get_csvs
# -------------------------

def test_get_csvs_all_present(tmp_path):
    reps = {"MGYG0001", "MGYG0002.1"}

    (tmp_path / "MGYG0001.csv").touch()
    (tmp_path / "MGYG0002.1.csv").touch()
    (tmp_path / "combined_results.csv").touch()

    csvs, missing = mod.get_csvs(tmp_path, reps)

    assert csvs == ["MGYG0001.csv", "MGYG0002.1.csv"]
    assert missing == set()


def test_get_csvs_missing_files(tmp_path):
    reps = {"MGYG0001", "MGYG0002.1"}

    (tmp_path / "MGYG0001.csv").touch()

    csvs, missing = mod.get_csvs(tmp_path, reps)

    assert csvs == ["MGYG0001.csv", "MGYG0002.1.csv"]
    assert missing == {"MGYG0002.1.csv"}


# -------------------------
# process_branchwater_file
# -------------------------

def test_process_branchwater_file_filters_by_containment(tmp_path):
    infile = tmp_path / "MGYG0001.csv"

    write_csv(
        infile,
        header=[
            "match_name",
            "query_name",
            "containment",
            "query_containment_ani",
        ],
        rows=[
            ["RUN1", "MGYG0001_1", "0.4", "95.1"],  # filtered out
            ["RUN2", "MGYG0001_1", "0.5", "96.2"],  # kept
            ["RUN3", "MGYG0001_1", "0.9", "97.3"],  # kept
        ],
    )

    cat_out = tmp_path / "cat.tsv"
    full_out = tmp_path / "full.tsv"

    with cat_out.open("w", newline="") as cat_fh, full_out.open("w", newline="") as full_fh:
        cat_writer = csv.writer(cat_fh, delimiter="\t")
        full_writer = csv.writer(full_fh, delimiter="\t")

        mod.process_branchwater_file(infile, cat_writer, full_writer)

    cat_rows = read_tsv(cat_out)
    full_rows = read_tsv(full_out)

    assert cat_rows == [
        ["RUN2", "MGYG0001", "0.5", "96.2"],
        ["RUN3", "MGYG0001", "0.9", "97.3"],
    ]
    assert cat_rows == full_rows


def test_process_branchwater_file_missing_containment(tmp_path):
    infile = tmp_path / "bw.csv"

    write_csv(
        infile,
        header=["match_name", "query_name"],
        rows=[["RUN1", "MGYG0001_1"]],
    )

    with pytest.raises(KeyError, match="containment"):
        with infile.open():
            mod.process_branchwater_file(infile, None, None)


def test_process_branchwater_file_invalid_containment(tmp_path):
    infile = tmp_path / "bw.csv"

    write_csv(
        infile,
        header=[
            "match_name",
            "query_name",
            "containment",
            "query_containment_ani",
        ],
        rows=[["RUN1", "MGYG0001_1", "not_a_number", "95.0"]],
    )

    with pytest.raises(ValueError, match="Invalid containment"):
        with infile.open():
            mod.process_branchwater_file(infile, None, None)


# -------------------------
# process_catalogue
# -------------------------

def test_process_catalogue_happy_path(tmp_path):
    # Metadata
    metadata = tmp_path / "metadata.tsv"
    write_csv(
        metadata,
        header=["Species_rep"],
        rows=[["MGYG0001"], ["MGYG0002.1"]],
        delimiter="\t",
    )

    # Branchwater folder
    bw_dir = tmp_path / "bw"
    bw_dir.mkdir()

    write_csv(
        bw_dir / "MGYG0001.csv",
        header=[
            "match_name",
            "query_name",
            "containment",
            "query_containment_ani",
        ],
        rows=[["RUN1", "MGYG0001_1", "0.8", "95.0"]],
    )

    write_csv(
        bw_dir / "MGYG0002.1.csv",
        header=[
            "match_name",
            "query_name",
            "containment",
            "query_containment_ani",
        ],
        rows=[["RUN2", "MGYG0002.1_1", "0.9", "96.0"]],
    )

    output_dir = tmp_path / "out"
    output_dir.mkdir()

    full_out = tmp_path / "full.tsv"
    with full_out.open("w", newline="") as fh:
        full_writer = csv.writer(fh, delimiter="\t")

        count = mod.process_catalogue(
            catalogue="cat-fur",
            branchwater_folder=bw_dir,
            metadata_table=metadata,
            output_folder=output_dir,
            date_suffix="2025-01-01",
            full_writer=full_writer,
        )

    assert count == 2

    cat_file = output_dir / "cat-fur_phase2_linkage_table_2025-01-01.tsv"
    rows = read_tsv(cat_file)

    assert rows[0] == mod.HEADER
    assert len(rows) == 3  # header + 2 records


def test_process_catalogue_missing_csv_raises(tmp_path):
    metadata = tmp_path / "metadata.tsv"
    write_csv(
        metadata,
        header=["Species_rep"],
        rows=[["rep1"]],
        delimiter="\t",
    )

    bw_dir = tmp_path / "bw"
    bw_dir.mkdir()

    output_dir = tmp_path / "out"
    output_dir.mkdir()

    with pytest.raises(FileNotFoundError, match="Missing CSV files"):
        mod.process_catalogue(
            catalogue="cat-fur",
            branchwater_folder=bw_dir,
            metadata_table=metadata,
            output_folder=output_dir,
            date_suffix="2025-01-01",
            full_writer=None,
        )
