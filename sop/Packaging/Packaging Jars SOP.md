# Packaging Jars SOP

## Section 1 — Packaging Flower in 3.5 g Jars

### 1. Purpose

To define the standardized procedure for packaging trimmed flower into 3.5 gram retail jars, applying compliant product labeling, generating Metrc Processing Package UIDs and Retail Item IDs, and preparing finished goods for wholesale distribution.

### 2. Inputs

- Trimmed flower package UID(s) – **Processing license**
- Blank 3.5 g glass jars and caps
- Boveda humidity packs
- Generic strain labels
- NYS required information labels
- Tamper seals
- Internal identification labels (strain + Processing UID)
- Metrc Retail Item ID labels (QR codes)
- Metrc Distribution Tags
- 4BARCODE label printer
- Labeling machine
- Ohaus Scout scale

### 3. Responsibilities

- **Packaging Technician:** Perform jar filling, labeling, sealing, and case preparation.
- **Administrator (Packaging Menu):** Generate Processing Package UIDs, Retail Item IDs, and Distribution Tags in Metrc.
- **Compliance Manager:** Verify packaging occurs only from batches marked **Tested – Passed**.

---

### 4. Procedure

#### 4.1 Label Preparation

1. Log into Metrc under the **Processing license**.
2. Navigate to: **Processing → Packages → Create Package**.
3. Create a new Processing Package UID for the trimmed flower container being packaged.
4. Print Internal identification labels containing:
    - Strain name
    - Processing Package UID

---

#### 4.2 Prepare Jars

1. Remove blank jars from the case.
2. Use the labeling machine to affix the **generic strain label** to each jar.
3. Remove jar caps.
4. Insert one **Boveda pack** into each jar.
5. Move all prepared jars to the weighing station.

---

#### 4.3 Weigh Flower

1. Place a clean container on the scale and **tare**.
2. Add trimmed flower until the scale reads **3.5 grams**.
3. Empty the container into an empty jar.
4. Replace the jar cap securely.
5. Repeat until all jars are filled.

---

#### 4.4 Finalize Jar Labeling

1. Affix the **NYS required information label** to each jar over the blank area in the generic label.
2. Apply a **tamper seal** to each jar.
3. Place finished jars into the case.

---

#### 4.5 Case Handling

1. When the **first case** for a Processing Package UID is full:
    - Affix the **Processing Package UID label** to the case.
    - Affix the **internal identification label** to the case.
2. For all **subsequent cases** from the same Processing Package UID:
    - Affix the **internal identification label only**.
3. To print internal lables, go to Add Package from the Packaging menu:
    - Select Crop and Strain
    - The system will list the packages for this Crop/Strain
    - Select Package Type (Jars)
    - Select Case No (New)
    - If there are one or more cases for this Crop/Strain/Jars, the system will automatically insert the MetrcID.  If this is the first case, scan the Processing Package UID label.  The ID will show in the MetrcID box.
    - Enter the number of jars in the case
    - Click on Save
    - The system will update the list of packages; the new package should show in the list
    - Click on the row containing the new package
    - Click on Print Lable
    - The system will generate the internal label


---

#### 4.6 Order Fulfillment and Retail UID Assignment

When an order is received:

1. For each case in the order:
    1. Transfer the required number of jars to distribution in Metrc.
    2. Create the **Retail Item IDs** in Metrc for the jars being shipped.
    3. Print the Retail Item ID QR labels.
    4. Affix one **Retail Item ID label** to the cap of each jar.
    5. Affix one **Distribution Tag UID** to the outside of the case.
    6. Affix the **internal identification label** to the case to identify the contents.

---

#### 4.7 Handling Leftover Material

1. When packaging is complete, any remaining Smalls, Trim and Loose Flower must be transferred to hash processing.

2. In Metrc navigate to: **Processing → Packages → Create Package**.
3. For leftover material:
    - **Source Package:** Select the trimmed flower Processing Package UID.
    - **Item:** *Extraction Input – Flower Leftovers*.
    - **Quantity:** Enter the exact remaining weight.
    - **Count:** `1`.
    - **Package Tag UID:** Use a new Processing-license tag.
4. Save the package.

**Compliance Check**

- No leftover flower may remain unassigned to a Metrc package.

---

### 5. Quality & Compliance Checks

1. All source flower packages must be marked **Tested – Passed** before packaging.
2. Each jar must have:
    - Generic strain label
    - NYS required information label
    - Tamper seal
    - Retail Item ID label applied prior to shipment
3. No Metrc Package UIDs shall be printed on consumer jars.
4. Unused jars with generic labels affixed must have the label removed or defaced.
5. Unused generic strain labels not affixed to jars may be disposed of as ordinary waste.

---

### 6. Records

- Metrc Processing Package creation logs
- Retail Item ID print logs
- Distribution Tag assignment logs
- Packaging date and batch records
