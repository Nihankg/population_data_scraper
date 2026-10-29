# Türkiye neighborhood and village population scraper

A Python notebook for turning district population tables on [Nüfusune](https://www.nufusune.com/) into an Excel dataset of neighborhood/village population records.

I developed this workflow to assemble small-area demographic inputs for research and link them to province, district and neighborhood identifiers. The data is collected from a third-party website, not directly from an official population-statistics API.

## What the notebook does

1. Reads an external list of provinces, districts and neighborhoods.
2. Normalizes Turkish characters and administrative names to construct district-page URLs.
3. Requests each selected district's population page and parses its HTML tables using Beautiful Soup.
4. Extracts neighborhood records and a village table where present.
5. Combines records, adds province/district identifiers, standardizes locality names and exports an Excel workbook.

The notebook demonstrates HTTP data collection, HTML parsing, administrative-name normalization, nested iteration over geographic units, table concatenation and Excel export.

## Repository file

- `nufus_scrape.ipynb`: input preparation, scraping, cleaning and export.

## Required input

The notebook expects a local workbook named `ilce_collapse.xlsx`, with columns:

| Column | Meaning |
| --- | --- |
| `Province` | Province name |
| `District` | District name |
| `Neighborhood` | Neighborhood/locality name |

This workbook is **not included**. Supply your own list and update the hard-coded input path. The scope of the extraction is determined by the unique province/district pairs in that list; the notebook does not automatically enumerate all of Türkiye.

The code contains specific central-district name corrections for Adıyaman, Kilis and Osmaniye. Review those mappings for your chosen input.

## Setup and execution

```bash
python -m pip install jupyterlab "pandas>=2.1" requests beautifulsoup4 openpyxl geopandas
jupyter lab
```

The `pandas>=2.1` requirement supports the notebook's `DataFrame.map` calls. GeoPandas is imported by the notebook, although the shown extraction workflow uses pandas tables.

Open `nufus_scrape.ipynb`, update the input/output paths, create the output directory, and run the cells in order. Begin with one district and inspect its source page and parsed output before a larger run.

## Output

The final workbook, `mahalle_nufus.xlsx`, contains:

```text
Neighborhood | District | Province | Total Population
```

The intermediate extraction also reads male/female population columns, but the final selected output drops them. Village names are moved into the shared `Neighborhood` field. The final table does not retain a locality-type field or a year column. Population strings are exported without an explicit numeric conversion, so inspect separators and types before quantitative analysis.

## Scope and limitations

This is an exploratory research notebook. The code was inspected for this documentation update; a fresh live extraction was not run.

- Page layouts, table identifiers and URL spellings can change. A successful HTTP response alone does not verify that the intended table was parsed.
- The code depends on `ust_tablo` table containers and assumes particular column layouts. Missing containers or differently shaped village tables may require adjustments.
- For district pages without a village table, the later `Village`-column cleaning step may need a guard if no village column was created anywhere in the extraction.
- The URL does not select a historical year. Record the population reference year shown by the site and your collection date separately; the output is not automatically a longitudinal panel.
- Non-200 responses are skipped. Keep a record of skipped districts and check extraction completeness.
- Turkish-to-ASCII normalization and locality-name replacements can create ambiguous identifiers. Check joins and duplicates before merging with other datasets.

Use modest request rates and respect the source site's access conditions. Credit Nüfusune as the extraction source and independently verify population definitions/reference years for your application.
