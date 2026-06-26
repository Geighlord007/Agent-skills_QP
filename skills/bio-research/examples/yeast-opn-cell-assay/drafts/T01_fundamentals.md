# T1 Fundamentals: Identity, Structure, Native Sources, and Physicochemical Properties of Osteopontin (OPN)

**Project:** Yeast-Expressed Human Osteopontin (OPN) — Recommended Cell Assays  
**Draft purpose:** Collect and organize fundamental data on human/bovine OPN. *Not a final report.*  
**Date compiled:** 2026-06-26

---

## 1. Scope and Search Strategy

- **Objective:** Compile authoritative data on OPN identity, gene/protein structure, native sources, key physicochemical properties, and recombinant (especially yeast) expression precedents relevant to designing cell assays for yeast-expressed human OPN.
- **Sources prioritized:** Peer-reviewed reviews and primary papers (PubMed/PMC), UniProt/NCBI reference entries, EFSA scientific opinions, EU implementing regulations, and patent documents.
- **Confidence legend used throughout:**
  - **High:** Directly from a reference database entry, official agency document, or peer-reviewed primary data.
  - **Medium:** Review/secondary summary that cites primary data, or a single study with acknowledged limitations.
  - **Low:** Supplier/preliminary data, inferred values, or unresolved contradictions.

---

## 2. Identity and Nomenclature

- **Osteopontin (OPN)** is a secreted, acidic, highly phosphorylated glycoprotein encoded by the human **SPP1** gene (HGNC:11255) [1][2][3].
- Established synonyms / historical names [1][3][4][5]:
  - Secreted phosphoprotein 1 (SPP-1)
  - Bone sialoprotein I (BSP I)
  - Early T-lymphocyte activation gene 1 (Eta-1)
  - Uropontin (urinary form)
  - Nephropontin (kidney form)
  - Lactopontin (milk form)
- OPN belongs to the **SIBLING** (Small Integrin-Binding Ligand, N-linked Glycoprotein) family [3][4].
- It was originally identified in the mineralized matrix of bovine bone and the term “osteopontin” (bone-bridge) was coined by Oldberg et al. [4][5]. Human milk OPN was first purified in 1989 [5].

---

## 3. Gene Organization and Primary Structure

### 3.1 Gene locus and architecture

- Human **SPP1** is located on chromosome **4q22.1** and spans approximately **7.7 kb** [2][3][4].
- Literature reports the gene as having **7 exons** [3][4], whereas NCBI Gene currently annotates **8 exons** in the reference assembly (GRCh38.p14) [2]. **This discrepancy is flagged** (see Section 9).
- Mouse *Spp1* is on chromosome 5 (~6 kb coding region, 8 exons) and encodes a 294-aa protein; human and mouse OPN share ~63% peptide identity but conserve key motifs [3].

### 3.2 Protein isoforms and primary sequence

| Attribute | Human OPN | Confidence | Source |
|-----------|-----------|------------|--------|
| Full-length precursor | 314 amino acids (aa) | High | [1] |
| Signal peptide | aa 1–16 | High | [1] |
| Mature secreted chain | aa 17–314 (298 aa) | High | [1][3][4] |
| Canonical isoforms (alternative splicing) | OPN-a (full-length); OPN-b (lacks exon 5 / aa 59–72); OPN-c (lacks exon 4 / aa 31–57); isoform 4 (lacks aa 95–116) | High | [1][3][17] |
| Intracellular vs. secreted isoforms | iOPN arises from alternative translation initiation without signal peptide; sOPN contains the signal sequence | High | [3][4] |
| Bovine mature OPN | 262 aa; deletion of aa 188–209 relative to human; 182 identical residues + 44 conservative substitutions | High | [4][5] |

- The major splice variants **OPN-a, OPN-b, OPN-c** were originally described in human glioma cell lines [17] and retain the signal peptide plus the integrin-binding and calcium-binding domains [3].
- PCR-based analyses of normal human and bovine mammary gland cDNA libraries have **not detected** these splice variants in milk, suggesting that milk OPN is predominantly the full-length transcript [5].

---

## 4. Structural Features and Functional Domains

- Human OPN is an **intrinsically disordered protein**; UniProt annotates a disordered region from aa 41–290 [1][3][4].
- There is **no published high-resolution structure of full-length OPN**; only short peptide/domain structures and AlphaFold/disordered predictions are available [1][3]. This is flagged as a gap (Section 9).

### 4.1 Key motifs (human numbering, full-length precursor)

| Motif / domain | Location (approx.) | Function / binding partner | Confidence | Source |
|----------------|--------------------|----------------------------|------------|--------|
| RGD integrin-binding motif | aa 159–161 | Binds αvβ1, αvβ3, αvβ5, αvβ6, α5β1, α8β1 integrins | High | [3][5] |
| Cryptic SVVYGLR motif | aa 146–152 | Binds α4β1, α4β7, α9β1 integrins after proteolytic exposure | High | [3][5] |
| Heparin-binding domain | Overlaps YGLRSKSKKF (aa ~169–177) | Heparin / cell-surface interactions | High | [3] |
| Calcium-binding domain | Multiple acidic clusters | Hydroxyapatite / mineral binding | High | [3][4] |
| CD44-binding region | C-terminal region | Binds CD44v6/v7 variants (RGD-independent) | High | [3] |
| Thrombin cleavage site | R168–S169 | Exposes SVVYGLR cryptic epitope | High | [3][5] |
| MMP-3 / MMP-7 cleavage site | G166–L167 | Disrupts cryptic epitope, affects integrin binding | High | [3] |
| Plasmin / cathepsin D cleavage sites | Multiple sites around the integrin-binding region | Generate milk N-terminal fragments | High | [5] |

- **Bovine OPN** contains the equivalent integrin-binding motif **SVAYGLK** instead of SVVYGLR [4][5].
- OPN can be **polymerized by transglutaminase 2 (TGM2)**, forming polyOPN with altered integrin-binding properties [3].

### 4.2 Proteolytic processing relevant to assays

- In milk, OPN exists as both **full-length** and **N-terminal fragments** generated by endogenous plasmin and cathepsin D; the corresponding C-terminal fragment is generally not found, presumably because it is further degraded [5].
- N-terminal milk fragments bind αvβ3 and α5β1 integrins more strongly than full-length OPN [5].
- Thrombin cleavage produces an N-terminal fragment containing RGD/SVVYGLR and a C-terminal fragment containing heparin-binding and CD44-binding regions [3][5].

---

## 5. Native Sources and Abundance

### 5.1 Tissue and cellular sources

- OPN is expressed by many cell types, including osteoblasts, osteoclasts, macrophages, dendritic cells, T cells, NK cells, neutrophils, eosinophils, mast cells, epithelial cells (breast, kidney, intestine, skin), endothelial cells, vascular smooth muscle cells, neurons, and microglia [1][3][4][5].
- It is found in tissues and body fluids including **bone, milk, blood/plasma, urine, cerebrospinal fluid, saliva, and bile** [1][3][5].
- **Milk contains the highest natural concentration of OPN** [5].

### 5.2 Milk concentrations

| Source / matrix | Reported OPN concentration | Notes | Confidence | Source |
|-----------------|----------------------------|-------|------------|--------|
| Human milk (mature, mean) | ~138 mg/L (range 18–322 mg/L; ~2.1% of milk protein) | Schack et al. 2009, Denmark | High | [5][8] |
| Human milk (multicenter median) | 99.7–266.2 mg/L depending on country and lactation stage | China, Japan, Korea, Denmark | High | [5] |
| Human colostrum / early milk | ~250–350 mg/L, declining over lactation | Multiple studies; assay-dependent | Medium–High | [5][8] |
| Bovine milk (average) | ~18–23 mg/L | Pooled dairy / Danish Holstein studies | High | [5][7][8] |
| Bovine milk (individual range) | 0.4–67.8 mg/L | Considerable inter-cow variation | High | [5] |
| Bovine milk (MS estimate) | ~50 mg/L | Two samples by MS/MS | Medium | [5] |
| Commercial infant formula (bmOPN) | ~5–15 mg/L historically; currently up to ~40–79 mg/L in some products | EFSA applicant data | High | [7][8] |

- Concentrations in human milk **decline with lactation stage**, and geographic/maternal factors (BMI, smoking, delivery mode, diet) are reported to influence levels, though findings are not fully consistent across studies [5].
- Quantification is complicated by OPN fragmentation, heterogeneous PTMs, complex formation with other milk proteins, and high dilution factors required for ELISA [5].

---

## 6. Post-Translational Modifications (PTMs)

### 6.1 Phosphorylation

- OPN is one of the most heavily phosphorylated proteins in milk.
- **Human milk OPN:** 36 phospho-residues mapped by mass spectrometry — **34 phosphoserines and 2 phosphothreonines** distributed over 34 sites [6].
- **Bovine milk OPN:** on average ~25 phosphates distributed over 28 sites [5].
- Phosphorylation is predominantly catalyzed by the Golgi kinase **FAM20C** (formerly mammary gland casein kinase) on **S-x-E/pS** motifs [1][4][5].
- Phosphorylation status modulates integrin binding, mineralization, macrophage activation, and IL-12 production [3][4][5].
- Dephosphorylation (e.g., via ALPL/TNAP) promotes hydroxyapatite crystallization, whereas phosphorylated OPN inhibits it [1].

### 6.2 Glycosylation

- **O-linked glycosylation:** Human milk OPN has **5 O-glycosylated threonine residues** in the Thr/Pro-rich region near the integrin-binding motifs (UniProt positions Thr-134, Thr-138, Thr-143, Thr-147, Thr-152 in the full-length precursor; numbering differs slightly in older literature) [1][5][6].
- These O-glycans are reported to **protect the RGD/SVVYGLR region from pepsin digestion**, preserving integrin-binding activity after gastric transit [4][5].
- **N-linked glycosylation:** Potential N-glycosylation sequence motifs exist, but N-glycosylation has **not been demonstrated** in milk OPN of any species [5][6].
- **Chondroitin sulfate:** Ser-234 and Ser-308 in human OPN can be modified with chondroitin sulfate in cerebrospinal fluid [1].
- Glycan structures differ between human and bovine milk OPN: human O-glycans contain fucosylated N-acetyllactosamine units, while bovine O-glycans have a disialylated GalNAc-galactose core [5].

### 6.3 Other modifications and processing

- **Transglutaminase 2-mediated cross-linking** forms OPN homo-/hetero-polymers [1][3].
- **Proteolytic cleavage** by thrombin, plasmin, MMP-3/7, cathepsin D, and PHEX generates functionally distinct fragments [3][5].

---

## 7. Key Physicochemical Properties

| Property | Value / observation | Confidence | Source |
|----------|---------------------|------------|--------|
| Calculated MW of full-length precursor | 35,423 Da (UniProt) | High | [1] |
| Calculated MW of mature polypeptide (aa 17–314) | ~33.7 kDa (in silico, average mass) | Medium* | [1], in-silico calculation |
| Apparent MW on SDS-PAGE | 40–80 kDa, depending on PTMs and species | High | [3][4][5] |
| bmOPN full-length (commercial ingredient) | ~33.9 kDa calculated; N-terminal fragment ~19.8 kDa | High | [7] |
| Isoelectric point (unphosphorylated) | ~4.1–4.3 | High | [4][15] |
| Isoelectric point (bovine milk OPN by IEF) | ~3.5 | High | [5] |
| Isoelectric point (recombinant algal/bacterial OPN) | 3.5–4.5 (phosphorylated forms); ~4.5 (non-phosphorylated E. coli) | Medium | [15] |
| Net charge at physiological pH | Strongly negative | High | [1][4] |
| Acidic (D+E) vs. basic (R+K) residues in mature hOPN | D+E = 75; R+K = 28 (ratio ≈ 2.7) | Medium* | [1], in-silico calculation |
| Cysteine content (mature hOPN) | 0 Cys → no disulfide bridges | High | [1] |
| Extinction coefficient (ε₂₈₀, in silico) | ~22,900 M⁻¹ cm⁻¹ | Low* | [1], in-silico calculation |

\* In-silico values are derived from the UniProt P10451 sequence [1]; they do not account for PTMs and should be treated as approximate.

### 7.1 Solubility and stability

- OPN is **heat- and acid-stable** and remains in solution after heating milk to 90 °C and acid precipitation of caseins at pH 4.6 [5].
- Native milk OPN is relatively **resistant to gastric digestion**; glycosylation protects the integrin-binding region, and both human and bovine milk OPN survive incubation with neonatal gastric juice at pH 2–6.5 [5][7].
- The **bulk bmOPN powder** is stable for >150 weeks at 5–20 °C, although a slow decrease in protein/bmOPN content and slight moisture increase were observed [7].
- When added to infant formula, bmOPN shows slow loss at room temperature (≤8.4% at 720 days) and more rapid degradation under accelerated conditions (40 °C / 75% RH; up to ~52% loss at 720 days) [7].

### 7.2 Analytical and purification behavior

- Because OPN is highly acidic, **anion-exchange chromatography** is the default capture method from whey/milk [5][7][15].
- Ceramic hydroxyapatite and immobilized metal affinity resins have been explored for separating phosphorylated OPN from non-phosphorylated contaminants, with variable selectivity [15].

---

## 8. Recombinant and Yeast-Expressed OPN Precedents

### 8.1 Non-yeast recombinant systems

| Host | Reported titer / yield | PTM status | Relevance | Source |
|------|------------------------|------------|-----------|--------|
| HEK293 mammalian cells | 28 mg/L | Mammalian-like glycosylation/phosphorylation possible | Reference for native-like OPN but high cost | [12] |
| *Escherichia coli* | 6–10 mg/L scale | No PTMs; often fragments / inclusion bodies | Limited functional relevance for milk OPN | [12] |
| *Chlamydomonas reinhardtii* (chloroplast) | Low (0.1–0.2% TSP) | Phosphorylated; not O-glycosylated | Functional similarity to bmOPN shown in mouse pups | [12][14][15] |
| *Nicotiana benthamiana* | Not quantified | Plant-type glycosylation | Structurally similar to HEK-produced OPN | [12] |

### 8.2 Yeast / *Pichia* / *Komagataella* expression

- **Zhang et al. 2024** reported the highest published **secreted human OPN titers** in *Komagataella phaffii*:
  - Host strain X33 selected by screening; initial titer 340.5 µg/L.
  - Optimized using the **PAOX1 promoter** and a **hybrid signal peptide (PROSCW10-α)**.
  - Co-expression of transcription factors, translation factors, and molecular chaperones increased extracellular hOPN to 23.6 mg/L.
  - Final engineered strain **XPSA01-CP** achieved **35.6 mg/L in shake-flask** and **128.5 mg/L in a 3-L bioreactor** [11].
- **Chinese patent CN114606148A** describes a *Pichia pastoris* X33 strain carrying an **OPN expression cassette (PAOX1 + α-factor signal peptide + OPN)** integrated at the AOX1 locus. The strain produced **32.2 mg/L OPN**, but secretion was delayed and much of the protein accumulated intracellularly/in vacuoles [13].

### 8.3 PTM implications for yeast-expressed OPN

- *Pichia* / *Komagataella* can perform **N-linked glycosylation**, but the glycans are typically **high-mannose / hypermannosylated** and lack mammalian-type complex sugars, sialic acid, or O-glycosylation unless the host is engineered [16].
- Yeast hosts do **not** carry out mammalian FAM20C-type phosphorylation of secreted proteins; any phosphorylation would need to be engineered or introduced in vitro.
- These PTM differences are expected to affect the apparent MW, pI, charge, receptor binding, immunogenicity, and possibly functional equivalence of yeast-expressed hOPN relative to native human milk OPN [7][8][12][16].
- **Jiang et al. 2021** showed that recombinant bovine and human OPN produced in *C. reinhardtii* retained bioactivities similar to bmOPN in mouse pups despite having fewer phosphorylation sites and no glycosylation, suggesting that some functional assays are robust to PTM differences [14].

---

## 9. Regulatory Context (Select, for Fundamentals)

- EFSA evaluated **bovine milk OPN (bmOPN)** as a novel food and concluded it is safe at a maximum use level of **151 mg/L** in infant and follow-on formula and young-child dairy meals [7].
- The **European Commission authorized bmOPN** as a novel food by **Commission Implementing Regulation (EU) 2023/463** [9].
- In the U.S., the GRAS notice **GRN 716** for bmOPN was withdrawn at the notifier’s request after FDA raised concerns about bioactive ingredient safety in infant formula; this is covered in detail in the regulatory draft (T07) [10].
- No specific regulatory approval for **yeast-expressed human OPN** as a novel food or food ingredient was identified in this search.

---

## 10. Confidence, Contradictions, and Gaps

### 10.1 High-confidence items

- Gene symbol, chromosomal location, UniProt canonical sequence, signal peptide, mature chain length, and major functional motifs [1][3].
- Acidic nature, heavy phosphorylation, O-glycosylation, and intrinsic disorder [1][4][5][6].
- Milk OPN concentrations and the decline over lactation (order-of-magnitude) [5][8].
- Yeast expression titers reported by Zhang et al. 2024 and CN114606148A [11][13].

### 10.2 Contradictions / discrepancies

- **Exon count:** Review sources describe human *SPP1* as 7 exons [3][4], whereas NCBI Gene annotates 8 exons [2]. The difference likely reflects annotation conventions (5′ UTR exon counting) but should be reconciled if used in a regulatory dossier.
- **Amino-acid length:** The canonical full-length precursor is 314 aa [1], but older literature occasionally reports 317 aa or longer isoforms up to 327 aa [2][4]. Mature milk OPN is consistently 298 aa [4][5].
- **pI and MW:** Reported values span 3.5–4.5 for pI and 33–80 kDa for apparent MW because of phosphorylation, glycosylation, fragmentation, and measurement method [4][5][7][15].
- **Maternal/geographic factors:** Some studies correlate milk OPN with BMI/age positively, others negatively; delivery-mode effects are also inconsistent [5].

### 10.3 Gaps relevant to yeast-expressed hOPN cell assays

- **No high-resolution structure** of full-length OPN; cell-assay design relies on short motifs and disordered-domain predictions.
- **PTM profile of yeast-expressed hOPN** is not comprehensively mapped in the public literature. It is unclear whether the Zhang 2024 material was phosphorylated, hypermannosylated, or truncated.
- **Direct side-by-side cell-assay comparison** of yeast-expressed hOPN vs. mammalian (HEK/CHO) hOPN or native human milk OPN is lacking.
- **FSANZ / other jurisdictions:** No specific approval or safety opinion for recombinant/yeast-expressed OPN was located; only the EU bmOPN precedent and the withdrawn U.S. GRN 716 are documented.
- **Standardization:** There is no widely accepted reference standard or potency assay for recombinant OPN; ELISAs, Western blots, MS peptide quantification, and integrin-binding assays each have limitations [5].

---

## 11. Sources

[1] **Database** — UniProt. “Osteopontin (P10451).” *UniProtKB/Swiss-Prot*. https://www.uniprot.org/uniprotkb/P10451

[2] **Database** — NCBI Gene. “Secreted phosphoprotein 1 (SPP1), GeneID 6696.” https://www.ncbi.nlm.nih.gov/gene/6696

[3] **Review** — Lin EY-H, Xi W, Aggarwal N, Shinohara ML. “OPN in innate immune cells and CNS-resident cells.” *International Journal of Molecular Sciences*. 2022;23(7):3629. https://pmc.ncbi.nlm.nih.gov/articles/PMC10071791/

[4] **Review** — Karasalih U, et al. “Osteopontin: structure, functions, and nutritional potential.” *International Journal of Molecular Sciences*. 2025;26(12):5868. https://pmc.ncbi.nlm.nih.gov/articles/PMC12192592/

[5] **Review** — Sørensen ES, Christensen B. “Osteopontin in milk: structure, function, and health effects.” *International Dairy Journal*. 2023;140:105647. https://pmc.ncbi.nlm.nih.gov/articles/PMC10255459/

[6] **Paper** — Christensen B, Nielsen MS, Haselmann KF, Petersen TE, Sørensen ES. “Post-translationally modified residues of native human osteopontin are located in clusters: identification of 36 phosphorylation and five O-glycosylation sites and their biological implications.” *Biochemical Journal*. 2005;390:285–292. PMID 15869464. https://pubmed.ncbi.nlm.nih.gov/15869464/

[7] **Official** — EFSA NDA Panel. “Safety of bovine milk osteopontin as a novel food pursuant to Regulation (EU) 2015/2283.” *EFSA Journal*. 2022;20(5):7137. https://pmc.ncbi.nlm.nih.gov/articles/PMC9074041/

[8] **Paper / Review** — Fleming SA, Rauch SM, Donovan SM, et al. “An expert panel on the adequacy of safety data and physiological roles of dietary bovine osteopontin in infancy.” *Frontiers in Nutrition*. 2024;11:1404303. https://pmc.ncbi.nlm.nih.gov/articles/PMC11197938/

[9] **Official** — European Commission. “Commission Implementing Regulation (EU) 2023/463 of 3 March 2023 authorising the placing on the market of bovine milk osteopontin as a novel food.” *Official Journal of the European Union*. https://www.wb6cif.eu/wp-content/uploads/2023/03/CELEX_32023R0463_EN_TXT.pdf

[10] **Official** — U.S. FDA. “GRN No. 716 — Bovine milk osteopontin.” GRAS Notice Inventory. https://www.cfsanappsexternal.fda.gov/scripts/fdcc/index.cfm?set=GRASNotices&id=716

[11] **Paper** — Zhang Z, Li Y, Liu Z, Cui S, Xu X, Liu Y, Li J, Du G, Lv X, Liu L. “Efficient secretory expression of human milk osteopontin in *Komagataella phaffii*.” *Future Foods*. 2024;10:100393. https://doi.org/10.1016/j.fufo.2024.100393

[12] **Review** — Wang Z, Wu Y, Lv X, Li J, Liu L, Du G, Chen J, Liu Y. “Advances in the biosynthesis of milk proteins fueled by synthetic biology.” *Agricultural Products Processing and Storage*. 2026;2(1):33. https://link.springer.com/article/10.1007/s44462-026-00065-5

[13] **Patent** — Chinese Patent Application CN114606148A. “Pichia pastoris strain for expressing osteopontin.” 10 Jun 2022. https://eureka.patsnap.com/patent-CN114606148A

[14] **Paper** — Jiang R, Tran M, Lönnerdal B. “Recombinant bovine and human osteopontin generated by *Chlamydomonas reinhardtii* exhibit bioactivities similar to bovine milk osteopontin when assessed in mouse pups fed osteopontin-deficient milk.” *Molecular Nutrition & Food Research*. 2021;65(4):e2000644. https://doi.org/10.1002/mnfr.202000644

[15] **Paper** — Ravi A, Guo S, Rasala B, Tran M, Mayfield S, Nikolov ZL. “Separation options for phosphorylated osteopontin from transgenic microalgae *Chlamydomonas reinhardtii*.” *International Journal of Molecular Sciences*. 2018;19(2):585. https://pmc.ncbi.nlm.nih.gov/articles/PMC5855807/

[16] **Paper** — Teh AY-H, Marquet A, Sinclair A, Timms P, Kemp R, Elefanty A, Stanley EG. “Recombinant human erythropoietin production in *Pichia pastoris* and glycosylation analysis.” *Plant Biotechnology Journal*. 2011;9(9):999–1010. https://pmc.ncbi.nlm.nih.gov/articles/PMC3168189/

[17] **Paper** — Saitoh Y, Kuratsu J, Takeshima H, Yamamoto S, Ushio Y. “Expression of osteopontin in human glioma. Its correlation with the malignancy.” *Laboratory Investigation*. 1995;72:55–63. PMID 7837791. https://pubmed.ncbi.nlm.nih.gov/7837791/

---

**End of draft.**
