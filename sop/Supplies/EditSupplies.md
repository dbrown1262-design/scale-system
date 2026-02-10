# Edit Supplies SOP

## 1. Purpose

To define the standardized procedure for managing supply records, vendor information, and department classifications in the supplies management system. This ensures accurate inventory tracking, proper vendor relationships, and organized departmental categorization for all supply-related operations.

---

## 2. Inputs

- Supabase Web App
- supplies table (Vendor, Dept, Descr, Size)
- suppliesvendors table (VendorName, Status)
- suppliesdept table (Dept)
- Vendor information
- Department classifications
- Supply item descriptions and sizes

---

## 3. Responsibilities

- **Administrator:** Manage supply records, vendors, and department classifications; ensure data accuracy and consistency.
- **Inventory Manager:** Provide accurate supply descriptions, sizes, and vendor assignments.
- **Department Managers:** Define and approve department classifications for supply categorization.

---

## 4. Procedure

### 4.1 Access Edit Supplies Application

1. From the Main Menu, navigate to the **Supplies** section.
2. Click **Edit Supplies** to launch the supply management application.
3. The application displays three sections:
	- Add Supply Item
	- Add Vendor
	- Add Department

---

### 4.2 Add a New Supply Item

**When to Add a Supply Item:**

- When a new product needs to be tracked in inventory
- Before ordering supplies that are not yet in the system
- When expanding product offerings or supply categories

**Steps:**

1. In the **Add Supply Item** section, select the **Vendor** from the dropdown.
	- The dropdown lists all active vendors from the suppliesvendors table.
	- If the vendor is not listed, add them first using the Add Vendor section (see 4.3).
2. Select the **Dept** (Department) from the dropdown.
	- The dropdown lists all departments from the suppliesdept table.
	- If the department is not listed, add it first using the Add Department section (see 4.4).
3. Enter the **Description** in the Description field.
	- Provide a clear, concise description of the supply item.
	- Use consistent naming conventions for similar items.
	- Example: "Airtight Glass Jar", "Nitrile Gloves", "Label Stock"
4. Enter the **Size** in the Size field.
	- Specify the size, capacity, or unit measurement.
	- Include units where applicable (oz, ml, grams, count, etc.).
	- Examples: "16 oz", "100 count", "4x6 inches"
5. Click **Add Supply** to insert the new supply record.
6. The system will:
	- Validate that all required fields are filled.
	- Insert the supply item into the supplies table.
	- Display a success message confirming the addition.
	- Clear the Description and Size fields for the next entry.

**Verification:**

- Confirm the success message displays the correct item description.
- Verify the supply item appears in other applications' supply selection lists.
- Check that Vendor and Department assignments are correct.

---

### 4.3 Add a New Vendor

**When to Add a Vendor:**

- Before adding supply items from a new supplier
- When establishing a new vendor relationship
- When setting up the system for the first time

**Steps:**

1. In the **Add Vendor** section, enter the **Vendor Name** in the text field.
	- Use the vendor's official business name.
	- Ensure consistent capitalization and spelling.
	- Example: "ABC Supply Company", "West Coast Distributors"
2. Click **Add Vendor** to insert the new vendor record.
3. The system will:
	- Validate that the vendor name is not empty.
	- Insert the vendor into the suppliesvendors table.
	- Set the vendor status to "Active" automatically.
	- Display a success message.
	- Clear the Vendor Name field.
	- Refresh the Vendor dropdown in the Add Supply Item section.

**Verification:**

- Confirm the new vendor appears in the Vendor dropdown.
- Verify the vendor name is spelled correctly.
- Check that the vendor is immediately available for adding supply items.

**Best Practices:**

- Establish vendor accounts before ordering or receiving supplies.
- Use consistent naming (e.g., always use full business names, not abbreviations).
- Coordinate with purchasing department on approved vendor list.

---

### 4.4 Add a New Department

**When to Add a Department:**

- When establishing a new department classification
- Before categorizing supplies for a new operational area
- When setting up the system for the first time

**Steps:**

1. In the **Add Department** section, enter the **Department Name** in the text field.
	- Use standard department naming conventions.
	- Keep names concise but descriptive.
	- Examples: "Cultivation", "Packaging", "Processing", "Trimming", "Laboratory"
2. Click **Add Department** to insert the new department record.
3. The system will:
	- Validate that the department name is not empty.
	- Insert the department into the suppliesdept table.
	- Display a success message.
	- Clear the Department Name field.
	- Refresh the Dept dropdown in the Add Supply Item section.

**Verification:**

- Confirm the new department appears in the Dept dropdown.
- Verify the department name follows organizational naming standards.
- Check that the department is immediately available for supply categorization.

**Best Practices:**

- Coordinate department names with organizational structure.
- Use consistent capitalization (e.g., "Cultivation" not "cultivation").
- Avoid creating duplicate departments with slightly different names.
- Establish department list before bulk supply entry.

---

### 4.5 Data Validation

The Edit Supplies application performs the following validations:

**Supply Item Validation:**

- Vendor must be selected (cannot be "Select").
- Department must be selected (cannot be "Select").
- Description field is required and cannot be empty.
- Size field is required and cannot be empty.

**Vendor Validation:**

- Vendor Name is required and cannot be empty.
- New vendors are automatically set to "Active" status.

**Department Validation:**

- Department Name is required and cannot be empty.

**Error Handling:**

- If validation fails, a warning message will appear explaining the missing information.
- Review the error message and correct the input.
- Use the **Refresh** button to reload vendor and department lists if needed.
- Contact the administrator if database errors occur.

---

### 4.6 Workflow Recommendations

**Recommended Setup Order:**

1. **First:** Add all necessary departments (Cultivation, Processing, Packaging, etc.).
2. **Second:** Add all vendors from approved vendor list.
3. **Third:** Add supply items, categorizing by vendor and department.

**For Ongoing Operations:**

- Add new vendors as vendor relationships are established.
- Add new departments only when organizational structure changes.
- Add supply items as new products are introduced.

**Data Consistency:**

- Review existing vendors and departments before adding duplicates.
- Use the Refresh button to ensure dropdown lists are current.
- Coordinate with other users to maintain naming consistency.

---

## 5. Quality & Compliance Checks

- All supply items must have valid vendor and department assignments.
- Vendor names must be accurate and match official business records.
- Department classifications must align with organizational structure.
- Supply descriptions should be clear and searchable.
- Size specifications must include appropriate units of measurement.
- Duplicate entries should be avoided; verify items don't already exist before adding.
- Changes to vendor or department lists should be coordinated with management.

---

## 6. Records

- Supabase supplies table entries
- Supabase suppliesvendors table entries
- Supabase suppliesdept table entries
- Supply item creation timestamps (maintained by Supabase)
- Vendor relationship documentation
- Department classification history

---

## 7. Related Procedures

- **Order Supplies SOP:** Uses vendor and supply item data for ordering
- **Receive Supplies SOP:** References supply items for inventory tracking
- **Inventory Management SOP:** Queries supply records for stock levels
- **Department Budget Tracking:** Uses department classifications for expense allocation
