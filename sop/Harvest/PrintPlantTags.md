# Print Plant Tags SOP

## 1. Purpose

To define the standardized procedure for receiving plant data, printing plant identification tags, and properly tagging plants prior to harvest. This ensures compliance, traceability, and accurate crop tracking throughout the harvest workflow.

---

## 2. Inputs

- Bamboo plant export (CSV)
- Supabase Web App
- scalecrops table
- scaleplants table
- 4BARCODE label printer
- 2.25" × 0.75" label stock
- Pre-numbered plant tags from Metric

---

## 3. Responsibilities

- **Harvest Technician:** Perform tag printing and plant tagging.
- **Administrator (Admin Menu):** Verify crop setup, ensure correct printer settings, and approve tag printing.

---

## 4. Procedure

### 4.1 Import Plants From Bamboo Into Supabase

1. Open the Supabase web application.
2. Import new plant data from Bamboo:
	- Add a new Harvest Number and Harvest Date to the scalecrops table.
	- Import the CSV file exported from Bamboo into the scaleplants table.
3. Confirm all rows were imported successfully and that each plant has a strain, plant ID, and associated crop number.

---

### 4.2 Print Strain Name Labels (Admin Menu)

The new tagging system uses pre-numbered tags purchased from Metric. The Print Plant Tags application prints strain name labels to affix to the back of each Metric tag.

Before printing, verify system and printer configuration:

#### 4.2.1 Operating the Weighing Application

{{ include Modules/LabelPrinterPlantSetup.md }}

**Print Production Labels**

1. Select the correct Crop Number.
2. For each strain in the crop:
	- Select the strain.
	- The system automatically queries scaleplants table and displays the plant count.
	- Verify or adjust the "Number of Labels" field as needed.
	- Click Print Tags.
	- Verify that the correct number of strain name labels have been printed.

---

### 4.3 Label Plants

**Prepare Tags**

1. Locate the pre-numbered plant tags from Metric.
2. Affix one printed strain name label to the back of each Metric tag.

**Apply Tags to Plants**

1. Apply one numbered Metric tag to each plant:
	- Attach the tag to the plant stem above the first branch.
	- Ensure the tag is secure and will not fall off during harvest.
	- Verify the Metric number on the front is visible.
	- Verify the strain name label on the back is secure.

**Verification**

Confirm that every plant is labeled before proceeding to harvest.

---

### 4.4 Register Plant Tags in Metrc

1. After physical plant tags have been affixed, log into Metrc.
2. Navigate to: **Grow → Immature / Vegetative / Flowering Plants → Add Plants**.
3. For each strain group:
	1. Enter the assigned Metrc Plant Tag UID numbers.
	2. Verify that the plant count in Metrc matches the number of physical tags applied.
4. Save the entries.

**Compliance Check**

- The number of plants in Metrc must equal the number of physically tagged plants before harvest may proceed.

---

## 5. Quality & Compliance Checks

- All plants in the crop must have a readable, affixed Metric tag with strain name label prior to harvest.
- Tag count should match the number of plants imported from Bamboo.
- Damaged or unreadable strain labels must be reprinted immediately.

---

## 6. Records

- Bamboo export CSV
- Supabase scalecrops entry
- Supabase scaleplants import
- Label print logs (if applicable)
