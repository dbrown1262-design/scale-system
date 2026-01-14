# Plant Weights Summary SOP

## 1. Purpose

To define the standardized procedure for viewing and analyzing plant weight data by strain for completed harvest crops. This report provides summary statistics for wet weights, dry weights, plant counts, and averages per strain to support crop analysis, yield tracking, and compliance verification.

---

## 2. Inputs

- Supabase scaleplants table (wet/dry weight data)
- Supabase scalecrops table (harvest dates)
- Scale application database connection

---

## 3. Responsibilities

- **Harvest Manager:** Review plant weight summaries to analyze crop yields and strain performance.
- **Quality Assurance:** Verify weight data completeness and accuracy.
- **Compliance Officer:** Use summary data for regulatory reporting and record-keeping.

---

## 4. Procedure

### 4.1 Access the Plant Weights Summary Application

1. From the Main Menu, select **Harvest → Plant Summary**.
2. The Plant Weights Summary window will open displaying the harvest date selector and data grid.

---

### 4.2 Select a Harvest Crop

1. At the top of the window, locate the **Harvest Date** dropdown.
2. Click the dropdown to view available harvest crops.
	- Crops are listed in the format: `CropNo - HarvestDate` (e.g., "20 - 2025-12-12").
3. Select the desired crop from the list.
4. The system will automatically load and display weight data for all strains in that crop.
5. Click **Refresh** if you need to reload the data.

---

### 4.3 Review Summary Data

The summary table displays the following columns for each strain:

- **Strain:** The strain name for the group of plants
- **WetWeight:** Total wet weight in pounds for all plants of this strain
- **WetCount:** Number of plants with recorded wet weights (weight > 0)
- **Avg Wet:** Average wet weight per plant in pounds (WetWeight ÷ WetCount)
- **DryWeight:** Total dry weight in pounds for all plants of this strain
- **DryCount:** Number of plants with recorded dry weights (weight > 0)
- **Avg Dry:** Average dry weight per plant in pounds (DryWeight ÷ DryCount)

**Total Row**

At the bottom of the table, a **TOTAL** row displays:
- Combined wet and dry weights across all strains
- Total counts of plants weighed wet and dry
- (Average columns are blank for the total row)

**Interpretation**

- Use **WetCount** and **DryCount** to verify all expected plants have been weighed.
- Compare **Avg Wet** and **Avg Dry** across strains to identify high-yielding or low-yielding varieties.
- Review totals to confirm overall crop yield and compliance with expected plant counts.

---

### 4.4 Export Data (Optional)

1. Click the **Export CSV** button at the bottom of the window.
2. The system will generate a CSV file containing all displayed data.
3. The file location will be displayed in the status area (typically in your system's temporary folder).
4. Use this CSV for:
	- External reporting
	- Data analysis in spreadsheet applications
	- Long-term record archival
	- Compliance documentation

**CSV Format**

The exported file includes:
- Header row with column names
- One row per strain with all weight statistics
- Total row at the end

---

### 4.5 Close the Application

1. Click the **Close** button to exit the Plant Weights Summary application.
2. The system will return to the Main Menu.

---

## 5. Quality & Compliance Checks

- Verify that WetCount and DryCount match the expected number of plants for each strain.
- Confirm all plants from the crop have been weighed (compare counts to original import from Bamboo).
- Check for zero or unusually low/high average weights that may indicate data entry errors.
- Ensure dry weights are present for all plants before final harvest completion.
- Missing weights should be investigated and corrected in the weighing applications.

---

## 6. Records

- Supabase scaleplants table (source data)
- Exported CSV files (when generated)
- Screen captures of summary data (for compliance documentation if needed)
- Crop yield analysis reports

---

## 7. Troubleshooting

**Problem:** "No crops found" message appears

- **Solution:** Verify that crops have been imported into the scalecrops table. Contact the administrator to add crop records.

**Problem:** Strain shows zero count but plants were weighed

- **Solution:** Check the scaleplants table to ensure weights were saved correctly. Weights of exactly 0 are not counted; ensure actual weight values were recorded.

**Problem:** Counts don't match expected plant numbers

- **Solution:** 
  1. Verify all plants were weighed using the Weigh Harvest application.
  2. Check for plants that may have been assigned to the wrong crop number.
  3. Review the original Bamboo import to confirm plant counts.

---

## 8. Related Procedures

- **Print Plant Tags:** Initial crop setup and plant tagging
- **Weigh Harvest:** Recording wet and dry plant weights
- **Weigh Bucked Totes:** Post-processing weight tracking
