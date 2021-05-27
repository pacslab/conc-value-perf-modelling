![GitHub](https://img.shields.io/github/license/pacslab/conc-value-perf-modelling)

# Analysis of Metric-Based Autoscaling in Serverless Computing

Package, experimentation results, and other artifacts for our serverless computing performance modeling paper. Using the presented performance model, the serverless computing platform provider and their users can optimize their workload and configurations to adapt to each workload being executed on them. The presented model uses analytical model to calculate steady-state system characteristics.

## Artifacts

Here is a list of different artifacts for the proposed model:

- [Deployment Code for Experimental Data Collection](./experiments/)
- [Experimentation and Parsing Code](./experiments/parse_multiple.ipynb)
- [Workload Profile Extraction Code](./experiments/parse_multiple_merged.ipynb)
- [Workloads and Results](./workloads/)
- [Model Implementation](./model/)

## Requirements

- Python 3.7+
- PIP

## Knative Installation

To run the experiments, you need to install `Knative` on your cluster.
For details on the Knative installation, please visit its [dedicated documentation](./KnativeInstallation.md).

## License

Unless otherwise specified:

MIT (c) 2020 Nima Mahmoudi & Hamzeh Khazaei

## Citation

You can find the paper with details of the proposed model in [PACS lab website](https://pacs.eecs.yorku.ca/publications/). You can use the following bibtex entry:

```bib
coming soon...
```
