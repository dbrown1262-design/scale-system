# Edit Daily Trim SOP

## 1. Purpose

To define the standardized procedure for viewing, editing, and correcting daily trim records in the database. This ensures accurate record-keeping of trim production data, including weights, start/end times, and trimmer performance tracking.

---

## 2. Inputs

- Supabase Web App
- dailytrim table
- Trimmer selection list
- Date filter
- AM/PM shift filter

---

## 3. Responsibilities

- **Harvest/Trim Manager:** Review and edit daily trim records for accuracy.
- **Trimmer Lead:** Verify trim weights and shift times before final record approval.
- **Administrator (Admin Menu):** Monitor data integrity and resolve discrepancies.

---

## 4. Procedure

### 4.1 Launch the Daily Trim Editor

1. From the main menu, navigate to Trimmers → Edit Daily Trim.
2. The DailyTrim Viewer/Editor window will open.

---

### 4.2 Filter and Load Trim Records

The application allows filtering by trimmer, date, and shift (AM/PM).

**Set Filter Parameters**

1. **Trim Date:** Select the starting date using the date picker. The system will load 7 days of data starting from this date.
2. **Trimmer:** Choose a trimmer name from the dropdown menu. Selection is required before loading data.
3. **AM/PM:** (Optional) Select "Morning", "Afternoon", or leave blank to view all shifts.
4. Click the **Load** button.

**Data Display**

The system queries the dailytrim table and displays matching records in a grid showing:

- Trimmer Name
- Trim Date
- Crop Number
- Strain
- Trim Type
- AM/PM Shift
- Grams
- Start Time
- End Time

Records are sorted by date, trimmer name, and strain.

---

### 4.3 Select and Edit a Trim Record

**Select a Row**

1. Click on any row in the grid to select it.
2. The selected record details will appear in the information banner below the grid.
3. The editable fields (Grams, Start Time, End Time) will populate in the editor controls at the bottom of the window.

**Edit Fields**

The following fields can be modified:

1. **Grams:** Enter the corrected weight value (numeric only).
2. **Start Time:** Select the shift start time from the dropdown (8:00 AM to 5:00 PM in 15-minute intervals).
3. **End Time:** Select the shift end time from the dropdown (8:00 AM to 5:00 PM in 15-minute intervals).

**Save Changes**

1. After editing the fields, click the **Save** button.
2. The system will:
	- Validate that Grams is numeric.
	- Convert time labels to database format.
	- Update the dailytrim table based on the unique record key (TrimmerName, TrimDate, CropNo, Strain, TrimType, AmPm).
3. A status message will confirm the update.
4. The grid will automatically reload to reflect the changes.

**Clear Selection**

- Click the **Clear** button to deselect the current record and reset the editor fields.

---

### 4.4 Verify Changes

After saving:

1. Verify the updated values appear correctly in the grid.
2. Cross-check that the Grams, Start Time, and End Time match the intended corrections.
3. If additional records require editing, repeat steps 4.3.

---

## 5. Quality & Compliance Checks

- All trim weights must be numeric and non-negative.
- Start times must precede end times for valid shift tracking.
- Any discrepancies between physical trim weights and recorded data must be investigated and documented.
- Records should be updated within 24 hours of the trim date to maintain data accuracy.

---

## 6. Records

- Supabase dailytrim table
- Updated trim weight and shift time records
- Filter parameters used (trimmer, date range, shift)
