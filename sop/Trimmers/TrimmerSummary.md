# Trimmer Summary SOP

## 1. Purpose

To define the standardized procedure for generating weekly trimmer performance reports and strain-specific summaries. This report provides detailed information on trimmer productivity, work hours, flower and smalls weights, and calculated pay rates to support payroll processing, performance tracking, and operational planning.

---

## 2. Inputs

- Supabase scale.trimdaily table (daily trimmer work records)
- Supabase scale.trimrates table (pay rates per strain)
- Supabase scalecrops table (crop information)
- Supabase scalestrains table (strain names)
- PDF generation library (ReportLab)

---

## 3. Responsibilities

- **Harvest Manager:** Generate weekly trimmer reports for payroll processing and performance review.
- **Payroll Administrator:** Use summary data to calculate trimmer pay and verify hours worked.
- **Operations Manager:** Analyze trimmer productivity across strains and identify training needs.
- **Quality Assurance:** Verify data completeness and accuracy before payroll processing.

---

## 4. Procedure

### 4.1 Access the Trimmer Summary Application

1. From the Main Menu, select **Trimmer → Weekly Trimmer Summary**.
2. The Trimmer Summary window will open with two tabs:
	- **Weekly Summary:** Shows detailed daily work records for a selected week
	- **Trimmer Strain Summary:** Shows aggregate data for a specific strain over a date range

---

### 4.2 Generate Weekly Summary Report

#### 4.2.1 Select Report Parameters

1. In the **Weekly Summary** tab, locate the filter controls at the top of the window.
2. **Select Trimmer:**
	- Click the **Trimmer** dropdown.
	- Choose a specific trimmer name to view individual performance, or select **All** to view combined data for all trimmers.
3. **Select Start Date:**
	- Click the **Start Date** calendar selector.
	- Select the first day of the work week (typically Monday).
	- The system will automatically include data through the next 6 days (full 7-day week).
4. Click the **Load Week** button to generate the report.

#### 4.2.2 Review Weekly Summary Data

The weekly summary displays data organized by date with the following information for each day:

**Per-Day Sections:**
- **Date:** The work date
- **Strain:** Cannabis strain being trimmed
- **Flower (g):** Weight of premium flower trimmed (in grams)
- **Smalls (g):** Weight of small buds trimmed (in grams)
- **Start Time:** Work session start time (displayed in 12-hour format with AM/PM)
- **End Time:** Work session end time (displayed in 12-hour format with AM/PM)
- **Hours:** Total hours worked on this strain (calculated from start and end times)

**Week Grand Total:**
- At the bottom of the daily sections, view cumulative totals:
	- **Flower:** Total grams of flower trimmed for the week
	- **Smalls:** Total grams of smalls trimmed for the week

**Pay Summary — Flower (Bigs):**
- **CropNo:** Crop number for the harvest
- **Strain:** Cannabis strain
- **Rate:** Pay rate per gram for this strain (from trimrates table)
- **Total Grams:** Total flower weight trimmed for this crop/strain combination
- **Pay:** Calculated payment (Total Grams × Rate)

#### 4.2.3 Interpret the Data

**Performance Analysis:**
- Compare hours worked to grams trimmed to calculate productivity rates.
- Identify high-performing trimmers for recognition or best practice sharing.
- Detect low productivity that may indicate training needs or equipment issues.

**Payroll Verification:**
- Verify all work sessions have valid start and end times.
- Confirm pay rates match approved rate schedules.
- Check that total hours align with expected work schedules.

**Data Quality Checks:**
- Missing times indicate incomplete data entry requiring correction.
- Zero weights suggest data entry errors or missed entries.
- Unusually high/low productivity rates may indicate data errors.

---

### 4.3 Export Weekly Summary PDF

1. After loading the weekly summary, click the **Export Report PDF** button.
2. The system will generate a formatted PDF report containing:
	- Report title and date range
	- Trimmer name (if individual report)
	- Daily work sessions with all detail columns
	- Grand totals for the week
	- Pay summary with calculated payments
3. The PDF will automatically open in your default PDF viewer.
4. The file is saved to your system's temporary folder with the filename: `trimmer_summary_report.pdf`

**Use the exported PDF for:**
- Payroll processing and record-keeping
- Trimmer performance reviews
- Compliance documentation
- Historical record archival

---

### 4.4 Generate Trimmer Strain Summary

The **Trimmer Strain Summary** tab provides an alternative view focused on a specific strain across multiple trimmers and dates.

#### 4.4.1 Select Strain Summary Parameters

1. Click the **Trimmer Strain Summary** tab at the top of the window.
2. **Select Crop:**
	- Click the **Crop** dropdown.
	- Choose a crop number and harvest date (format: "CropNo - HarvestDate").
	- The strain dropdown will update with strains available for the selected crop.
3. **Select Strain:**
	- Click the **Strain** dropdown.
	- Choose the specific strain to analyze.
4. **Select Date Range:**
	- Set **Start** date using the calendar selector.
	- Set **End** date using the calendar selector.
	- This defines the reporting period for the strain analysis.
5. Click **Load Strain Summary** to generate the report.

#### 4.4.2 Review Strain Summary Data

The strain summary table displays:
- **Date:** Work date
- **Trimmer:** Name of the trimmer who worked on this strain
- **Flower:** Grams of flower trimmed
- **Smalls:** Grams of smalls trimmed

A **TOTAL** row at the bottom shows cumulative weights across all trimmers and dates for the selected strain.

**Use this view to:**
- Compare trimmer performance on the same strain
- Track total production for a specific strain over time
- Identify which trimmers are most efficient with particular strains
- Support crop-specific reporting and analysis

#### 4.4.3 Export Strain Summary PDF

1. After loading the strain summary, click **Export Strain PDF**.
2. The system generates a formatted PDF with the strain-specific data.
3. The PDF automatically opens in your default viewer.

---

### 4.5 Close the Application

1. Click the **Close** button in the filter row to exit the Trimmer Summary application.
2. The system will return to the Main Menu.

---

## 5. Quality & Compliance Checks

- **Verify Complete Time Records:** All work sessions must have both start and end times recorded.
- **Validate Pay Rates:** Confirm rates in the Pay Summary match approved rate schedules in the trimrates table.
- **Check for Data Gaps:** Ensure all expected work days have entries for active trimmers.
- **Review Totals:** Grand totals should align with expected weekly production volumes.
- **Audit Hours Calculation:** Spot-check calculated hours against expected shift durations.
- **Zero Weight Records:** Investigate any entries with zero flower or smalls weights.
- **Cross-Reference with Attendance:** Compare trimmer hours with time clock or attendance records.

---

## 6. Records

- Weekly summary PDF reports (archived by date and trimmer)
- Strain summary PDF reports (archived by crop and strain)
- Supabase trimdaily table (source data for all reports)
- Payroll calculation worksheets (derived from summary data)
- Performance review documentation

---

## 7. Troubleshooting

**Problem:** "All" trimmer filter shows no data

- **Solution:** Verify that trimdaily table contains records for the selected week. Check that data entry was completed in the Enter Daily Trim application.

**Problem:** Pay rates show as $0.00 or incorrect amounts

- **Solution:** 
  1. Verify trimrates table has entries for all strains being trimmed.
  2. Contact administrator to update missing or incorrect rates.
  3. Use the Edit Trim Rates application (Admin menu) to correct rate data.

**Problem:** Hours calculation shows 0.00 or negative values

- **Solution:**
  1. Check that End Time is later than Start Time.
  2. Verify times are in 24-hour format in the database (HH:MM:SS).
  3. Correct invalid time entries using Edit Daily Trim application.

**Problem:** PDF export fails or file won't open

- **Solution:**
  1. Check that you have a PDF viewer installed.
  2. Verify write permissions to the system temporary folder.
  3. Close any previously opened summary PDF files.
  4. Try exporting again.

**Problem:** Strain dropdown is empty after selecting a crop

- **Solution:** The selected crop may not have strain data. Verify that plants were imported with strain information for this crop in the scaleplants table.

**Problem:** Trimmer appears in list but has no data for the week

- **Solution:** Verify that work records were entered for this trimmer in the Enter Daily Trim application. If trimmer did not work during the selected week, this is expected behavior.

---

## 8. Related Procedures

- **Enter Daily Trim:** Recording daily trimmer work sessions and weights
- **Edit Daily Trim:** Correcting or updating existing trim records
- **Edit Trim Rates:** Managing pay rates per strain
- **Edit Trimmer List:** Adding or removing trimmers from the system
