# Edit Trim Rates SOP

## 1. Purpose

To define the standardized procedure for viewing and editing BigsRate values for strains within a crop. This ensures accurate calculation of trimmer compensation based on strain-specific processing difficulty and quality standards.

---

## 2. Inputs

- Supabase Web App
- trimrates table
- scalecrops table
- Crop selection list
- Strain names from selected crop

---

## 3. Responsibilities

- **Harvest/Trim Manager:** Set and adjust BigsRate values for each strain based on trim difficulty and processing standards.
- **Administrator (Admin Menu):** Monitor rate consistency and approve rate changes for payroll calculations.

---

## 4. Procedure

### 4.1 Launch the Trim Rates Editor

1. From the main menu, navigate to Trimmers → Edit Trim Rates.
2. The Edit Trim Rates window will open.

---

### 4.2 Select a Crop

**Choose Crop**

1. In the Crop dropdown at the top of the window, select the desired crop.
	- Crops are displayed in the format: "CropNo - HarvestDate" (e.g., "19 - 2023-04-12").
2. Click the **Ensure & Load** button.

**System Actions**

The application will:

1. Query the trimrates table for all strains in the selected crop.
2. For any strain that does not have an existing trim rate record, automatically insert a default BigsRate of **0.36**.
3. Load all strain names and their current BigsRate values into the grid.

**Data Display**

The grid displays two columns:

- **Strain:** The strain name.
- **BigsRate:** The current BigsRate value (displayed to 4 decimal places).

Strains are sorted alphabetically.

---

### 4.3 Edit a BigsRate

**Select a Strain**

1. Locate the strain you wish to edit in the grid.
2. Double-click the row to load it into the edit fields at the bottom of the window.

**Edit Fields**

The edit section displays:

- **Strain:** (read-only) The selected strain name.
- **BigsRate:** (editable) The current BigsRate value.

**Update the Rate**

1. Modify the BigsRate value as needed.
	- BigsRate must be a valid decimal number (e.g., 0.40, 0.36, 0.32).
	- Common rates range from 0.30 to 0.50 depending on strain difficulty.
2. Click the **Update** button.

**System Actions**

The application will:

1. Validate that BigsRate is a numeric value.
2. Update the trimrates table for the selected CropNo and Strain.
3. Refresh the grid to display the updated rate.
4. Display a status message confirming the update (e.g., "Updated Strain X to 0.4000").

---

### 4.4 Verify Changes

After updating:

1. Confirm the updated BigsRate value appears correctly in the grid.
2. If additional strains require rate adjustments, repeat step 4.3.

---

## 5. Quality & Compliance Checks

- BigsRate values must be numeric and positive.
- Default BigsRate of 0.36 is automatically assigned to new strains until manually adjusted.
- Rate changes should be documented and communicated to payroll personnel.
- BigsRate should reflect the relative difficulty of trimming each strain to ensure fair compensation.
- All strains in a crop must have a BigsRate entry before trimmer compensation can be calculated.

---

## 6. Records

- Supabase trimrates table
- Updated BigsRate values by CropNo and Strain
- Crop selection and strain list used
