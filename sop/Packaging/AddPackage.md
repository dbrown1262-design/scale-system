# Add Package — Packaging Entry Application SOP

## 1. Purpose

To standardize the process for entering packaging activity data into the system, including crop, strain, package type, Metrc ID tracking, and quantity management.

---

## 2. Required Equipment

- Handheld QR code scanner
- Add Package application (Packaging menu)
- 4BARCODE label printer (for label printing)
- Metrc package tags

---

## 3. Operating the Application

1. Open the Packaging menu.
2. Select **Add Package**.
3. Check the status indicator in the upper right:
	- **QR: Connected** (green) — scanner is ready.
	- **QR: Not Found** (red) — turn on scanner and press trigger.

---

## 4. Entering Package Data

### 4.1 Select Crop and Strain

1. Select the **Crop** from the dropdown menu.
	- Crops are loaded from the scalecrops table.
	- Format: "CropNo - HarvestDate"
2. Select the **Strain** from the dropdown menu.
	- Strains are filtered based on the selected crop.
	- The package list will automatically update to show existing packages for this crop/strain.

---

### 4.2 Select Package Type

1. Select the **Type** from the dropdown menu:
	- **Flower** — trimmed flower buds
	- **Jars** — packaged jars ready for retail
	- **PreRolls** — pre-rolled joints
	- **Trim** — leaf material from trimming
	- **Hash** — hash products
	- **Rosin** — rosin products
2. When a type is selected:
	- The system loads available cases for this crop/strain/type combination.
	- If a Metrc ID exists for this type, it will auto-populate in the Metrc ID field.

---

### 4.3 Select Case Number

1. Select the **Case No** from the dropdown menu:
	- **New Case:** Select "New" to create a new case.
		- The system will automatically assign the next sequential case number.
	- **Existing Case:** Select an existing case number to add units to that case.
	- Cases are specific packaging batches within a type.
	- Format may include the associated Metrc ID: "CaseNo (MetrcID)"
2. When a case is selected:
	- If the case has an associated Metrc ID, it will auto-populate in the Metrc ID field.

---

### 4.4 Enter or Scan Metrc ID

**Using QR Scanner (Recommended)**

1. Position the QR scanner over the Metrc Package Tag UID barcode.
2. Press the scanner trigger.
3. The Metrc ID will automatically populate in the **Metrc ID** field.

**Manual Entry**

1. Click in the **Metrc ID** field.
2. Type the Metrc Package Tag UID number.
3. Press **Enter** or click elsewhere to confirm.

---

### 4.5 Enter Quantity

1. Click in the **Quantity** field.
2. Enter the number of units being packaged.
3. The system will calculate total weight based on:
	- Package type unit weight (from packagetypes table)
	- Quantity entered

---

### 4.6 Save Package Entry

1. Click **Save** to record the package.
2. The system will:
	- Retrieve the harvest date for the crop
	- Calculate total weight: `Quantity × UnitWeight`
	- Insert the package record with:
		- Crop number
		- Strain
		- Case number
		- Metrc ID
		- Package type
		- Quantity (number of units)
		- Total weight
		- Package date (today's date)
3. The package list will refresh to show the new entry.
4. A status message will confirm the save.

---

## 5. Viewing Existing Packages

The table at the bottom of the window displays all packages for the selected crop and strain:

**Columns:**
- **Crop** — Crop number
- **Strain** — Strain name
- **Type** — Package type (Flower, Jars, etc.)
- **Case** — Case number
- **MetrcID** — Metrc Package Tag UID
- **Units** — Number of units/packages
- **Weight** — Total weight in grams
- **PackDate** — Date package was created

**Totals Row:**
- The last row shows totals for Units and Weight columns.
- This row is highlighted in blue.

---

## 6. Printing Package Labels

After saving a package, you can print a label:

1. Select the package from the table (click on the row).
2. Click **Print Label**.
3. The system will:
	- Retrieve the package details from the database
	- Generate a PDF label with:
		- Strain name
		- Package type
		- Harvest date
		- Metrc ID
		- Weight in grams
		- Company name
4. The label will be sent to the printer.

> **Note:** Ensure the 4BARCODE printer is set as the default printer and has label stock loaded.

---

## 7. Case Handling Workflow

### 7.1 Processing Package UID and Case Labeling

When packaging products (such as jars), follow this case handling procedure:

1. When the **first case** for a Processing Package UID is full:
	- Affix the **Processing Package UID label** to the case.
	- Affix the **internal identification label** to the case.

2. For all **subsequent cases** from the same Processing Package UID:
	- Affix the **internal identification label only**.

### 7.2 Printing Internal Labels for Cases

To print internal labels for any package type:

1. Select **Crop** and **Strain**.
2. Select **Package Type** (e.g., "Jars", "Flower", "PreRolls").
3. Select **Case No** (or "New" for a new case).
4. **Metrc ID Handling:**
	- For subsequent cases: The Metrc ID auto-populates from existing packages.
	- For the first case: Scan the Processing Package UID label.
5. Enter the **Quantity** (number of units in the case).
6. Click **Save**.
7. Click on the new package row in the table.
8. Click **Print Label** to generate the internal identification label.

> **Note:** See specific packaging SOPs (e.g., Packaging Jars SOP) for detailed case handling procedures for each product type.

---

## 8. Refreshing Lists

If new crops or strains have been added to the database:

1. Click **Refresh Lists**.
2. The Crop dropdown will reload with the latest data.
3. All downstream selections (Strain, Type, Case) will reset to "Select".

---

## 9. Troubleshooting

### QR Scanner Not Working

- Verify the scanner is powered on.
- Check that the QR status shows **QR: Connected** (green).
- Press the trigger on the scanner to activate it.
- If scanning fails, manually enter the Metrc ID.

### Case Dropdown is Empty

- Verify that Crop, Strain, and Type are all selected.
- Cases are created when packages are first entered for a type.
- If no cases exist yet, the dropdown will show "Select" only.

### Metrc ID Not Auto-Populating

- Metrc IDs are only auto-populated if previously saved for this type/case.
- For new types or cases, you must scan or manually enter the Metrc ID.

### Save Button Does Nothing

- Verify all required fields are populated:
	- Crop (cannot be "Select")
	- Strain (cannot be "Select")
	- Type (cannot be "Select")
	- Case No (cannot be "Select")
	- Metrc ID (must have a value)
	- Quantity (must be a positive number)
- Check the status message for error details.

### Total Weight is Incorrect

- Total weight is calculated as: `Quantity × UnitWeight`
- Unit weights are defined in the packagetypes table.
- Use **Edit Package Types** (Packaging menu) to verify/update unit weights.

### Label Won't Print

- Verify the package exists in the database (visible in the table).
- Check that the printer is powered on and connected.
- Verify the C:\labels\ folder exists and is accessible.
- Ensure the 4BARCODE printer is selected as default.

---

## 10. Best Practices

- Always scan Metrc IDs when possible to avoid manual entry errors.
- Verify the QR scanner status is green before beginning package entry.
- Double-check Crop, Strain, and Type selections before saving.
- Use the package list to verify entries were saved correctly.
- Print labels immediately after package entry for proper identification.
- Keep Metrc Package Tags organized and ensure they match the physical packages.

---

## 11. Data Flow

1. **Input Sources:**
	- Crop/Strain: scalecrops and scaleplants tables
	- Case Numbers: Generated or retrieved from existing packages
	- Metrc IDs: Scanned from physical Metrc tags or manual entry
	- Unit Weights: packagetypes table

2. **Calculation:**
	- Total Weight = Quantity × UnitWeight (from packagetypes)

3. **Output:**
	- Package record saved to packages table
	- Includes: CropNo, Strain, CaseNo, MetrcID, PackageType, TotUnits, TotWeight, PackDate

4. **Metrc Compliance:**
	- Each package must have a unique Metrc Package Tag UID
	- Package records support compliance reporting and inventory tracking
