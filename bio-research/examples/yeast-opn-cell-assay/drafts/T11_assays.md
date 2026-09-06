# T11_assays: Recommended Cell-Based Assays for Yeast-Expressed Human Osteopontin (OPN)

**Status:** Data-collection draft. Not a polished final report.  
**Scope:** Identify, prioritize, and annotate cell-based assays for characterizing the bioactivity of recombinant human OPN produced in yeast. Literature is weighted toward bovine-milk OPN (bmOPN), native human OPN, or recombinant OPN from bacterial/mammalian systems; direct data for yeast-expressed human OPN are scarce and must be flagged as a gap.

---

## 1. Assay Overview & Prioritization

| Assay area | Priority | Primary cell model(s) | Key readouts | Rationale | Confidence |
|------------|----------|----------------------|--------------|-----------|------------|
| Caco-2/HT-29 intestinal barrier | **High** | Caco-2 monoculture; Caco-2/HT29-MTX co-culture on Transwells [1][3][5] | TEER; FITC-dextran / mannitol Papp; occludin, ZO-1, claudins by IF/WB/qPCR; basolateral IL-8, IL-6, TNF-α, IL-10 [1][3][4] | First site of contact for orally delivered OPN; strongest published in vitro evidence linking OPN to tight-junction maintenance and anti-inflammatory tone [1][3][4] | High for bmOPN/native OPN; Medium for yeast-expressed OPN |
| PBMC cytokine profiling | **High** | Human PBMCs, ± TLR/pathogen stimulus [10][11] | Multiplex / ELISA for IL-12, TNF-α, IFN-γ, IL-6, IL-1β, IL-8, CCL2, IL-10, IL-2 [10][11][22] | Direct readout of immune modulation; bridges to infant-formula clinical cytokine data [22] | High |
| moDC maturation | **High** | CD14+ monocyte-derived DCs (moDCs) [6][7] | Flow: CD14, CD83, CD86, HLA-DR, CD80; cytokines IL-12p70, TNF-α, IL-10, IL-4; Annexin V apoptosis [6][7] | Mechanistic link between OPN, DC maturation, and Th1-skewed responses [6][7] | High for endogenous/exogenous OPN; Medium for dose response of yeast-expressed OPN |
| Hydroxyapatite (HA) inhibition | **Medium** | Cell-free biochemical assay (constant-composition autotitration or agarose gel) [12][13] | Nucleation lag time; crystal growth rate; comparison with dephosphorylated OPN / poly-Asp control [12][13][14] | Established, quantifiable biochemical function; directly sensitive to phosphorylation state, which is a critical quality attribute for yeast OPN [12][13][14] | High for native phosphorylated OPN; Medium/Low for yeast OPN unless phosphorylated |
| Macrophage polarization | **Medium** | THP-1-derived macrophages or CD14+ monocyte-derived macrophages; M0 baseline + LPS/IFN-γ (M1) or IL-4/IL-13 (M2) [8][9] | Flow markers CD86/CD80 (M1), CD163/CD206/CD204 (M2); cytokines TNF-α, IL-6, IL-1β, IL-10; phagocytosis; Transwell migration [8][9] | OPN is implicated in macrophage recruitment and M2-like biology, but direct polarization effects are context-dependent [8][9] | Medium |
| Osteoblast differentiation | **Medium** | MC3T3-E1 or human MSCs in osteogenic medium [15][16][17] | ALP activity; alizarin red mineralization; qPCR/WB for Runx2, Sp7, ALP, Col1a1, OCN, OPN [15][16][17] | OPN is an osteogenic marker and regulator, though exogenous effects vary with concentration and cell context [15][16] | Medium |

---

## 2. Background Context for Yeast-Expressed OPN

- Recombinant human OPN has been produced in *Pichia pastoris* using a pPICZαA-α-factor-OPN cassette under the AOX1 promoter; a reported shake-flask/expression yield reached ~32.2 mg/L, with partial secretion and substantial intracellular accumulation in vacuoles [23].
- OPN bioactivity depends heavily on post-translational modifications, especially phosphorylation and glycosylation [14][21]. Native bone/milk OPN is highly phosphorylated; yeast may under-phosphorylate unless engineered, and *Pichia* N-glycosylation tends to be hypermannosylated compared with mammalian cells [23][14].
- Regulatory precedents for OPN as a food ingredient are dominated by bmOPN (Lacprodan® OPN-10):
  - EFSA issued a positive 2022 opinion for bovine milk OPN as a novel food at up to 151 mg/L in infant and follow-on formula and in milk-based drinks/cereals for young children up to 35 months [18].
  - FDA GRAS Notice GRN 716 for the same bmOPN ingredient was **withdrawn at the notifier's request** in February 2018 after FDA questions, including the intended use in infant formula [24].
  - A 13-week rat dietary study with Lacprodan® OPN-10 identified a NOAEL of 2% in the diet (~1,208–1,272 mg/kg bw/day); the material was not genotoxic and developmental parameters were unaffected [19].
  - An independent expert panel noted that safety data are adequate for the proposed use but flagged mechanistic gaps, including limited ADME data, blood-brain-barrier transport, and direct demonstration that bmOPN functions equivalently to human milk OPN [20].

**Gap / translation note:** The evidence base below is therefore mostly indirect for yeast-expressed human OPN. Each assay recommendation should be accompanied by side-by-side benchmarking against a well-characterized reference (e.g., bmOPN, commercial rhOPN, or native human milk OPN) and by analytical characterization of phosphorylation/glycosylation.

---

## 3. Assay-by-Assay Data Notes

### 3.1 Caco-2 / HT-29 Intestinal Barrier

**Key findings**
- Endogenous OPN supports intestinal epithelial barrier integrity. In Caco-2 monolayers, OPN knockdown reduced transepithelial electrical resistance (TEER) and disrupted junctional occludin localization; OPN-null mice showed worse DSS-colitis barrier breakdown [1].
- Bovine milk OPN binds to the Caco-2 cell surface but is not substantially internalized; N-terminal fragments can be transported across Caco-2 and Caco-2/HT29-MTX co-cultures in an energy- and temperature-dependent manner that is inhibited by wortmannin [3]. One related report described little to no internalization of intact bmOPN by Caco-2 cells [2].
- A co-culture model combining OPN and 2'-FL fermentation metabolites increased TEER and up-regulated tight-junction proteins (occludin, claudin-1/2, ZO-1/2), lowered IL-1β, IL-6, and TNF-α, and raised IL-10 via MyD88/IκB-α/NF-κB signaling [4].
- Caco-2/HT-29 co-cultures are standard for testing whey-derived peptides and inflammation-induced permeability; TEER threshold of ~250–300 Ω·cm² is typically used to confirm monolayer integrity [5].

**Recommended protocol outline**
- **Models:** Caco-2 monoculture (21-day differentiation) or Caco-2:HT29-MTX co-culture (e.g., 9:1 or 75:25) on 12-mm Transwell inserts [3][5].
- **Challenge:** Basal condition or cytokine cocktail (TNF-α/IL-1β/IFN-γ) / LPS to model inflammation [4][5].
- **Treatment arms:** vehicle, positive control (L-glutamine or known barrier peptide), yeast-expressed rhOPN at 25–200 µg/mL (range based on Caco-2 binding/transport studies [3]; infant-formula-relevant range ~65–151 mg/L [18]).
- **Readouts:**
  - TEER at baseline and post-treatment [1][5].
  - Paracellular permeability: FITC-dextran (4 kDa or 70 kDa) or [³H]-mannitol Papp [3][5].
  - Tight-junction markers: occludin, ZO-1, claudin-1/3/4 by immunofluorescence and Western blot; qPCR for OCLN, TJP1, CLDN1/3/4 [1][4].
  - Cytokines in basolateral medium: IL-8, IL-6, TNF-α, IL-10 by ELISA or multiplex [4][5].

**Confidence:** High that OPN protects intestinal barrier integrity in these models; Medium for predicting the potency of yeast-expressed OPN because transport/binding may depend on phosphorylation and glycosylation states [3][14].

**Contradiction / gap:** One study reported surface binding without internalization [2], whereas another observed N-terminal fragment transcytosis [3]. The difference may reflect fragment size, exposure time, or detection sensitivity. The fate of full-length yeast-expressed OPN across the intestinal epithelium is not established.

---

### 3.2 Monocyte-Derived Dendritic Cell (moDC) Maturation

**Key findings**
- Human monocyte-derived DCs synthesize OPN during differentiation. Neutralizing anti-OPN reduces expression of CD86 and HLA-DR, impairs maturation, and increases apoptosis, indicating OPN is an endogenous survival/maturation factor [6].
- In hepatitis B virus (HBV) antigen-stimulated PBMCs, OPN neutralization reduced CD80/CD86/HLA-DR on BDCA-1+ DCs, lowered IL-12, TNF-α, and IFN-γ, and increased IL-4; conversely, an OPN-derived peptide enhanced CD80/CD86 and IFN-γ-producing T cells [7].

**Recommended protocol outline**
- **Model:** CD14+ monocytes isolated from human PBMCs, differentiated 5–6 days with GM-CSF (e.g., 800 U/mL) + IL-4 (e.g., 500 U/mL) [6][7].
- **Treatment arms:** vehicle, rhOPN added during differentiation and/or during LPS/maturation trigger (e.g., 0.1–10 µg/mL), anti-OPN neutralizing antibody as mechanistic control [6][7].
- **Readouts:**
  - Flow cytometry: CD14, CD11c, CD83, CD86, HLA-DR, CD80 [6][7].
  - Cytokines: IL-12p70, TNF-α, IL-10, IL-4 by ELISA/multiplex [7].
  - Apoptosis: Annexin V/PI [6].
  - Optional: allogeneic T-cell proliferation or IFN-γ/IL-4 staining to confirm functional Th1 skewing [7].

**Confidence:** High that OPN supports moDC maturation and survival; Medium for quantitative translation to yeast-expressed OPN because receptor engagement depends on phosphorylation and proteolytic fragments [7][14].

---

### 3.3 Macrophage Polarization

**Key findings**
- OPN expression is highest in M2-like macrophages. OPN knockdown in macrophages reduces M2-associated genes (e.g., PPARγ, TGF-β1) and enhances phagocytic activity [9].
- In human monocyte-derived macrophages (MDMs) and murine bone-marrow-derived macrophages, presence of OPN during polarization did not produce a clear M1/M2 skewing pattern and dampened LPS-induced pro-inflammatory cytokine production while increasing phagocytosis [8].
- OPN acts as a chemoattractant for M0 and M2 macrophages through integrin αvβ5; it does not itself skew macrophage polarization in M0 precursors [9].

**Recommended protocol outline**
- **Model:** THP-1 monocytes differentiated with PMA (e.g., 100 nM, 24–48 h) or CD14+ monocyte-derived macrophages; polarize with LPS + IFN-γ (M1) or IL-4 + IL-13 (M2) [8][9].
- **Treatment arms:** vehicle, rhOPN at 0.1–10 µg/mL added at polarization and/or to mature M1/M2 cultures; neutralizing antibody or RGD-blocking peptide as control [8][9].
- **Readouts:**
  - Surface markers by flow: CD86, CD80 (M1); CD163, CD206, CD204 (M2) [8][9].
  - Cytokines: TNF-α, IL-6, IL-1β, IL-10 [8].
  - Functional assays: phagocytosis (pHrodo E. coli or FITC-dextran particles); migration across Transwell toward OPN gradient [8][9].

**Confidence:** Medium. OPN's primary macrophage role appears to be chemotaxis and M2-signature maintenance rather than a simple M1-polarizing stimulus [8][9]. The effect of yeast-expressed OPN glycoforms on these phenotypes is unknown.

---

### 3.4 PBMC Cytokine Profiling

**Key findings**
- Native OPN induces IL-12 production by non-infected PBMCs in a dose-dependent manner, with optimal activity around 50 µg/mL [10].
- Recombinant OPN (1 µg/mL) preferentially induces pro-inflammatory chemokines and cytokines (IL-1, IL-8, CCL2/MCP-1, CXCL1) and activates NF-κB in PBMCs from rheumatoid arthritis patients [11].
- In a randomized infant-formula trial, bovine OPN supplementation (65 or 130 mg/L) lowered plasma TNF-α and moved cytokine profiles closer to breast-fed infants; the highest dose was associated with fewer febrile episodes [22].

**Recommended protocol outline**
- **Model:** Human PBMCs isolated by density-gradient centrifugation, plated at ~2 × 10⁶ cells/mL [10][11].
- **Treatment arms:** vehicle, rhOPN alone (0.1–100 µg/mL), rhOPN + LPS (e.g., 10 ng/mL) or antigen, and anti-OPN or isotype control [10][11].
- **Readouts:**
  - Multiplex / ELISA at 24 h and 48 h: IL-12, TNF-α, IFN-γ, IL-6, IL-1β, IL-8, CCL2, CXCL1, IL-10, IL-2 [10][11][22].
  - Intracellular cytokine staining / ELISpot for Th1 (IFN-γ) and Th2 (IL-4, IL-13) responses [7][10].
  - Optional NF-κB reporter assay or phospho-p65 Western blot [11].

**Confidence:** High that OPN modulates PBMC cytokine output. Directionality (pro- vs. anti-inflammatory) is context- and dose-dependent, so the assay should test both resting and stimulated conditions [10][11][22].

**Contradiction:** Exogenous OPN can activate NF-κB and pro-inflammatory chemokines in RA PBMCs [11], whereas dietary bmOPN in infants is associated with lower TNF-α and fewer fevers [22]. The difference likely reflects concentration, exposure route, disease state, and interaction with other milk matrix components.

---

### 3.5 Hydroxyapatite (HA) Inhibition

**Key findings**
- Native OPN is a potent inhibitor of de novo HA formation, with an IC₅₀ of ~0.06 µg/mL in a constant-composition autotitration assay. Activity requires both phosphate and carboxylate groups; enzymatic dephosphorylation reduces inhibitory activity >40-fold [12].
- Short phosphopeptides corresponding to OPN residues 41–52 and 290–301 are the most potent HA-nucleation inhibitors; phosphorylation is essential and negative charge density correlates with potency [13].
- Phosphorylation is broadly required for OPN regulation of biomineralization [14].

**Recommended protocol outline**
- **Model:** Cell-free biochemical assay (constant-composition pH-stat titration or agarose gel diffusion) [12][13].
- **Treatment arms:** yeast-expressed rhOPN; dephosphorylated rhOPN as negative control; commercial phosphorylated OPN or poly-L-aspartate as positive control; vehicle [12][13][14].
- **Readouts:**
  - Nucleation lag time and rate of HA crystal growth [12].
  - Dose-response IC₅₀ for rhOPN versus reference [12].
  - Phosphorylation stoichiometry by mass spectrometry or phosphate assay to correlate activity with PTM status [14].

**Confidence:** High for native phosphorylated OPN. For yeast-expressed OPN, confidence is **Low to Medium** unless the protein is shown to be phosphorylated at the relevant sites; unphosphorylated recombinant OPN is much less active [13][14].

---

### 3.6 Osteoblast Differentiation

**Key findings**
- OPN is a late marker of osteogenic differentiation; its expression increases during MC3T3-E1 osteoblast differentiation and is accompanied by Runx2, Sp7, ALP, and OCN [17].
- OPN-null murine mesenchymal stem cells show impaired osteogenic differentiation and enhanced adipogenesis; addition of exogenous OPN (purified or recombinant) restores osteogenesis through integrin αvβ1 [16].
- Exogenous OPN (100 ng/mL) can suppress osteoblast responses to mechanical strain and growth factors by inhibiting focal adhesion kinase (FAK) phosphorylation via low-molecular-weight protein tyrosine phosphatase (LMW-PTP) and CD44 [15].

**Recommended protocol outline**
- **Model:** MC3T3-E1 pre-osteoblasts or human bone-marrow/ adipose-derived MSCs in osteogenic medium (ascorbic acid, β-glycerophosphate, dexamethasone) [15][16][17].
- **Treatment arms:** vehicle, rhOPN added at differentiation onset or at late maturation (e.g., 10–500 ng/mL), positive control (BMP-2 or osteogenic medium alone), and anti-CD44 or anti-integrin blocking controls [15][16].
- **Readouts:**
  - Early differentiation: alkaline phosphatase (ALP) activity and staining at day 7 [15][17].
  - Late mineralization: alizarin red S or von Kossa staining at day 14–21 [16][17].
  - qPCR/WB: Runx2, Sp7 (Osterix), ALP, Col1a1, osteocalcin (OCN), OPN [15][16][17].
  - Optional adipogenesis: Oil Red O staining and PPARγ/adiponectin expression if MSCs are used [16].

**Confidence:** Medium. OPN is an important osteogenic regulator and late marker, but exogenous effects are not uniformly stimulatory and depend on concentration and integrin/CD44 context [15][16].

**Contradiction:** OPN supports MSC osteogenesis in OPN-null cells [16], yet exogenous OPN can suppress FAK-mediated osteoblast responsiveness in mechanically loaded cells [15]. This suggests dose, timing, and mechanical context matter.

---

## 4. Cross-Cutting Contradictions & Gaps

| Issue | Observations | Implication for assay design |
|-------|--------------|------------------------------|
| **Macrophage phenotype** | OPN is linked to M2 maintenance and chemotaxis [9] but does not simply skew M0 to M1/M2 and can dampen LPS responses [8]. | Do not treat OPN as a pure M1 or M2 inducer; include chemotaxis and phagocytosis. |
| **PBMC cytokine direction** | Pro-inflammatory activation in RA PBMCs [11] vs. lower TNF-α and fewer fevers in formula-fed infants [22]. | Test both resting and stimulated PBMCs; report dose-response; control for donor disease state. |
| **Osteoblast response** | OPN restores osteogenesis in OPN-null MSCs [16] but suppresses FAK signaling in mechanically stimulated osteoblasts [15]. | Include multiple time points and mechanical/static conditions; use OPN-null/knockdown rescue where possible. |
| **Intestinal uptake** | Surface binding without internalization [2] vs. N-terminal fragment transcytosis [3]. | Use labeled OPN, time-course, and fragment analysis; compare yeast-expressed vs. bmOPN. |
| **PTM dependence** | Phosphorylation is required for HA inhibition and likely influences receptor binding; yeast OPN may differ from native/mammalian OPN [12][13][14][23]. | Co-characterize phosphorylation/glycosylation of each rhOPN batch; include dephosphorylated control. |
| **Direct yeast OPN data** | Most published cell assays use bmOPN, native human OPN, or non-yeast recombinant OPN. | Run head-to-head reference curves and flag yeast-specific results as novel. |

---

## 5. Suggested First Experiment Set

1. **Analytical QC:** phosphorylation stoichiometry, glycosylation profiling, endotoxin, and SDS-PAGE/SEC of yeast-expressed rhOPN [14][23].
2. **Barrier + immune axis:** Caco-2/HT-29 co-culture (TEER, permeability, TJ proteins, IL-8/IL-10) at infant-formula-relevant OPN concentrations [1][3][4][5].
3. **Immune modulation:** PBMC cytokine multiplex under resting and LPS-stimulated conditions, followed by moDC maturation panel [10][11][6][7].
4. **Bone/calcium function:** HA inhibition assay with phosphorylated vs. dephosphorylated rhOPN [12][13][14].
5. **Secondary:** macrophage polarization and osteoblast differentiation, run only after the primary assays establish active, well-characterized material [8][9][15][16].

---

## 6. Sources

1. **Paper.** Woo et al. (2019). "Osteopontin regulates intestinal barrier function and prevents colitis by modulating tight junctions." *J Nutr Biochem.* PMID: 30146676. https://pubmed.ncbi.nlm.nih.gov/30146676/
2. **Paper.** Nakase et al. (2019). "Uptake and intestinal immunity of food-derived osteopontin: lack of internalization of bovine milk osteopontin by Caco-2 cells." *J Agric Food Chem.* PMID: 30368682. https://pubmed.ncbi.nlm.nih.gov/30368682/
3. **Paper.** Christensen et al. (2023). "Bovine osteopontin binding and N-terminal fragment transport across Caco-2 and Caco-2/HT29-MTX intestinal epithelial models." *Biomedicines.* PMID: 36979733. https://pubmed.ncbi.nlm.nih.gov/36979733/
4. **Paper.** Cai et al. (2025). "Fermentation of osteopontin and 2'-fucosyllactose enhances intestinal epithelial barrier function." *J Agric Food Chem.* DOI: 10.1021/acs.jafc.4c07683. https://doi.org/10.1021/acs.jafc.4c07683
5. **Paper.** Marescotti et al. (2021). "The effects of whey-derived peptides on intestinal permeability and inflammation in Caco-2/HT-29 co-culture." *Front Immunol.* PMCID: PMC8085553. https://pmc.ncbi.nlm.nih.gov/articles/PMC8085553/
6. **Paper.** Kawamura et al. (2005). "Osteopontin inhibits apoptosis and supports human monocyte-derived dendritic cell survival and differentiation." *Cell Immunol.* PMCID: PMC540203. https://pmc.ncbi.nlm.nih.gov/articles/PMC540203/
7. **Paper.** Wang/Cui et al. (2015). "Osteopontin promotes dendritic cell maturation and Th1 immune response in hepatitis B virus infection." *Drug Des Devel Ther.* PMCID: PMC4472071. https://pmc.ncbi.nlm.nih.gov/articles/PMC4472071/
8. **Paper.** Schuch et al. (2016). "Osteopontin modulates macrophage polarization and dampens LPS-induced pro-inflammatory cytokine production." *Immunobiology.* PMID: 27221527. https://pubmed.ncbi.nlm.nih.gov/27221527/
9. **Paper.** Wei et al. (2019). "Osteopontin is a key mediator of M2 macrophage maintenance and chemotaxis." *J Clin Invest.* PMID: 30617191. https://pubmed.ncbi.nlm.nih.gov/30617191/
10. **Paper.** Koguchi et al. (2002). "Osteopontin induces IL-12 production by non-infected peripheral blood mononuclear cells." *J Investig Allergol Clin Immunol.* PMCID: PMC127744. https://pmc.ncbi.nlm.nih.gov/articles/PMC127744/
11. **Paper.** Xu et al. (2005). "Recombinant osteopontin induces pro-inflammatory chemokine and cytokine expression and NF-κB activation in rheumatoid arthritis PBMCs." *J Clin Invest.* PMID: 15800196. https://pubmed.ncbi.nlm.nih.gov/15800196/
12. **Paper.** Hunter & Goldberg (1994). "The inhibitory activity of osteopontin on hydroxyapatite formation in vitro." *Biochem J.* PMCID: PMC1138226. https://pmc.ncbi.nlm.nih.gov/articles/PMC1138226/
13. **Paper.** Pampena et al. (2004). "The inhibition of hydroxyapatite formation by osteopontin phosphopeptides." *Biochem J.* PMCID: PMC1224036. https://pmc.ncbi.nlm.nih.gov/articles/PMC1224036/
14. **Paper.** Gericke et al. (2005). "Importance of phosphorylation for osteopontin regulation of biomineralization." *Calcif Tissue Int.* DOI: 10.1007/s00223-004-1288-1. https://doi.org/10.1007/s00223-004-1288-1
15. **Paper.** Kusuyama et al. (2017). "Osteopontin inhibits osteoblast responses by suppressing focal adhesion kinase signaling." *J Bone Miner Res.* PMCID: PMC5426847. https://pmc.ncbi.nlm.nih.gov/articles/PMC5426847/
16. **Paper.** Chen et al. (2014). "Osteopontin-null mesenchymal stem cells have impaired osteogenesis and enhanced adipogenesis; exogenous OPN restores osteogenesis." *Stem Cells.* PMCID: PMC3961005. https://pmc.ncbi.nlm.nih.gov/articles/PMC3961005/
17. **Paper.** Andrasch et al. (2025). "Osteopontin expression increases during MC3T3-E1 osteoblast differentiation and correlates with late osteogenic markers." *Sci Rep.* PMID: 40000861. https://pubmed.ncbi.nlm.nih.gov/40000861/
18. **Official.** EFSA Panel on Nutrition, Novel Foods and Food Allergens (2022). "Safety of bovine milk osteopontin as a novel food." *EFSA Journal.* DOI: 10.2903/j.efsa.2022.7137. https://doi.org/10.2903/j.efsa.2022.7137
19. **Paper.** Kvistgaard et al. (2014). "Toxicological evaluation of bovine milk osteopontin (Lacprodan® OPN-10)." *Food Chem Toxicol.* PMID: 25072164. https://pubmed.ncbi.nlm.nih.gov/25072164/
20. **Paper.** Fleming et al. (2024). "An expert panel on the adequacy of safety data and physiological roles of dietary bovine osteopontin in infancy." *Front Nutr.* PMCID: PMC11197938. https://pmc.ncbi.nlm.nih.gov/articles/PMC11197938/
21. **Paper.** Sørensen et al. (2023). "Osteopontin in milk: bioactive functions and effects on infant health." *Nutrients.* DOI: 10.3390/nu15112423. https://doi.org/10.3390/nu15112423
22. **Paper.** Lönnerdal et al. (2016). "Growth, nutrition, and cytokine response of breast-fed infants and infants fed formula with added bovine osteopontin." *J Pediatr Gastroenterol Nutr.* PMID: 26465791. https://pubmed.ncbi.nlm.nih.gov/26465791/
23. **Patent.** CN114606148A (2022). "Pichia pastoris strain for expressing osteopontin." Patent number CN114606148A. https://eureka.patsnap.com/patent-CN114606148A
24. **Official.** U.S. FDA (2018). GRAS Notice GRN 716 — Correspondence regarding withdrawal at notifier's request for bovine milk osteopontin. https://www.fda.gov/media/110870/download
