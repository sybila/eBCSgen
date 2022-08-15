[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6644973.svg)](https://doi.org/10.5281/zenodo.6644973)
[![Docker Pulls](https://badgen.net//docker/pulls/sybila/ebcsgen?icon=docker)](https://hub.docker.com/r/sybila/ebcsgen/)
[![Install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat)](http://bioconda.github.io/recipes/ebcsgen/README.html)

[![Python Package using Conda](https://github.com/sybila/eBCSgen/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/sybila/eBCSgen/actions/workflows/python-package-conda.yml)
[![docs](https://readthedocs.org/projects/ebcsgen/badge/?version=latest)](https://ebcsgen.readthedocs.io/en/latest/)

# eBCSgen

eBSCgen is a tool for development and analysis of models written in Biochemical Space Language (BCSL). 

The tool is deployed online as a part of [BioDivine](https://biodivine-vm.fi.muni.cz/galaxy/) Galaxy toolset.

For more information about the tool, see [Wiki](https://github.com/sybila/eBCSgen/wiki).

**To get started with the usage of Galaxy Platform and eBCSgen, we recommend this [tutorial](https://www.fi.muni.cz/~xtrojak/files/papers/eBCSgen_tutorial.pdf).**

## Installation

### Conda

Install `eBCSgen` from Bioconda with:

```
# install eBCSgen in a new virtual environment to avoid dependency clashes
conda create --name eBCSgen python=3.9
conda activate eBCSgen
conda install --channel bioconda --channel conda-forge eBCSgen
```

### Docker

You can also use prebuild [docker image](https://hub.docker.com/r/sybila/ebcsgen).

## Developer Documentation

### Setup

Create your development environment using the provided [script](conda/environment.yml) via conda to install all required dependencies.

### Contributing

We appreciate contributions - feel free to open an issue on our repository, create your own fork, work on the problem and post a PR. 
Please adhere to the [versioning](https://semver.org/spec/v2.0.0.html).

### Testing

All functionality is tested with the [pytest](https://docs.pytest.org/en/6.2.x/contents.html) framework.
