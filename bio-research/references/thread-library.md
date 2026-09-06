# Thread Library

Select threads per project. Not every project needs every thread. The same thread may be instantiated multiple times with different foci.

## Generic threads

| ID | Thread | Typical questions | Useful for |
|----|--------|-------------------|------------|
| T1 | Fundamentals | Identity, structure, native source, key properties, nomenclature | All topics |
| T2 | Mechanism | Biochemical pathway, molecular target, structure-function, known modifications | Proteins, enzymes, actives |
| T3 | Production | Expression host, fermentation/culture conditions, yield, downstream purification, PTM | Recombinant proteins, strains |
| T4 | Engineering | Sequence/strain/process engineering options, design principles, trade-offs | Protein engineering, synthetic biology |
| T5 | Safety & Toxicology | In vitro/in vivo safety data, allergenicity, genotoxicity, NOAEL, ADI | Ingredients, food proteins |
| T6 | Clinical Evidence | Human/animal studies, endpoints, sample size, effect size, limitations | Bioactives, therapeutics |
| T7 | Regulatory Status | GRAS, Novel Food, FDA, EFSA, FSANZ, NMPA, COSMOS/INCI requirements | Food, cosmetics, novel ingredients |
| T8 | Patent & FTO | Key patents, assignees, claims, freedom-to-operate risks, expiry | Any commercial topic |
| T9 | Competitive Landscape | Companies, products, positioning, partnerships, funding | Market-facing topics |
| T10 | Market & Applications | Addressable markets, use cases, pricing, adoption barriers | Commercial assessment |
| T11 | Cell / Assay Models | Recommended assays, readouts, cell lines, protocols, benchmarks | Functional validation |
| T12 | Strain / Host Constraints | Codon usage, glycosylation, secretion, proteolysis, transformation | Filamentous fungi, yeast, bacteria |

## Thread bundles by project type

### Protein engineering / recombinant protein

Suggested threads: T1, T2, T3, T4, T5, T8, T12
Optional: T6, T9, T10

### Cell-assay recommendation

Suggested threads: T1, T2, T5, T6, T7, T11
Optional: T3, T8, T9

### Strain / fermentation optimization

Suggested threads: T1, T3, T4, T5, T12, T9
Optional: T2, T7, T10

### Regulatory pathway / novel food / GRAS

Suggested threads: T1, T5, T7, T8, T9
Optional: T3, T6, T10

### Competitive intelligence

Suggested threads: T1, T8, T9, T10, T4
Optional: T5, T7

## Thread prompt template

Use this template when spawning a thread subagent:

```
You are a life-sciences research assistant working on Project: {project}.

Thread: {thread_id} {thread_name}
Mode: {quick|standard|deep}

Investigate:
{questions}

Rules:
1. Search authoritative sources first (PubMed, official agencies, patents, company SEC filings if relevant).
2. For every fact you record, append a source entry to datas/sources.jsonl using the exact schema in references/source-persistence.md.
3. In drafts/T{NN}_{thread_name}.md, write structured findings only — no prose report.
4. Annotate every claim with [N] matching the source ID in sources.jsonl.
5. Assign confidence: High (peer-reviewed or official), Medium (industry/press with traceable source), Low (unverified or single source).
6. Explicitly flag contradictions and gaps.
7. Do not invent PMIDs, patent numbers, or URLs.
```
