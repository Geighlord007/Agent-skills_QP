# Authoritative Databases and Search Targets

Prioritize these sources in descending order.

## Scientific literature

| Database | URL pattern | Best for |
|----------|-------------|----------|
| PubMed | `https://pubmed.ncbi.nlm.nih.gov/{PMID}/` | Biomedical papers |
| Europe PMC | `https://europepmc.org/article/MED/{PMID}` | Open-access full texts |
| Semantic Scholar | search | Citation context, related papers |
| Google Scholar | search | Broad discovery |
| bioRxiv / medRxiv | preprints | Very recent findings |

## Patents

| Database | URL pattern | Best for |
|----------|-------------|----------|
| Google Patents | `https://patents.google.com/patent/{number}` | Fast lookup |
| Espacenet (EPO) | `https://worldwide.espacenet.com/` | Global patent search |
| USPTO Patent Center | `https://patentcenter.uspto.gov/` | US patents and applications |
| Lens.org | `https://www.lens.org/` | Patent analytics |

## Regulatory / official

| Agency | Database | Best for |
|--------|----------|----------|
| US FDA | GRAS Notices, FCN, IND database | Food ingredient safety |
| EFSA | OpenFoodTox, EFSA Journal | EU novel food, safety opinions |
| FSANZ | Approved substances | Australia/NZ novel food |
| NMPA (China) | 化妆品原料目录, 食品相关产品 | China cosmetics/food |
| EU CosIng | `https://ec.europa.eu/growth/tools-databases/cosing/` | EU cosmetics ingredients |
| ClinicalTrials.gov | `https://clinicaltrials.gov/` | Human trials |

## Industry / commercial

| Source | Best for |
|--------|----------|
| Company websites / investor relations | Product claims, pipeline |
| SEC EDGAR | US public company filings |
| Crunchbase / PitchBook | Funding, partnerships |
| Press releases (PRNewswire, GlobeNewswire) | announcements |

## Search strategy

1. Start with PubMed and the relevant regulatory database.
2. Use patent search to identify IP constraints.
3. Use company sources last and mark them as `company` confidence.
4. Cross-check surprising claims against a second independent source.
