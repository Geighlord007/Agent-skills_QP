# Recommended Cell-Assay Strategy for Yeast-Expressed Human Osteopontin (OPN)

**Project:** Yeast-Expressed Human Osteopontin — Recommended Cell Assays  
**Date:** 26 June 2026  
**Prepared for:** Internal R&D and Regulatory Strategy  
**Status:** Standard-mode research report

---

## 1. Executive Summary

Yeast-expressed human osteopontin (OPN) has no published regulatory approval and no peer-reviewed cell-assay benchmark. The closest precedent is bovine milk OPN (bmOPN), which received a positive EFSA novel-food opinion in 2022 but had its U.S. GRAS notice withdrawn in 2018 because FDA considered a standard toxicology package insufficient for a bioactive ingredient in infant formula [1][2]. Recombinant bovine lactoferrin and β-lactoglobulin produced in *Komagataella phaffii* have since received FDA "no questions" letters for general food use, but explicitly not for infant formula [3][4][5]. This regulatory asymmetry means the assay strategy must generate evidence that is strong enough to address FDA's specific concerns about functional equivalence, ADME, immunomodulation, and developmental safety, while also supporting the more product-focused EU novel-food pathway.

This report recommends a staged assay strategy that separates material qualification from mechanistic and regulatory evidence. The strategy is designed to produce data that can be used across jurisdictions: the product-focused EU novel-food pathway, the more mechanistic U.S. GRAS pathway, and emerging process-focused frameworks such as FSANZ's assessment of precision-fermented proteins:

- **Tier 1 (must run first):** analytical PTM characterization (phosphorylation, glycosylation, endotoxin, host-cell proteins, residual DNA), Caco-2/HT-29 intestinal barrier assay, human PBMC cytokine profiling, and monocyte-derived dendritic cell (moDC) maturation. These assays directly test the biological activities that regulators have flagged as most relevant.
- **Tier 2 (run once active material is confirmed):** hydroxyapatite (HA) inhibition assay, macrophage polarization/phagocytosis, and osteoblast differentiation. These assays support claim substantiation and PTM-function relationships.
- **Tier 3 (parallel regulatory track):** OECD genotoxicity battery and a 90-day rat subchronic study, unless structural and functional equivalence to bmOPN is accepted by the target regulator.

Every assay should include a well-characterized reference standard (native human milk OPN, bmOPN, or a commercial recombinant OPN) because yeast-specific post-translational modifications may alter receptor binding and potency [6][7]. Running head-to-head comparisons from the start avoids the risk of generating uninterpretable data later in the program and provides a foundation for any future equivalence argument to a regulator. The cell-assay program should therefore be viewed as both a scientific characterization effort and a regulatory risk-reduction exercise. By generating comparator data early, the program preserves optionality: if the yeast-expressed material is equivalent to the reference, the path to a dossier is shorter; if it is not, the data will point to the specific PTM or functional gap that must be fixed before further investment.

---

## 2. Background: What Is OPN and Why Does It Matter?

Osteopontin is a secreted, acidic, highly phosphorylated glycoprotein encoded by the human *SPP1* gene [8]. The mature secreted form is 298 amino acids, intrinsically disordered, and carries no cysteines, so it lacks disulfide bridges [8]. Its functional motifs include an RGD integrin-binding site, a thrombin-exposable SVVYGLR motif, heparin- and calcium-binding domains, and a CD44-binding region [9]. Native human milk OPN contains up to 36 phosphoserines and 2 phosphothreonines, plus O-linked glycans that protect the integrin-binding region from gastric digestion [6][9]. These modifications are not decorative: phosphorylation is required for hydroxyapatite inhibition and modulates integrin binding, while O-glycans influence protease resistance and receptor engagement [16][17].

OPN is abundant in human milk (~100–270 mg/L depending on lactation stage and geography) but much lower in bovine milk (~18 mg/L) [9]. This concentration gap has driven interest in recombinant production as a way to match human-milk levels in infant formula or to supply adult nutrition products. OPN is also implicated in bone remodeling, immune cell trafficking, wound healing, and epithelial barrier maintenance, so a recombinant source could in principle support multiple product categories if its activity is demonstrated [9][12].

Zhang et al. (2024) reported the highest published secreted human OPN titers in *Komagataella phaffii*: 35.6 mg/L in shake flask and 128.5 mg/L in a 3-L bioreactor [7]. A Chinese patent application describes a *Pichia pastoris* strain producing 32.2 mg/L, but with substantial intracellular accumulation in vacuoles [10]. These technical achievements show that yeast can express the protein, but they do not establish that the product is functionally equivalent to native human milk OPN. Titer improvements must therefore be paired with analytical and functional characterization before a candidate can advance.

For cell-assay design, the critical uncertainty is therefore not expression titer but **post-translational equivalence**. *Pichia/Komagataella* can hypermannosylate N-glycans and does not perform mammalian FAM20C-type phosphorylation unless engineered [11]. Recombinant OPN produced in *Chlamydomonas* lacked mammalian glycosylation and had fewer phosphorylation sites yet retained bioactivity in mouse pups, suggesting that some functions are robust to PTM differences [12]. However, extrapolation to human cell assays is not automatic, and the specific phosphorylation occupancy and glycan structures produced by a given yeast strain must be measured before assay results can be interpreted or compared across studies. This measurement is a prerequisite for choosing appropriate reference standards and for setting release specifications.

---

## 3. Regulatory Precedent Shapes the Assay Package

The regulatory landscape for OPN and recombinant milk proteins is split: the EU has approved bmOPN for infant nutrition through the novel-food pathway, while the U.S. has not cleared any OPN ingredient for infant formula. More recent FDA approvals for recombinant milk proteins produced in yeast are restricted to general foods. This precedent defines both the minimum safety package and the additional evidence that cell assays can provide.

### 3.1 EFSA approved bmOPN for infant formula; FDA did not

EFSA concluded in 2022 that bmOPN is safe as a novel food at up to 151 mg/L in infant and follow-on formula, based on a genotoxicity battery, a 90-day rat study with NOAEL 1,200 mg/kg/day, and a 6-month infant feeding trial [1]. The margin of exposure was 36. The European Commission authorized bmOPN by Implementing Regulation (EU) 2023/463, with five-year data protection for Arla [13]. EFSA's assessment was product-focused: it accepted the notifier's characterization, toxicology, and exposure estimates while noting limitations in the clinical data without treating them as safety concerns [1].

In contrast, FDA "ceased to evaluate" GRN 716 at the notifier's request in February 2018. Internal memos and an independent expert panel summarized FDA's concerns: high variability of human-milk OPN exposure, relevance of the selected use level, lack of ADME data, potential blood–brain-barrier crossing, long-term immunomodulatory mechanism, functional similarity to human milk OPN, and whether standard toxicology endpoints are adequate for a bioactive protein in infants [2][14]. The withdrawal was not a safety determination; it signaled that the existing package did not resolve mechanistic and developmental questions for the proposed infant-formula use.

### 3.2 Recombinant milk proteins in yeast have cleared FDA for general foods

Since the bmOPN withdrawal, FDA has issued "no questions" letters for *Komagataella*-expressed bovine lactoferrin (GRN 1219, 1284) and β-lactoglobulin (GRN 1200), and for *Trichoderma*-expressed β-lactoglobulin (GRN 863) [3][4][5]. All are explicitly **not intended for infant formula**. Their safety narratives emphasize sequence identity to native milk proteins, long history of safe consumption, non-pathogenic production host, removal of biomass, residual host-protein assessment, and dietary exposure estimates [3][4][5].

These approvals establish that yeast- and filamentous-fungus-derived milk proteins can clear FDA for general food use, but they do not lower the bar for infant formula. Lactoferrin and β-lactoglobulin are primarily nutritional proteins, whereas OPN is a heavily modified phosphoglycoprotein with reported immunomodulatory activity. That functional difference is why the cell-assay package must go beyond identity and purity to demonstrate bioactivity comparable to the native reference. For general food use, the evidence burden is lighter and likely comparable to the lactoferrin/β-lactoglobulin dossiers; for infant formula, the evidence burden remains high because of FDA's GRN 716 experience.

### 3.3 Implication for yeast-expressed human OPN

There is **no regulatory precedent** for yeast-expressed human OPN. A dossier would likely need to address three questions that cell assays can help answer, and the answers will need to be substantially more detailed for infant-formula than for general-food uses:

1. **Functional equivalence:** Does yeast-expressed hOPN engage the same receptors and pathways as native hOPN or bmOPN?
2. **Immunomodulatory signature:** Does it produce an immune response consistent with the published safety package, or does it show unexpected pro-inflammatory activity?
3. **PTM-driven potency:** Is phosphorylation sufficient for mineralization inhibition and receptor binding?

The recommended Tier 1 assays are chosen specifically to generate data relevant to these questions. PBMC and moDC assays address immunomodulation; Caco-2 barrier assays address the first site of contact and ADME-relevant epithelial interaction; HA inhibition assays address PTM-driven function. Without this evidence, a regulator is likely to treat yeast-expressed hOPN as a novel entity requiring a full stand-alone safety package.

---

## 4. Recommended Assays by Priority Tier

### 4.1 Tier 1: Analytical QC and core bioactivity

#### 4.1.1 PTM and purity characterization

Before any cell assay, characterize each rhOPN batch for phosphorylation stoichiometry, glycosylation profile, molecular weight, aggregation state, endotoxin, residual host protein, and residual DNA [11][15]. Phosphorylation is especially important because HA inhibition and integrin binding are phosphorylation-sensitive [16][17].

#### 4.1.2 Caco-2 / HT-29 intestinal barrier assay

**Rationale:** The intestine is the first site of contact for orally delivered OPN. Endogenous OPN supports occludin phosphorylation and tight-junction localization in Caco-2 monolayers [18]. Bovine milk OPN binds Caco-2 cells and N-terminal fragments can be transported across Caco-2/HT29-MTX co-cultures [19].

**Protocol outline:**
- Models: Caco-2 monoculture (21-day differentiation) or Caco-2:HT29-MTX co-culture on Transwell inserts [19][20].
- Challenge: basal condition or cytokine cocktail to model inflammation [20].
- Treatment: yeast-expressed rhOPN at 25–200 µg/mL, with bmOPN or commercial rhOPN as reference.
- Readouts: TEER, FITC-dextran / [³H]-mannitol Papp, tight-junction proteins (occludin, ZO-1, claudins) by IF/WB/qPCR, and basolateral IL-8, IL-6, TNF-α, IL-10 [18][19][20].

**Confidence:** High for bmOPN/native OPN; Medium for yeast-expressed OPN until phosphorylation/glycosylation effects are quantified.

#### 4.1.3 Human PBMC cytokine profiling

**Rationale:** PBMCs provide a direct readout of immune modulation and bridge to the infant-formula cytokine data, where bmOPN lowered plasma TNF-α and was associated with fewer febrile episodes [21]. Native OPN induces IL-12 production by non-stimulated PBMCs in a dose-dependent manner, with optimal activity around 50 µg/mL [22].

**Protocol outline:**
- Model: human PBMCs isolated by density-gradient centrifugation, plated at ~2 × 10⁶ cells/mL [22].
- Treatment: rhOPN alone (0.1–100 µg/mL) and rhOPN + LPS (10 ng/mL).
- Readouts: multiplex ELISA for IL-12, TNF-α, IFN-γ, IL-6, IL-1β, IL-8, CCL2, CXCL1, IL-10, IL-2 [22][23][21].

**Interpretation note:** Exogenous OPN can activate NF-κB and pro-inflammatory chemokines in rheumatoid-arthritis PBMCs [23], whereas dietary bmOPN in infants is associated with lower TNF-α [21]. Directionality is context- and dose-dependent, so test both resting and stimulated conditions.

#### 4.1.4 Monocyte-derived dendritic cell (moDC) maturation

**Rationale:** OPN is required for moDC differentiation, survival, and maturation, and it primes naive T cells toward a Th1-polarizing phenotype [24][25]. Neutralizing anti-OPN reduces CD86 and HLA-DR expression and increases apoptosis [24].

**Protocol outline:**
- Model: CD14+ monocytes differentiated 5–6 days with GM-CSF + IL-4 [24][25].
- Treatment: rhOPN during differentiation and/or LPS maturation trigger (0.1–10 µg/mL), with anti-OPN neutralizing antibody as mechanistic control [24][25].
- Readouts: flow cytometry for CD14, CD11c, CD83, CD86, HLA-DR, CD80; cytokines IL-12p70, TNF-α, IL-10, IL-4; Annexin V apoptosis [24][25].

### 4.2 Tier 2: Mechanistic and claim-supporting assays

#### 4.2.1 Hydroxyapatite (HA) inhibition assay

**Rationale:** OPN is a potent inhibitor of hydroxyapatite crystal formation, with an IC₅₀ of ~0.06 µg/mL for native phosphorylated OPN [16]. Activity requires both phosphate and carboxylate groups; dephosphorylation reduces activity more than 40-fold [16][17].

**Protocol outline:**
- Model: cell-free constant-composition pH-stat titration or agarose gel diffusion [16][17].
- Treatment: yeast-expressed rhOPN, dephosphorylated rhOPN as negative control, phosphorylated OPN or poly-L-aspartate as positive control [16][17].
- Readouts: nucleation lag time, crystal growth rate, IC₅₀, and phosphorylation stoichiometry by mass spectrometry [16][17].

**Confidence:** High for native phosphorylated OPN; Low to Medium for yeast-expressed OPN unless phosphorylation is demonstrated.

#### 4.2.2 Macrophage polarization and phagocytosis

**Rationale:** OPN is linked to M2-signature maintenance and chemotaxis, but it does not simply skew M0 to M1 or M2 and can dampen LPS-induced pro-inflammatory cytokine production [26][27].

**Protocol outline:**
- Model: THP-1-derived macrophages or CD14+ monocyte-derived macrophages, polarized with LPS + IFN-γ (M1) or IL-4 + IL-13 (M2) [26][27].
- Readouts: surface markers (CD86/CD80 for M1; CD163/CD206/CD204 for M2), cytokines (TNF-α, IL-6, IL-1β, IL-10), phagocytosis, and Transwell migration [26][27].

**Interpretation note:** Do not treat OPN as a pure M1 or M2 inducer. Include chemotaxis and phagocytosis as primary readouts.

#### 4.2.3 Osteoblast differentiation

**Rationale:** OPN is a late marker of osteogenic differentiation and supports osteogenesis in OPN-null mesenchymal stem cells, but exogenous effects vary with concentration and mechanical context [28][29].

**Protocol outline:**
- Model: MC3T3-E1 pre-osteoblasts or human MSCs in osteogenic medium [28][29].
- Readouts: ALP activity at day 7, alizarin red mineralization at day 14–21, qPCR/WB for Runx2, Sp7, ALP, Col1a1, OCN, OPN [28][29].

### 4.3 Tier 3: Regulatory safety package

Based on bmOPN and recombinant milk-protein precedents, the expected regulatory safety package includes [1][3][4][5][14]:

- OECD 471 bacterial reverse mutation assay.
- OECD 473 in vitro chromosome aberration or OECD 487 in vitro micronucleus assay.
- OECD 474 in vivo micronucleus assay.
- OECD 408 90-day rat subchronic toxicity study (current guideline includes thyroid hormones).
- Allergenicity assessment: sequence homology, pepsin digestibility, and, if indicated, serum IgE binding.
- Residual host-protein and DNA quantification with validated clearance rationale.

These are not cell assays in the narrow sense, but the cell-assay data should align with and support the safety narrative. For example, if PBMC and moDC assays show no unexpected pro-inflammatory signal at intended exposure levels, that evidence can be cited to support the absence of immunotoxicity concern. Conversely, if an unexpected cytokine profile appears, the 90-day study design and clinical monitoring endpoints should be adjusted accordingly. The cell-assay program and the regulatory toxicology program should therefore be planned together, not as separate workstreams.

---

## 5. Cross-Cutting Experimental Design Principles

The following three principles apply across all tiers. They are intended to prevent common failure modes: uninterpretable results due to missing comparators, over-claims from single-point data, and loss of credibility from ignored contradictions. Applying them consistently will make the difference between a dataset that merely looks positive and a dataset that can support a regulatory decision.

### 5.1 Always include a reference standard

Because yeast PTMs may differ from mammalian PTMs, every assay should compare yeast-expressed rhOPN side-by-side with bmOPN, commercial rhOPN, or native human milk OPN. This directly addresses the functional-equivalence question raised by FDA in GRN 716 [2][14]. The reference standard should be analytically characterized in the same batch of experiments: molecular weight, phosphorylation occupancy, glycosylation profile, and endotoxin. Without this comparator, a positive or negative result cannot be attributed to the protein, the production system, or an assay artifact. The comparator also provides a potency benchmark for release specifications and equivalence claims, helps detect batch-to-batch drift in the yeast process, and makes it possible to distinguish a true biological effect from an assay artifact or PTM-dependent change. In practice, this means the reference standard should be run on every assay plate and its response should fall within a pre-defined acceptance window before the yeast-expressed sample is evaluated.

### 5.2 Report dose-response, not single-point activity

OPN effects are dose- and context-dependent. A single high-dose result is not enough to support a safety or efficacy claim. Report full dose-response curves and note where responses plateau or reverse. In the infant-formula literature, 65 mg/L produced weaker signals than 130 mg/L for some immune endpoints, suggesting a non-linear dose relationship [21]. In PBMC assays, native OPN shows optimal IL-12 induction around 50 µg/mL, but rheumatoid-arthritis PBMCs respond to 1 µg/mL with pro-inflammatory chemokines [22][23]. The assay program should therefore define the active concentration range for each readout, include both pharmacological and supra-pharmacological concentrations, and explain how that range relates to intended human exposure. Dose-response data also support the selection of relevant concentrations for any subsequent animal toxicology study and help justify the margin between cellular effect levels and anticipated human intake for each intended use population.

### 5.3 Flag contradictions rather than smoothing them over

The literature contains genuine contradictions: OPN can activate or suppress autophagy depending on cell type [30][31], promote Th1 responses in some models but be dispensable in others [32], and appear pro-inflammatory in RA PBMCs but anti-inflammatory in infant feeding trials [21][23]. The report and the assay protocol should acknowledge these context dependencies rather than forcing a single mechanistic narrative. Present the conditions under which each effect is observed, the cell type, the disease state, and the OPN dose, and explain how the chosen assay design controls for those conditions. This intellectual honesty strengthens the regulatory and scientific case and reduces the risk of a later contradiction undermining the entire dossier. It also helps reviewers understand why a result that differs from a published study is still internally valid, and it guides the design of follow-up experiments to resolve apparently conflicting findings in a transparent manner.

---

## 6. Suggested Execution Sequence

The following 12-week integrated plan separates material qualification, mechanistic cell assays, and regulatory preparation. It assumes that a purified, analytically characterized yeast-expressed rhOPN batch is available at the start of Week 0, that the reference standard has been selected and qualified, and that human primary cells or approved cell lines are ready for use. Regulatory and CRO discussions are started in parallel so that the toxicology package can be initiated as soon as Tier 1 data support a go decision. The plan is intentionally front-loaded: if the candidate fails the Tier 1 analytical or bioactivity gates, the program can be paused before committing to the more expensive Tier 2 and Tier 3 work. This sequencing reduces the risk of investing in a full toxicology package for a material that has not first demonstrated relevant bioactivity and acceptable purity.

| Phase | Timing | Activities |
|-------|--------|------------|
| 0 | Week 0 | Define reference standard and acceptance criteria; analytical QC of yeast-expressed rhOPN batch (phosphorylation stoichiometry, glycosylation profile, SDS-PAGE/SEC, endotoxin, host-cell proteins, residual DNA) [11][15]. |
| 1 | Weeks 1–4 | Tier 1 cell assays: Caco-2/HT-29 barrier (TEER, permeability, tight-junction markers, cytokines), PBMC cytokine multiplex under resting and LPS-stimulated conditions, and moDC maturation panel (CD83, CD86, HLA-DR, IL-12p70) [18][19][20][21][22][23][24][25]. |
| 2 | Weeks 5–8 | Tier 2 assays: HA inhibition with phosphorylated and dephosphorylated controls, macrophage polarization and phagocytosis, and osteoblast differentiation in MC3T3-E1 or human MSCs [16][17][26][27][28][29]. |
| 3 | Parallel | Initiate regulatory safety-package discussions with target agencies and CRO procurement for OECD genotoxicity battery and 90-day rat subchronic study; draft study protocols based on Tier 1 findings [1][3][4][5][14]. |
| 4 | Week 12 | Integrate data, compare yeast rhOPN to reference standards across all assays, identify any unexpected signals, and decide whether to proceed to larger toxicology studies or reformulate the candidate before investing in the full regulatory package. |

Go/no-go criteria between phases should be explicit and documented. For example, if Tier 1 shows that yeast-expressed rhOPN lacks phosphorylation and fails HA inhibition, the program should pause to engineer phosphorylation (e.g., co-expression of FAM20C or in vitro kinase treatment) before proceeding to Tier 2 claim-supporting assays. Similarly, if PBMC or moDC assays reveal an unexpected pro-inflammatory signature relative to the reference standard, the program should reformulate or add mechanistic controls before committing to a 90-day toxicology study. Clear gates protect both scientific quality and capital efficiency.

---

## 7. Key Risks and Data Gaps

The following risks are not theoretical; each is grounded in a specific precedent or data gap identified in the literature and regulatory record. Addressing them should be part of the assay program's success criteria, not an afterthought. Several of these risks can be mitigated or closed through the recommended Tier 1 and Tier 2 assays, while others require parallel regulatory engagement.

1. **No regulatory precedent for yeast-expressed human OPN.** The closest precedent (bmOPN) was withdrawn in the U.S. and approved only in the EU [1][2]. A yeast-expressed human OPN may be treated as a different novel food from bmOPN, requiring its own full dossier rather than reliance on the existing approval.

2. **PTM uncertainty.** Yeast may under-phosphorylate and hypermannosylate OPN, affecting receptor binding, HA inhibition, and immunogenicity [11][16]. If phosphorylation is insufficient, the material may not support bone-health or barrier claims, and the immunomodulatory profile may differ from native OPN.

3. **Immunomodulatory mechanism not fully understood.** OPN has both activating and regulatory effects on DCs and macrophages, complicating safety interpretation [24][25][26][27]. An unexpected cytokine signature in PBMC or moDC assays could trigger additional toxicology or clinical endpoints.

4. **No published yeast-expressed hOPN cell-assay data.** All recommendations are extrapolated from bmOPN, native hOPN, or non-yeast recombinant systems. The first yeast-expressed OPN dataset will therefore be novel and must be interpreted conservatively.

5. **EU data-protection barrier.** Arla holds EU data protection for bmOPN until March 2028, which may complicate reliance on its dossier for a yeast-expressed hOPN application [13]. A subsequent applicant would need to rely on publicly available data or generate a stand-alone package.

6. **Infant-formula regulatory asymmetry.** FDA's withdrawal of GRN 716 suggests that the U.S. pathway for OPN in infant formula is currently blocked without extensive developmental-safety data. The cell-assay program should be designed to generate the mechanistic and equivalence evidence that FDA identified as missing.

These risks do not make the program unviable, but they do mean that the cell-assay work must be rigorous enough to stand on its own. The goal is not simply to generate positive results, but to generate interpretable, well-controlled data that can survive regulatory and scientific scrutiny, clearly separate what is known from what remains to be demonstrated, and guide go/no-go decisions at each stage of development.

---

## 8. References
[1] EFSA NDA Panel. EFSA: Safety of bovine milk osteopontin as a novel food. *EFSA Journal*. 2022. EFSA J 20(5):7137. https://doi.org/10.2903/j.efsa.2022.7137

[2] U.S. FDA. FDA GRAS Notice GRN 716 — Bovine milk osteopontin. *GRAS Notice Inventory*. 2018. GRN 716. https://www.cfsanappsexternal.fda.gov/scripts/fdcc/index.cfm?set=GRASNotices&id=716

[3] U.S. FDA. FDA response letter GRN 1219 — Recombinant bovine lactoferrin from Komagataella phaffii M020. *GRAS Notice Inventory*. 2025. GRN 1219. https://www.fda.gov/media/187721/download

[4] U.S. FDA. FDA response letter GRN 1284 — Recombinant bovine lactoferrin from Komagataella phaffii Ppas_337. *GRAS Notice Inventory*. 2026. GRN 1284. https://www.fda.gov/media/191907/download

[5] U.S. FDA. FDA response letter GRN 1200 — β-lactoglobulin from Komagataella phaffii VIPLA. *GRAS Notice Inventory*. 2025. GRN 1200. https://www.fda.gov/media/187493/download

[6] Christensen B, et al.. Post-translationally modified residues of native human osteopontin. *Biochemical Journal*. 2005. PMID 15869464. https://pubmed.ncbi.nlm.nih.gov/15869464/

[7] Zhang Z, et al.. Efficient secretory expression of human milk osteopontin in Komagataella phaffii. *Future Foods*. 2024. DOI 10.1016/j.fufo.2024.100393. https://doi.org/10.1016/j.fufo.2024.100393

[8] UniProt Consortium. UniProt: Osteopontin (P10451). *UniProtKB/Swiss-Prot*. 2026. P10451. https://www.uniprot.org/uniprotkb/P10451

[9] Sørensen ES, Christensen B. Osteopontin in milk: structure, function, and health effects. *International Dairy Journal*. 2023. PMID/PMC review. https://pmc.ncbi.nlm.nih.gov/articles/PMC10255459/

[10] Chinese Patent Application CN114606148A. Pichia pastoris strain for expressing osteopontin. *CNIPA*. 2022. CN114606148A. https://eureka.patsnap.com/patent-CN114606148A

[11] Teh AY-H, et al.. Recombinant human erythropoietin production in Pichia pastoris and glycosylation analysis. *Plant Biotechnology Journal*. 2011. PMID 21666729. https://pmc.ncbi.nlm.nih.gov/articles/PMC3168189/

[12] Jiang R, Tran M, Lönnerdal B. Recombinant bovine and human osteopontin generated by Chlamydomonas reinhardtii exhibit bioactivities similar to bovine milk osteopontin. *Molecular Nutrition & Food Research*. 2021. DOI 10.1002/mnfr.202000644. https://doi.org/10.1002/mnfr.202000644

[13] European Commission. Commission Implementing Regulation (EU) 2023/463 authorising bovine milk osteopontin as a novel food. *Official Journal of the European Union*. 2023. CELEX 32023R0463. https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX:32023R0463

[14] Fleming SA, et al.. An expert panel on the adequacy of safety data and physiological roles of dietary bovine osteopontin in infancy. *Frontiers in Nutrition*. 2024. PMC11197938. https://www.frontiersin.org/journals/nutrition/articles/10.3389/fnut.2024.1404303/full

[15] ICH. ICH Q6B Specifications: Test procedures and acceptance criteria for biotechnological/biological products. *ICH Guidelines*. 1999. Q6B. https://database.ich.org/sites/default/files/Q6B%20Guideline.pdf

[16] Hunter GK, Goldberg HA. The inhibitory activity of osteopontin on hydroxyapatite formation in vitro. *Biochemical Journal*. 1994. PMC1138226. https://pmc.ncbi.nlm.nih.gov/articles/PMC1138226/

[17] Gericke A, et al.. Importance of phosphorylation for osteopontin regulation of biomineralization. *Calcified Tissue International*. 2005. DOI 10.1007/s00223-004-1288-1. https://doi.org/10.1007/s00223-004-1288-1

[18] Woo SH, et al.. Osteopontin protects colonic mucosa from DSS-induced acute colitis by regulating junctional distribution of occludin. *Digestive Diseases and Sciences*. 2019. PMID 30146676. https://pubmed.ncbi.nlm.nih.gov/30146676/

[19] Christensen B, et al.. Bovine osteopontin binding and N-terminal fragment transport across Caco-2 and Caco-2/HT29-MTX intestinal epithelial models. *Biomedicines*. 2023. PMID 36979733. https://pubmed.ncbi.nlm.nih.gov/36979733/

[20] Marescotti MC, et al.. The effects of whey-derived peptides on intestinal permeability and inflammation in Caco-2/HT-29 co-culture. *Frontiers in Immunology*. 2021. PMC8085553. https://pmc.ncbi.nlm.nih.gov/articles/PMC8085553/

[21] Lönnerdal B, et al.. Growth, nutrition, and cytokine response of breast-fed infants and infants fed formula with added bovine osteopontin. *Journal of Pediatric Gastroenterology and Nutrition*. 2016. PMID 26465791. https://pubmed.ncbi.nlm.nih.gov/26465791/

[22] Koguchi Y, et al.. Osteopontin induces IL-12 production by non-infected peripheral blood mononuclear cells. *Journal of Investigational Allergology and Clinical Immunology*. 2002. PMC127744. https://pmc.ncbi.nlm.nih.gov/articles/PMC127744/

[23] Xu G, et al.. Recombinant osteopontin induces pro-inflammatory chemokine and cytokine expression and NF-κB activation in rheumatoid arthritis PBMCs. *Journal of Clinical Investigation*. 2005. PMID 15800196. https://pubmed.ncbi.nlm.nih.gov/15800196/

[24] Kawamura K, et al.. Differentiation, maturation, and survival of dendritic cells by osteopontin regulation. *Clinical and Diagnostic Laboratory Immunology*. 2005. PMID 15643009. https://pubmed.ncbi.nlm.nih.gov/15643009/

[25] Cui G, et al.. Osteopontin promotes dendritic cell maturation and Th1 immune response in hepatitis B virus infection. *Drug Design, Development and Therapy*. 2015. PMC4472071. https://pmc.ncbi.nlm.nih.gov/articles/PMC4472071/

[26] Schuch K, et al.. Osteopontin affects macrophage polarization promoting endocytic but not inflammatory properties. *Obesity*. 2016. PMID 27221527. https://pubmed.ncbi.nlm.nih.gov/27221527/

[27] Wei J, et al.. Osteopontin is a key mediator of M2 macrophage maintenance and chemotaxis. *Journal of Clinical Investigation*. 2019. PMID 30617191. https://pubmed.ncbi.nlm.nih.gov/30617191/

[28] Chen Y, et al.. Osteopontin-null mesenchymal stem cells have impaired osteogenesis and enhanced adipogenesis. *Stem Cells*. 2014. PMC3961005. https://pmc.ncbi.nlm.nih.gov/articles/PMC3961005/

[29] Kusuyama J, et al.. Osteopontin inhibits osteoblast responses by suppressing focal adhesion kinase signaling. *Journal of Bone and Mineral Research*. 2017. PMC5426847. https://pmc.ncbi.nlm.nih.gov/articles/PMC5426847/

[30] Zheng YH, et al.. Osteopontin stimulates autophagy via integrin/CD44 and p38 MAPK signaling pathways in vascular smooth muscle cells. *Journal of Cellular Physiology*. 2012. PMID 21374592. https://pubmed.ncbi.nlm.nih.gov/21374592/

[31] Bai RJ, et al.. OPN inhibits autophagy through CD44, integrin and the MAPK pathway in osteoarthritic chondrocytes. *Frontiers in Endocrinology*. 2022. PMID 36034459. https://pubmed.ncbi.nlm.nih.gov/36034459/

[32] Abel B, et al.. Osteopontin is not required for the development of Th1 responses and viral immunity. *Journal of Immunology*. 2005. PMID 16237095. https://pubmed.ncbi.nlm.nih.gov/16237095/
