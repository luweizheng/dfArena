# PANCANCER_ATLAS

The original data groups are provided as local Parquet tables.

Original group names remain below for interpreting the original hints. Paths are relative to this dataset directory.

## clinical_database

This database is stored in Parquet format and contains clinical information for patients in the PanCancer Atlas. It includes detailed metadata such as patient identifiers, cancer type acronyms, demographics, diagnosis records, treatment outcomes, survival status, and other clinical annotations.

### clinical_info

99 source columns describing each patient; physical column names and types are listed below. The original document did not individually define these clinical fields.

File: `data/clinical/clinical_info.parquet`

| Column | Arrow type |
|---|---|
| `Patient_description` | string |
| `days_to_birth` | double |
| `days_to_death` | string |
| `days_to_last_followup` | string |
| `days_to_initial_pathologic_diagnosis` | double |
| `age_at_initial_pathologic_diagnosis` | double |
| `icd_10` | string |
| `tissue_retrospective_collection_indicator` | string |
| `icd_o_3_histology` | string |
| `tissue_prospective_collection_indicator` | string |
| `history_of_neoadjuvant_treatment` | string |
| `icd_o_3_site` | string |
| `tumor_tissue_site` | string |
| `new_tumor_event_after_initial_treatment` | string |
| `radiation_therapy` | string |
| `race` | string |
| `prior_dx` | string |
| `ethnicity` | string |
| `informed_consent_verified` | string |
| `person_neoplasm_cancer_status` | string |
| `patient_id` | string |
| `year_of_initial_pathologic_diagnosis` | double |
| `histological_type` | string |
| `tissue_source_site` | string |
| `form_completion_date` | string |
| `pathologic_T` | string |
| `pathologic_M` | string |
| `clinical_M` | string |
| `pathologic_N` | string |
| `system_version` | string |
| `pathologic_stage` | string |
| `clinical_stage` | string |
| `clinical_T` | string |
| `clinical_N` | string |
| `extranodal_involvement` | string |
| `postoperative_rx_tx` | string |
| `primary_therapy_outcome_success` | string |
| `lymph_node_examined_count` | string |
| `primary_lymph_node_presentation_assessment` | string |
| `initial_pathologic_diagnosis_method` | string |
| `number_of_lymphnodes_positive_by_he` | double |
| `eastern_cancer_oncology_group` | string |
| `anatomic_neoplasm_subdivision` | string |
| `residual_tumor` | string |
| `histological_type_other` | string |
| `init_pathology_dx_method_other` | string |
| `karnofsky_performance_score` | string |
| `neoplasm_histologic_grade` | string |
| `height` | double |
| `weight` | double |
| `number_of_lymphnodes_positive_by_ihc` | double |
| `tobacco_smoking_history` | string |
| `number_pack_years_smoked` | double |
| `stopped_smoking_year` | double |
| `performance_status_scale_timing` | string |
| `laterality` | string |
| `targeted_molecular_therapy` | string |
| `year_of_tobacco_smoking_onset` | double |
| `anatomic_neoplasm_subdivision_other` | string |
| `patient_death_reason` | string |
| `tumor_tissue_site_other` | string |
| `menopause_status` | string |
| `margin_status` | string |
| `kras_gene_analysis_performed` | string |
| `venous_invasion` | string |
| `lymphatic_invasion` | string |
| `perineural_invasion_present` | string |
| `her2_immunohistochemistry_level_result` | string |
| `breast_carcinoma_progesterone_receptor_status` | string |
| `breast_carcinoma_surgical_procedure_name` | string |
| `breast_neoplasm_other_surgical_procedure_descriptive_text` | string |
| `axillary_lymph_node_stage_method_type` | string |
| `breast_carcinoma_estrogen_receptor_status` | string |
| `cytokeratin_immunohistochemistry_staining_method_micrometastasi` | string |
| `lab_proc_her2_neu_immunohistochemistry_receptor_status` | string |
| `lab_procedure_her2_neu_in_situ_hybrid_outcome_type` | string |
| `additional_pharmaceutical_therapy` | string |
| `additional_radiation_therapy` | string |
| `lymphovascular_invasion_present` | string |
| `location_in_lung_parenchyma` | string |
| `pulmonary_function_test_performed` | string |
| `egfr_mutation_performed` | string |
| `diagnosis` | string |
| `eml4_alk_translocation_performed` | string |
| `days_to_new_tumor_event_after_initial_treatment` | string |
| `hemoglobin_result` | string |
| `serum_calcium_result` | string |
| `platelet_qualitative_result` | string |
| `number_of_lymphnodes_positive` | string |
| `white_cell_count_result` | string |
| `alcohol_history_documented` | string |
| `family_history_of_cancer` | string |
| `braf_gene_analysis_performed` | string |
| `city_of_procurement` | string |
| `surgical_approach` | string |
| `peritoneal_wash` | string |
| `total_pelv_lnr` | double |
| `total_aor_lnr` | double |
| `prior_glioma` | string |

## molecular_database

This database is stored in Parquet format and contains molecular profiling data of patients in the PanCancer Atlas.

### Mutation_Data

File: `data/molecular/Mutation_Data.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `ParticipantBarcode` | string | Patient identifier |
| `Tumor_SampleBarcode` | string | Tumor sample identifier |
| `Tumor_AliquotBarcode` | string | Tumor aliquot identifier |
| `Normal_SampleBarcode` | string | Normal control sample identifier |
| `Normal_AliquotBarcode` | string | Normal control aliquot identifier |
| `Normal_SampleTypeLetterCode` | string | Sample type abbreviation for the normal sample |
| `Hugo_Symbol` | string | Gene symbol of the mutation (e.g., TP53, CDH1) |
| `HGVSp_Short` | string | Protein-level mutation annotation |
| `Variant_Classification` | string | Classification of the mutation (e.g., Missense_Mutation, Nonsense_Mutation) |
| `HGVSc` | string | Coding DNA sequence mutation annotation |
| `CENTERS` | string | Contributing sequencing center |
| `FILTER` | string | Mutation filter status (e.g., PASS for reliable calls) |

### RNASeq_Expression

File: `data/molecular/RNASeq_Expression.parquet`

| Column | Arrow type | Description |
|---|---|---|
| `ParticipantBarcode` | string | Patient identifier |
| `SampleBarcode` | string | Sample identifier |
| `AliquotBarcode` | string | Aliquot identifier |
| `SampleTypeLetterCode` | string | Sample type abbreviation |
| `SampleType` | string | Sample type description |
| `Symbol` | string | Gene symbol |
| `Entrez` | int64 | Entrez gene ID |
| `normalized_count` | double | Normalized RNA expression value |

## Representation

Structured text, bracketed annotations, and date-like or number-like text are strings. Additional guidance is in context/hints.md when enabled by the experiment configuration.
