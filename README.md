# TDDP Parameters Report

This repository contains a script `main.py` that produces an aggregation of the parameters (also known as observable properties) `parameters.csv` file from TERN's metadata records in the TERN Data Discovery Portal (TDDP).

## Running the script

Make a copy of `.env-template` and name it `.env`. Populate it with values to run `main.py` correctly.

### Environment variables

| Environment variable          | Description                                                                     |
|-------------------------------|---------------------------------------------------------------------------------|
| `TDDP_ELASTICSEARCH_URL`      | The Elasticsearch URL at the `/_search` endpoint. Include the index/alias name. |
| `TDDP_ELASTICSEARCH_USERNAME` | The basic authentication username used at the Elasticsearch URL.                |
| `TDDP_ELASTICSEARCH_PASSWORD` | The basic authentication password used at the Elasticsearch URL.                |

With the Python packages defined in `requirements.txt` installed, run the script:

```
python main.py
```

## Example output

The `doc_count` column refers to the number of metadata records in TDDP that have the parameter tagged.

| id                                                                                                        | doc_count | label               | definition                                                                                                                                                                                                                                                                                                                               |
|-----------------------------------------------------------------------------------------------------------|-----------|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|   http://linked.data.gov.au/def/tern-cv/dc6dded77ce5b935c4f5a3ec6b5912d25cfbc5a23f18acf9507b2c8f7816469a  |   102     |   soil temperature  |   Soil temperature is the bulk temperature of the soil, not the surface (skin) temperature. "Soil" means the near-surface layer where plants sink their roots. For subsurface temperatures that extend beneath the soil layer or in areas where there is no surface soil layer, the standard name temperature_in_ground should be used.  |
|   http://linked.data.gov.au/def/tern-cv/01d61e19be44d561a606475b102a3dd8b8aec647aa9fc61dd85be8c6b1926d1d  |   102     |   wind speed        |   Speed is the magnitude of velocity. Wind is defined as a two-dimensional (horizontal) air velocity vector, with no vertical component. (Vertical motion in the atmosphere has the standard name upward_air_velocity.) The wind speed is the magnitude of the wind velocity.                                                            |
