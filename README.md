## Phase 2 of genome to assembly linkage

This repo contains a script that generates a table for the branchwater-based linkage of MGnify genomes and assemblies.
The script expects that branchwater has already been executed for each species representative genome of each catalogue.

### Input

The script accepts a CSV file as input. The file should have no header and should contain the following columns:
- name of catalogue 

  *(free text, primarily for the user to distinguish between catalogues, does not need to match 
  anything on the website or in the db)*
- path to the branchwater output folder 

  *(The folder should contain results of branchwater runs for each species rep against the branchwater db. The names of the files should be <species_rep_accession>.csv. For example, MGYG000001.csv). Results for each species rep in the catalogue must be present.*  
  Example of a branchwater output file:
    ```bash
      query_name,query_md5,match_name,containment,intersect_hashes,ksize,scaled,moltype,match_md5,jaccard,max_containment,query_containment_ani
      MGYG000305249_1,e5183e097fc19da8072390cada1ef313,SRR24912637,0.2632286995515695,587,21,1000,DNA,,,,0.9384190617731216
      MGYG000305249_1,e5183e097fc19da8072390cada1ef313,SRR12529272,0.6349775784753363,1416,21,1000,DNA,,,,0.9786052524151458
      MGYG000305249_1,e5183e097fc19da8072390cada1ef313,ERR2019398,0.2632286995515695,587,21,1000,DNA,,,,0.9384190617731216
  ```
- path to the catalogue metadata table

Input file example:
```bash
human-gut,/home/user/branchwater_results_for_human_gut,/nfs/catalogues/human-gut/v2.0/ftp/genomes-all_metadata.tsv
soil,/home/user/branchwater_results_for_soil,/nfs/catalogues/soil/v1.0/ftp/genomes-all_metadata.tsv
```

### Running the script
```bash
mitload miniconda && conda activate pybase
python3 branchwater_results_to_table.py -h
usage: branchwater_results_to_table.py [-h] -i INPUT_CSV -o OUTPUT_FOLDER

Produce genome-to-assembly linkage tables from per-genome branchwater results.

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_CSV, --input_csv INPUT_CSV
                        No-header CSV with: catalogue name, branchwater results folder, catalogue metadata table
  -o OUTPUT_FOLDER, --output_folder OUTPUT_FOLDER
                        Output directory (created if missing)
```

Example:
```bash
python3 branchwater_results_to_table.py -i samplesheet.csv -o final_table_folder
```

### Output
The script will save a combined TSV file (`full_phase2_linkage_table_{date}.tsv`) to the output folder.
It will also create individual, per-catalogue outputs.

Example:
```bash
Run	Genome_Mgnify_accession	Containment	cANI
SRR17827830	MGYG000000001	1.0	1.0
ERR6501030	MGYG000000001	1.0	1.0
ERR9708953	MGYG000000001	1.0	1.0
ERR9709279	MGYG000000001	0.9996828417380272	0.9999848949442115
SRR10816049	MGYG000000001	0.9996828417380272	0.9999848949442115
SRR29449304	MGYG000000001	0.9996828417380272	0.9999848949442115
```