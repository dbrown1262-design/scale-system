# Plant Weights Summary — METRC Entry SOP

## 1. Purpose

To define the standardized procedure for using the Plant Weights Summary application to review, verify, and enter harvest weight data into METRC.

This SOP ensures:

* Accurate reporting of harvested cannabis weights
* Proper reconciliation of wet and dry weights
* Consistency between internal records and METRC
* Compliance with regulatory requirements

---

## 2. Scope

This SOP applies to all personnel responsible for:

* Reviewing plant weight data
* Verifying harvest totals
* Entering harvest data into METRC

This procedure covers the use of the Plant Weights Summary application as the **primary source for METRC harvest entry**.

---

## 3. Data Source and System

The Plant Weights Summary application retrieves data from:

* Supabase **scaleplants** table (wet and dry weights)
* Supabase **scalecrops** table (harvest dates)

The application aggregates plant-level data into strain-level totals.

This system is the **official internal record of harvest weights**.

---

## 4. Responsibilities

**Harvest Manager**

* Review plant weight summaries
* Verify completeness of harvest data

**Compliance Officer**

* Enter verified data into METRC
* Ensure accuracy of regulatory reporting

**Quality Assurance (QA)**

* Confirm reconciliation between plant weights and downstream processing

---

## 5. Procedure

### 5.1 Open the Application

1. From the Main Menu, select:
   **Harvest → Plant Summary**
2. The Plant Weights Summary window will open.

---

### 5.2 Select Harvest Crop

1. Use the **Harvest Date** dropdown.
2. Select the desired crop:

   * Format: `CropNo - HarvestDate`
3. Click **Refresh** if needed.

The system will display all strains associated with the selected crop.

---

### 5.3 Review Summary Data

For each strain, the system displays:

* **Strain**
* **Wet Weight (lbs)**
* **Wet Count**
* **Average Wet Weight**
* **Dry Weight (lbs)**
* **Dry Count**
* **Average Dry Weight**

A **TOTAL row** displays:

* Total wet weight
* Total dry weight
* Total plant counts

---

### 5.4 Verify Data Accuracy

Before entering data into METRC:

1. Confirm all expected strains are present.
2. Verify plant counts:

   * WetCount matches harvested plants
   * DryCount matches dried plants
3. Review weights for anomalies:

   * Missing weights
   * Unusually high or low values
4. Confirm dry weights are complete for all plants.

Any discrepancies must be investigated before proceeding.

---

### 5.5 Enter Data into METRC

1. Log into METRC.

2. Navigate to:
   **Harvests → Active Harvests → Finish Harvest**

3. For each strain:

   * Enter total **Dry Weight** from the summary
   * Verify units match (convert if necessary)

4. Confirm:

   * Total weights match internal records
   * No strain is omitted

---

### 5.6 Verification

1. After entry, review METRC totals.
2. Compare METRC entries to:

   * Plant Weights Summary totals
3. A second person should verify:

   * All entries are correct
   * All strains are included

---

### 5.7 Documentation

* Save or export the summary (CSV optional)
* Record verification completion
* Retain documentation for audit purposes

---

## 6. Quality & Compliance Checks

* METRC weights must match Plant Weights Summary totals
* All harvested plants must be accounted for
* Dry weights must be complete prior to entry
* Any corrections must be documented

---

## 7. Records

* Supabase **scaleplants** table
* Supabase **scalecrops** table
* Plant Weights Summary report
* METRC harvest records
* Exported CSV files (if generated)

---

## 8. Relationship to Other Processes

* Plant Weights Summary establishes **harvest totals**

* Bucked totes and trimming data are used for:

  * internal tracking
  * yield analysis
  * mass balance verification

* Final reconciliation is performed using:

  * Harvest Summary report

---

## 9. Revision History

Revision: 1
Effective Date: [Enter Date]
Approved By: President/CEO

Change Summary:
Rev 1 – Initial release; establishes Plant Weights Summary as METRC entry source
