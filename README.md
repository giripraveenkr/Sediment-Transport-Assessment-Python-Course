# Open Python for WRR Data Project - Starter Template

This repository is a starter for the student project. It gives you a clean, reproducible Python setup for WRR analyses with geodata and GDAL.

## Quick start

Either use conda, or light-weight mamba:

1. Install [mamba](https://mamba.readthedocs.io).
2. Create the environment:
   ```bash
   mamba env create -f environment.yml
   mamba activate wrr-proj
   ```
3. Run the pipeline end-to-end:
   ```bash
   make all
   ```

## Repo structure
```
.
├── CITATION.cff
├── LICENSE
├── Makefile
├── environment.yml
├── pyproject.toml
├── ruff.toml
├── .pre-commit-config.yaml
├── .gitignore
├── notebooks/
├── src/wrr/
├── data/            # not tracked; add links and checksums to data/README.md
├── gdal/
├── prompts/
├── results/         # generated outputs
└── figures/         # generated figures
```

## What you must customize
1. Edit `notebooks/results_discussions.ipynb` with your site, flows, and parameters.
2. Replace placeholder GDAL steps in `src/wrr/gdal_utils.py` with your AOI (area of interest) and CRS.
3. Fill `data/README.md` with your sources, licenses, and checksums.
4. Keep the AI diary in `prompts/AI_DIARY_TEMPLATE.md` up to date.

## Make targets
```bash
make data      # prepare small example tiles or downloads (you edit)
make build     # run analyses and generate figures
make test      # run unit tests
make lint      # ruff + black check
make fmt       # format code
make clean     # remove outputs
make all       # data + build + test
```

## Notes

Heavy geospatial libraries (1+ GB) are installed from conda-forge via `environment.yml` for reliability.

