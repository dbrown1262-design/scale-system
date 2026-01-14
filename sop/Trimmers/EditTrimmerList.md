# Edit Trimmer List SOP

## 1. Purpose

To define the standardized procedure for managing the trimmer roster in the system. This includes adding new trimmers, updating existing trimmer information, and changing trimmer status (Active/Inactive) to maintain an accurate and current list of personnel authorized to perform trimming operations.

---

## 2. Inputs

- Supabase trimmers table (id, TrimmerName, TrimmerStat)
- Personnel roster and hiring records
- HR status updates (active/inactive employees)

---

## 3. Responsibilities

- **Administrator (Admin Menu):** Maintain the trimmer list, add new employees, and update status changes.
- **HR Manager:** Provide notification of new hires and terminations requiring trimmer roster updates.
- **Operations Manager:** Request trimmer additions for newly hired trim room personnel.
- **Payroll Administrator:** Verify trimmer list accuracy before processing payroll.

---

## 4. Procedure

### 4.1 Access the Trimmer List Editor

1. From the Main Menu, select **Admin → Edit Trimmer List**.
2. The Trimmer Maintenance window will open displaying the current trimmer roster.
3. The table shows all trimmers with their ID, Name, and Status (Active/Inactive).

---

### 4.2 View and Filter Trimmer List

**View All Trimmers**

The main table displays three columns:
- **ID:** Unique database identifier for the trimmer record
- **Trimmer Name:** Full name of the trimmer
- **Status:** Current employment status (Active or Inactive)

**Filter by Name**

1. Locate the **Filter by name...** search box in the upper right corner.
2. Type any part of a trimmer's name.
3. The list automatically filters to show only matching names.
	- Non-matching names appear dimmed but remain visible.
4. Clear the filter box to show all trimmers again.

---

### 4.3 Add a New Trimmer

**When to Add a Trimmer:**
- New employee hired for trim room operations
- Seasonal trimmer starting work
- Contractor or temporary worker authorized to trim

**Add Procedure:**

1. Click the **Add New** button.
2. In the form fields at the bottom of the window:
	- **Trimmer Name:** Enter the employee's full name (first and last name).
	- **Status:** Select **Active** from the dropdown (this is the default for new trimmers).
3. Verify the information is correct.
4. Click **Add New** again to confirm.
5. A confirmation message will appear: "New trimmer added."
6. The new trimmer will appear in the table with an automatically assigned ID.
7. The form will clear, ready for another entry if needed.

**Validation:**
- Trimmer Name is required; blank names are not allowed.
- Status must be either "Active" or "Inactive".

---

### 4.4 Edit an Existing Trimmer

**When to Edit:**
- Correct a misspelled name
- Update name after legal name change
- Change status from Active to Inactive (or vice versa)

**Edit Procedure:**

1. Click on the trimmer's row in the table to select it.
2. The form fields will populate with the selected trimmer's information:
	- **Trimmer Name:** Current name on file
	- **Status:** Current status (Active or Inactive)
	- **ID:** Displays the database ID (read-only)
3. Modify the **Trimmer Name** or **Status** as needed.
4. Click **Save Changes**.
5. A confirmation message will appear: "Changes saved."
6. The updated information will display in the table.

**Status Change Guidelines:**

**Set to Inactive when:**
- Trimmer is terminated or quits
- Trimmer transfers to a different department
- Seasonal worker's contract ends
- Trimmer is on extended leave

**Set to Active when:**
- Inactive trimmer returns to work
- Seasonal worker rehired
- Employee transfers back to trim room
- Correcting an erroneous Inactive status

---

### 4.5 Clear the Form

1. Click the **Clear Form** button to reset all form fields.
2. This action:
	- Clears the Trimmer Name field
	- Resets Status to "Active"
	- Deselects any selected row in the table
	- Resets the ID display to "ID: —"
3. Use this when you want to add a new trimmer after viewing or editing another record.

---

### 4.6 Refresh the Data

1. Click the **Refresh** button to reload the trimmer list from the database.
2. Use this to:
	- Verify recent changes saved correctly
	- See updates made by other users
	- Recover from any display issues

---

### 4.7 Close the Application

1. Click the **Close** button to exit the Trimmer Maintenance application.
2. The system will return to the Main Menu.

---

## 5. Quality & Compliance Checks

- **Name Accuracy:** Verify names match official personnel records and payroll documents.
- **Status Consistency:** Ensure Active trimmers are currently employed and authorized to work.
- **Inactive Records:** Confirm all terminated or inactive employees are marked Inactive.
- **Duplicate Prevention:** Check for existing entries before adding new trimmers to avoid duplicates.
- **Regular Audits:** Review trimmer list quarterly to remove obsolete entries and verify status accuracy.
- **Cross-Reference Payroll:** Before processing payroll, verify that all trimmers in timesheets exist in the trimmer list with Active status.

---

## 6. Records

- Supabase trimmers table (master record)
- HR personnel files (supporting documentation)
- Payroll authorization records
- System audit logs (if available)

---

## 7. Troubleshooting

**Problem:** Cannot add a new trimmer - no confirmation message appears

- **Solution:**
  1. Verify that the Trimmer Name field is not blank.
  2. Check for special characters that may cause database errors.
  3. Confirm database connection is active.
  4. Try clicking **Refresh** and attempt to add again.

**Problem:** Changes to trimmer name or status do not save

- **Solution:**
  1. Ensure you selected a row before clicking Save Changes.
  2. Verify that you clicked **Save Changes** button (not Add New).
  3. Check that the ID field shows a valid number (not "ID: —").
  4. Click **Refresh** to verify if changes were actually saved.

**Problem:** Trimmer appears twice in the list

- **Solution:**
  1. Check if one entry is for a different person with the same name.
  2. If duplicate, verify which ID is being used in trim records.
  3. Set the unused duplicate to Inactive status.
  4. Contact administrator to merge or delete duplicate records if necessary.

**Problem:** Inactive trimmer still appears in dropdown lists in other applications

- **Solution:**
  1. Verify the trimmer status was saved as "Inactive".
  2. Close and restart applications using the trimmer list.
  3. Some applications may cache trimmer lists; they will update on next launch.

**Problem:** Filter doesn't show expected trimmers

- **Solution:**
  1. Clear the filter box completely.
  2. Check spelling of search term.
  3. Filter searches name only, not status or ID.
  4. Filtered-out names appear dimmed; scroll to see them.

**Problem:** "Failed to load trimmers" error on startup

- **Solution:**
  1. Verify database connection is active.
  2. Check that Supabase credentials are configured correctly.
  3. Contact administrator to verify trimmers table exists and is accessible.

---

## 8. Data Management Best Practices

- **Never delete trimmer records:** Use Inactive status instead to preserve historical payroll data.
- **Consistent naming:** Use full legal names matching payroll records.
- **Immediate updates:** Change status to Inactive on the employee's last working day.
- **Documentation:** Keep HR documentation supporting status changes.
- **Communication:** Notify payroll and operations managers of trimmer list changes.

---

## 9. Related Procedures

- **Enter Daily Trim:** Recording daily work sessions using active trimmers
- **Edit Daily Trim:** Correcting trim records that reference trimmers
- **Weekly Trimmer Summary:** Generating payroll reports from trimmer data
- **Edit Trim Rates:** Managing pay rates (separate from trimmer roster)
