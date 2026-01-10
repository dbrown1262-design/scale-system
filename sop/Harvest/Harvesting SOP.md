# Harvesting SOP

## Section 1: Harvesting Plants

### 1. Purpose

To outline the standardized procedure for removing plants from the grow room, handling trellis and soil bags, weighing plants, and preparing the grow room for sanitation.

### 2. Procedure

#### 2.1 Harvesting Plants

**Clean the Drying Room**

1. Remove any totes from previous harvests
2. Remove any rolling shelves containing product.
3. Wash walls, sweep and mop floor.
4. Sanidate the room using the compressor and foaming machine

**Remove trellis from plants:**

1. Use scissors to remove as much trellis as possible.
2. Leave enough trellis attached to keep plants upright until they are harvested.
3. Bag used trellis and set aside for disposal.

**Remove fertigation lines:**

1. Remove fertigation tubes from the soil bags prior to cutting plants.

**Cut the plant at the base:**

1. Use lopper shears to cut the plant at the stem base.
2. Verify the plant tag is still attached.
3. Transport the plant to the weighing station (see Section 1.2 below).
4. Remove remaining trellis once the plant is at the weighing station.

**Manage soil bags during harvest:**

1. Move harvested soil bags to the end of the grow table.
2. Remove small fertigation tubes as each plant is processed to keep the work area clear.

##### 2.1.1 When All Plants in Grow Room Are Harvested

1. Remove all remaining trellis from the tables and walkways.
2. Transport used soil bags to the designated storage area.
3. Separate soil from plastic:
    - Empty the soil from the plastic grow bags.
    - Place soil into the dump trailer for transport to the compost pile.

**Clean the grow tables:**

1. Use the shop vac to remove loose debris.
2. Use the pressure washer to clean surfaces thoroughly.

**Sanitize the grow room:**

1. Set up the compressor and Sanidate sprayer.
2. Spray tables, walls, and floors.

---

#### 1.2 Weighing Plants

##### 1.2.1 Set Up the Scale (If Necessary)

1. Place the Ohaus Ranger scale on the rack above the drying room door.
2. Screw the bottom hook into the scale.
3. Hang one stainless steel "S" hook on the bottom hook.
4. Tare the scale to zero.

##### 1.2.2 Operating the Weighing Application

1. Select "Weigh Plants" from the Harvest menu.
2. Confirm Plant Type = "Wet."
3. Since each plant has a unique ID, no crop or strain selection is required.

**Hang the plant:**

1. Place an S hook on a lower branch.
2. Hang the plant upside down from the scale.
    - This same hook will be used to hang the plant in the drying room after weighing.
3. Verify the weight appears in the Weight box on screen.
4. Use the handheld QR reader to scan the plant tag.

The system will:

- Record the weight
- Add a line to the Log box
- Associate the weight with the correct plant ID automatically

##### 1.2.3 If a QR Code Does Not Scan

1. Hang the plant on the scale and verify the weight is displayed.
2. Type the Plant ID manually.
3. Click Process Current Plant.

##### 1.2.4 Duplicate Weighing Warning

If the plant has already been weighed:

- The system will display a warning message with options:
    - Cancel
    - Replace the Existing Weight
- This situation is common when weighing dry plants while the application is still set to Wet mode.

##### 1.2.5 After Weighing

1. Hang the plant in the drying room.
2. Ensure the plant tag remains attached so it can be identified and weighed again after drying.

---

#### 1.3 Create Harvest Batch in Metrc

1. After all plants from a grow room have been harvested and moved to the drying room, log into Metrc.
2. Navigate to: **Grow → Harvests → Create Harvest Batch**.
3. Select all harvested plant tag UIDs for the room and strain.
4. Enter:
    - Harvest Date  
    - Room Name  
    - Strain  
    - Total Wet Weight
5. Save the harvest batch.

**Compliance Check**

- All plant tags must be included in exactly one harvest batch.  
- No plant tag may remain active after harvest.

---

\newpage

## Section 2: Bucking Plants

### 1. Purpose
The bucking process removes flowers from stems following drying. This reduces material volume, prevents moisture retention, and prepares the flowers for trimming. Proper bucking supports product quality, reduces mold risk, and maintains strain separation and traceability.

---

### 2. Bucking Procedure

#### 2.1 Remove Plants From Drying Room
1. Remove plants from the drying room **one strain at a time**.
2. Weigh each plant before bucking (see **Section 2.3 – Weigh Dry Plants**).

#### 2.2 Prepare Branches for Bucking
1. Cut branches off the main stem to make them more manageable.
2. Place branches with flowers on the work table.
3. Place bare stems (no flowers) into a tote for later transport to the compost pile.

#### 2.3 Remove Flowers From Branches
1. Using scissors, cut each flower from the branches.
2. Place flowers into trays.
3. Discard stems once flowers are removed.

#### 2.4 Collecting Bucked Flower
1. Line a 27-gallon tote with a **breathable tote liner**.
2. As trays are filled, empty them into the lined tote.
3. Continue until the entire strain has been bucked.

#### 2.5 Weighing Bucked Flower Bags
1. Seal each liner bag with a zip tie.
2. Weigh each bag (see **Section 2.4 – Weigh Bucked Flower**).
3. Place weighed bags back into the tote and secure the lid.
4. When space permits, return totes to the drying room.

#### 2.6 Sanitation Between Strains
1. Wash scissors with isopropyl alcohol.
2. Clean trays and tables before starting the next strain.

#### 2.7 End-of-Harvest Cleanup
1. Wash all stainless steel **“S” hooks** in an alcohol bath and store them.
2. Sweep the drying room floor to remove any remaining plant material.

#### 2.8 Create Bulk Bucked Flower Packages in Metrc

1. After each tote liner bag is weighed and sealed, affix one unused **3 × 4 inch Metrc Package Tag UID** to the outside of the tote lid.
2. Log into Metrc and navigate to: **Processing → Packages → Create Package**.
3. For each tote:
    1. Set **Source** to the Harvest Batch.
    2. Set **Item** to *[Strain Name] – Bulk Flower*.
    3. Enter the exact tote weight as **Quantity**.
    4. Set **Count** to `1`.
    5. Enter the **Package Tag UID** from the tag affixed to the tote.
4. Save the package.

**Compliance Check**

- Each physical tote must correspond to exactly one Metrc Package UID.
- Tote labels and Metrc records must match 1:1.

---

### 3. Weighing Dry Plants

#### 3.1 Set Up Scale (If Necessary)

1. Place the **Ohaus Ranger scale** on the rack above the drying room door.
2. Install the bottom hook.
3. Hang a stainless steel **"S" hook**.
4. **Tare** the scale.

#### 3.2 Configure Software

1. Select **Weigh Plants** from the Harvest menu.
2. Set plant type to **Dry**.
3. No crop or strain selection is required since each plant ID is unique.

#### 3.3 Weighing Dry Plants
1. Hang the plant upside down using the attached S-hook.
2. Confirm the weight appears in the **Weight** box.
3. Scan the QR code on the plant tag.
4. The system records the weight and logs the entry.

#### 3.4 If a QR Code Does Not Scan

1. Hang the plant and verify weight is displayed.
2. Enter the Plant ID manually.
3. Click **Process Current Plant**.

#### 3.5 Duplicate Weight Warning

If the plant was previously weighed, the system displays a warning with:

- **Cancel**
- **Replace Existing Weight**

This may occur if the software was previously set to **Wet** mode.

#### 3.6 Post-Weigh Actions

1. Remove the S-hook.
2. Remove the plant tag.
3. Remove any remaining pieces of plastic trellis.

---

### 4. Weighing Bucked Flower

#### 4.1 Scale Setup

1. Place the Ohaus Ranger scale on the rack above the drying room door.
2. Install the bottom hook.
3. Hang a stainless steel S-hook.
4. **Tare** the scale.

#### 4.2 Prepare Label Printer

1. Ensure the **4BARCODE** printer is selected as the default.
2. Set label stock to **3 × 2 inch** labels.
3. Load label stock into the printer.

#### 4.3 Configure Software for Bucked Flower

1. Select **Weigh Bucked Totes** from the Harvest menu.

**Printer Test**

1. Select:
    - Crop: **1**
    - Strain: **Test Strain**
    - Tote: **1**
2. Click **Print Label** to confirm printing works.

#### 4.4 Weighing Bucked Flower Per Bag

For each strain:

1. Select the **Crop Number**.
2. Select the **Strain**.
3. For each bag of bucked flower:
    1. Remove the bag from the tote.
    2. Seal with a zip tie.
    3. Hang the bag from the scale.
    4. Confirm the weight appears in the **Tote Weight** box.
    5. Click **New Tote** to generate the next tote number.
    6. Click **Save Tote Weight** to print the tote label.
    7. Return the bag to the tote, affix the label, and cover the tote.

---

## Section 3 — Lab Sampling & Test Status in Metrc

### 3.1 Create Lab Sample

1. When all bulk bucked flower totes for a strain are complete, log into Metrc.
2. Navigate to: **Lab Testing → Create Sample**.
3. Select all bulk bucked flower package UIDs for the strain.
4. Generate the lab sample manifest for the licensed laboratory.

### 3.2 Record Test Results

1. After receiving a passing COA, log into Metrc.
2. Navigate to: **Lab Testing → Record Test Results**.
3. Upload the COA.
4. Mark all associated bulk packages as **Tested – Passed**.

**Compliance Check**

- No bulk flower package may be packaged into retail units until marked **Tested – Passed**.
