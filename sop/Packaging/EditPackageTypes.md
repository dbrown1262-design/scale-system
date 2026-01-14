# Edit Package Types SOP

## 1. Purpose

To define the standardized procedure for creating, viewing, and editing package type definitions in the database. This ensures accurate tracking of package configurations, unit weights, and inventory management for cannabis product packaging operations.

---

## 2. Inputs

- Supabase Web App
- packagetypes table
- Package type names
- Unit weight values (in grams)

---

## 3. Responsibilities

- **Packaging Manager:** Create and maintain package type definitions for all packaging configurations used in the facility.
- **Inventory Manager:** Verify unit weights match physical packaging specifications.
- **Administrator (Admin Menu):** Monitor package type list accuracy and resolve discrepancies.

---

## 4. Procedure

### 4.1 Launch the Package Types Editor

1. From the main menu, navigate to Packaging → Edit Package Types.
2. The Edit Package Types window will open.
3. The system automatically loads all existing package types from the packagetypes table.

---

### 4.2 View Package Types

**Data Display**

The grid displays all package types with the following columns:

- **TypeName:** The name of the package type (e.g., "1g Jar", "3.5g Jar", "7g Bag").
- **UnitWeight:** The weight of the empty package in grams.

**Refresh Data**

- Click the **Refresh** button to reload the latest data from the database.

---

### 4.3 Add a New Package Type

**Enter New Package Information**

1. In the form fields at the bottom of the window, enter:
	- **Type Name:** The descriptive name for the package type (e.g., "14g Mylar Bag").
	- **Unit Weight:** The weight of the empty package in grams (e.g., 2.5).

**Validation**

- Type Name is required and cannot be blank.
- Unit Weight must be a valid numeric value. If left blank, it defaults to 0.0.

**Save New Package Type**

1. Click the **Add Row** button.
2. The system will:
	- Validate the input fields.
	- Insert a new record into the packagetypes table.
	- Refresh the grid to display the new package type.
	- Display a status message confirming the insertion.

---

### 4.4 Edit an Existing Package Type

**Select a Package Type**

1. Click on any row in the grid to select it.
2. The selected package type's values will populate the form fields at the bottom.
3. A status message will display the selected row ID.

**Modify Package Information**

1. Update the **Type Name** or **Unit Weight** fields as needed.
2. Verify the values are correct.

**Save Changes**

1. Click the **Update Selected** button.
2. The system will:
	- Validate that a row is selected and input values are valid.
	- Update the packagetypes table for the selected record ID.
	- Refresh the grid to display the updated values.
	- Display a status message confirming the update.

---

### 4.5 Clear the Form

- Click the **Clear** button to deselect the current row and reset the form fields.
- This allows you to enter a new package type without interference from previously selected data.

---

## 5. Quality & Compliance Checks

- All package types must have a unique, descriptive Type Name.
- Unit Weight values must be accurate to ensure proper net weight calculations.
- Unit Weight should be measured using a calibrated scale for each package type.
- Package types should match the physical inventory of packaging materials available in the facility.
- Obsolete or discontinued package types should be verified before removal to prevent data integrity issues.

---

## 6. Records

- Supabase packagetypes table
- Package type names and unit weights
- Insert and update timestamps (if applicable)
