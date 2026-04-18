# Edit Crops SOP

## 1. Purpose

To define the standardized procedure for managing crop records in the scalecrops table, including adding new crops and updating harvest dates and crop status. This ensures accurate crop tracking, proper lifecycle management, and compliance throughout all harvest and post-harvest operations.

---

## 2. Inputs

- Supabase Web App
- scalecrops table
- Harvest date information
- Crop status (Active/Inactive)

---

## 3. Responsibilities

- **Administrator:** Manage crop records, including creating new crops and updating existing crop information.
- **Harvest Manager:** Provide accurate harvest dates and approve crop status changes.

---

## 4. Procedure

### 4.1 Access Edit Crops Application

1. From the Main Menu, navigate to the **Harvest** section.
2. Click **Edit Crops** to launch the crop management application.
3. The application displays all existing crops (both Active and Inactive) in the crop selection dropdown.

---

### 4.2 Add a New Crop

**When to Add a New Crop:**

- Before importing plant data from Bamboo
- When starting a new harvest cycle
- When preparing for a new cultivation batch

**Steps:**

1. In the **Crop** dropdown, select **New Crop**.
2. The application will:
	- Clear the Harvest Date field.
	- Set Crop Status to "Active" by default.
	- Enable the **Insert** button.
	- Disable the **Update** button.
3. Enter the **Harvest Date** in YYYY-MM-DD format (e.g., 2026-01-20).
4. Verify or change the **Crop Status** if needed (typically remains "Active" for new crops).
5. Click **Insert** to create the new crop record.
6. The system will:
	- Automatically assign the next sequential crop number.
	- Insert the crop into the scalecrops table.
	- Display a success message with the new crop number.
	- Refresh the crop list to include the new entry.

**Verification:**

- Confirm the new crop appears in the dropdown list.
- Verify the crop number, harvest date, and status are correct.

---

### 4.3 Edit an Existing Crop

**When to Edit a Crop:**

- To update or correct a harvest date
- To change crop status from Active to Inactive (or vice versa)
- To make administrative corrections to crop records

**Steps:**

1. In the **Crop** dropdown, select the crop you want to edit.
	- The dropdown displays crops in the format: "CropNo - HarvestDate (Status)"
	- Example: "19 - 2025-11-15 (Active)"
2. The application will:
	- Load the crop's current harvest date and status.
	- Populate the Harvest Date field.
	- Set the Crop Status dropdown to the current status.
	- Enable the **Update** button.
	- Disable the **Insert** button.
3. Modify the **Harvest Date** or **Crop Status** as needed.
	- Harvest Date must be in YYYY-MM-DD format.
	- Crop Status options are: Active or Inactive.
4. Click **Update** to save the changes.
5. The system will:
	- Update the crop record in the scalecrops table.
	- Display a success message.
	- Refresh the crop list to reflect the changes.

**Verification:**

- Confirm the updated information appears correctly in the dropdown list.
- If changing status to Inactive, verify the crop no longer appears in other application crop lists.

---

### 4.4 Crop Status Management

**Active Status:**

- Crop is currently in use or planned for upcoming harvest operations.
- Appears in crop selection lists throughout the application (Print Plant Tags, Weigh Plants, etc.).
- Should be used for all current and planned harvest cycles.

**Inactive Status:**

- Crop has been completed and archived.
- Does not appear in standard crop selection lists (only visible in Edit Crops).
- Used for historical record-keeping and compliance.

**Best Practices:**

- Set crops to "Inactive" after all harvest and post-harvest operations are complete.
- Never delete crop records; use Inactive status instead.
- Review and update crop status regularly to keep active crop lists clean and relevant.

---

### 4.5 Data Validation

The Edit Crops application performs the following validations:

**Date Format:**

- Harvest Date must be in YYYY-MM-DD format.
- Invalid dates will trigger a warning message.
- Enter dates carefully to ensure accuracy.

**Required Fields:**

- Harvest Date is required for both new crops and updates.
- Crop Status must be either Active or Inactive.

**Error Handling:**

- If validation fails, review the error message and correct the input.
- Use the **Refresh** button to reload the crop list if needed.
- Contact the administrator if database errors occur.

---

## 5. Quality & Compliance Checks

- All new crops must have a valid harvest date before plant data can be imported.
- Crop numbers are assigned sequentially and must not be duplicated.
- Active crops should reflect only current and planned harvest cycles.
- Inactive crops must retain all historical data for compliance and auditing.
- Changes to harvest dates should be documented and approved by the Harvest Manager.

---

## 6. Records

- Supabase scalecrops table entries
- Crop creation timestamps
- Crop modification history (maintained by Supabase)
- Harvest date documentation

---

## 7. Related Procedures

- **Print Plant Tags SOP:** Requires active crops with valid harvest dates
- **Weigh Plants SOP:** Uses active crop data for harvest tracking
- **Plant Weights Summary SOP:** Queries crop records for reporting

---

## Section 10 — Revision History

Revision: 1  
Effective Date: 2026-04-09  
Approved By: President/CEO

Change Summary:  
Rev 1 – Initial release
