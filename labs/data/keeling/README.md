# Fixed data for the Keeling curve notebooks

These classroom copies support the regression and emissions-driven notebooks.
The notebooks retrieve version-pinned copies from this repository and cache them
locally. Source versions and processing details are recorded in the provenance files.

- `mauna_loa_monthly_1958-2025.csv`: monthly CO₂ observations at Mauna Loa, in ppm, from the Scripps CO₂ Program. This is a station record, not a global mean. [Original source](https://scrippsco2.ucsd.edu/data/atmospheric_co2/).
- `historical_budget_1850-2024.csv`: Global Carbon Budget 2025 historical budget, extracted from its Historical Budget sheet. Fluxes are in GtC/year. The classroom input is fossil/industrial plus land-use emissions minus the separately reported cement-carbonation sink. [Data source and citation](https://globalcarbonbudget.org/datahub/the-latest-gcb-data-2025/).
- `carbon_models.py`: numerical support for the classroom one-box and simplified FaIR-style examples. Model references and simplifications are documented in the notebook and helper.

Data providers retain their source terms. Cite the Scripps CO₂ Program for the concentration record and Friedlingstein et al., Global Carbon Budget 2025, for the emissions data. Please retain the provenance files when redistributing these classroom copies.
