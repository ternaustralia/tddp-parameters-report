import os

import requests
from jinja2 import Template

try:
    from dotenv import load_dotenv

    load_dotenv()
except ModuleNotFoundError:
    pass


ELASTICSEARCH_URL = os.environ["TDDP_ELASTICSEARCH_URL"]
ELASTICSEARCH_USERNAME = os.environ["TDDP_ELASTICSEARCH_USERNAME"]
ELASTICSEARCH_PASSWORD = os.environ["TDDP_ELASTICSEARCH_PASSWORD"]

query = {
    "size": 0,
    "aggs": {
        "type": {
            "filter": {"term": {"subject.type": "data-group"}},
            "aggs": {
                "parameters": {
                    "terms": {
                        "field": "subject.vocab_uri",
                        "size": 50000,
                        "min_doc_count": 1,
                        # Include only HTTP URLs. The data contains some values that are UUIDs.
                        "include": "https?://.*",
                        # Exclude certain URLs based on the following regex patterns.
                        # Effectively, the remaining values have the following base URL http://linked.data.gov.au/def/tern-cv/ 
                        # but we didn't know that when we were initially performing the filtering using exclude.
                        # Regex patterns:
                        # - https://gcmd.* - The GCMD URIs are not parameters
                        # - http://qudt.org/vocab/unit/.* - These are units of measure
                        # - https://(id.)?biodiversity.org.au/.* - Taxon related, not parameters
                        # - https://linked.data.gov.au/def/anzsrc.* - These are ANZSRC keywords
                        # - http://purl.org/au-research/vocabulary/anzsrc-for/.* - These are ANZSRC keywords
                        # - https://w3id.org/tern/resources/.* - These are usually people, organisations, platforms, etc.
                        # - http://linked.data.gov.au/dataset/.* - Sites from datasets such as AusPlots.
                        # - http://linkeddata.tern.org.au/xxx - Looks like placeholder values have snuck into prod.
                        # - https://w3id.org/tern/ontologies/.* - TERN Ontology stuff.
                        # - http://linkeddata.tern.org.au/def/.* - These are not correct. Controlled vocabularies should not be using this base URL.
                        "exclude": "(https://gcmd.*|http://qudt.org/vocab/unit/.*|https://(id.)?biodiversity.org.au/.*|https://linked.data.gov.au/def/anzsrc.*|http://purl.org/au-research/vocabulary/anzsrc-for/.*|https://w3id.org/tern/resources/.*|http://linked.data.gov.au/dataset/.*|http://linkeddata.tern.org.au/xxx|https://w3id.org/tern/ontologies/.*|http://linkeddata.tern.org.au/def/.*)",
                    }
                }
            },
        }
    },
}


if __name__ == "__main__":
    response = requests.post(
        url=ELASTICSEARCH_URL,
        json=query,
        auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    parameter_items = [
        (item["key"], item["doc_count"])
        for item in data["aggregations"]["type"]["parameters"]["buckets"]
    ]

    sparql_query_template = Template(
        """\
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

    SELECT ?id ?doc_count ?label ?definition
    WHERE {
        VALUES (?id ?doc_count) {
            {% for uri, doc_count in parameter_items %}
            {% if uri %}
            (<{{ uri }}> {{ doc_count }})
            {% endif %}
            {% endfor %}
        }

        ?id skos:prefLabel ?label ;
            skos:definition ?definition .
    }
    ORDER BY DESC(?doc_count)
    """
    )

    sparql_query = sparql_query_template.render(parameter_items=parameter_items)

    response = requests.post(
        url="https://graphdb.tern.org.au/repositories/tern_vocabs_core",
        data=sparql_query,
        headers={
            "content-type": "application/sparql-query",
            "accept": "text/csv",
        },
        timeout=60,
    )

    if response.status_code != 200:
        raise requests.exceptions.HTTPError(
            f"Response status code: {response.status_code}. {response.text}"
        )

    with open("parameters.csv", "w", encoding="utf-8") as file:
        file.write(response.text)
