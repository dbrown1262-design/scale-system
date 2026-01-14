# Edit SOP Index SOP

## 1. Purpose

To define the standardized procedure for managing the SOP file index, including editing SOP descriptions and sequence numbers. This ensures accurate organization, ordering, and display of Standard Operating Procedures within the application's menu system.

---

## 2. Inputs

- Supabase Web App
- sopfiles table
- Activity selection list
- SOP file names
- Sequence numbers
- Description text

---

## 3. Responsibilities

- **Operations Manager:** Maintain accurate SOP descriptions and logical ordering of procedures.
- **Training Coordinator:** Verify SOP sequence aligns with workflow and training materials.
- **Administrator (Admin Menu):** Monitor SOP index integrity and resolve display issues.

---

## 4. Procedure

### 4.1 Launch the SOP Index Editor

1. From the main menu, navigate to SOP Scripts → Edit SOP Index.
2. The Edit SOP Index window will open.
3. The system automatically loads the list of activities from the sopfiles table.

---

### 4.2 Select an Activity

**Choose Activity**

1. In the Activity dropdown at the top of the window, select the desired activity category.
	- Activities represent functional areas such as "Harvest", "Packaging", "Trimmers", "Modules", etc.
2. The system will automatically load all SOP files associated with the selected activity.

**Data Display**

The grid displays three columns:

- **File Name:** The name of the SOP markdown file (e.g., "PrintPlantTags.md").
- **Seq #:** The sequence number used to order SOPs in menus (lower numbers appear first).
- **Description:** A brief text description of the SOP's purpose.

Files are displayed in the order they were retrieved from the database.

---

### 4.3 Edit SOP Details

**Select an SOP File**

1. Click on any row in the grid to select it.
2. The selected SOP's values will populate the form fields at the bottom of the window.

**Editable Fields**

The following fields can be modified:

- **File Name:** (Read-only) Displays the selected file name for reference.
- **Seq #:** The display order number (numeric value). Default is 99.
	- Lower numbers appear earlier in menus.
	- Use increments of 10 (e.g., 10, 20, 30) to allow easy insertion of new SOPs.
- **Description:** A brief description of the SOP's purpose and function.

**Validation**

- Sequence number must be a valid integer.
- Description can be any text string or left blank.

**Save Changes**

1. After editing the Seq # or Description fields, click the **Save** button.
2. The system will:
	- Validate that a file is selected and sequence number is numeric.
	- Update the sopfiles table for the selected Activity and FileName.
	- Refresh the grid to display updated values.
	- Display a status message confirming the update.

---

### 4.4 Refresh and Clear

**Refresh Data**

- Click the **Refresh** button to reload the latest SOP file data from the database for the selected activity.

**Clear Selection**

- Click the **Clear** button to deselect the current row and reset the form fields.
- This allows you to select a different SOP without interference from previously selected data.

---

### 4.5 Change Activity

To view and edit SOPs for a different activity:

1. Select a new activity from the Activity dropdown.
2. The system automatically loads SOP files for the new activity.
3. Edit SOP details as needed following step 4.3.

---

## 5. Quality & Compliance Checks

- Sequence numbers should be unique or logically ordered to prevent display confusion.
- Common sequence numbering convention: use increments of 10 (10, 20, 30, etc.) to allow easy insertion.
- SOP descriptions should be concise and accurately describe the procedure's purpose.
- All active SOP files should have a description to aid user navigation.
- Verify sequence numbers produce the intended menu order after making changes.

---

## 6. Records

- Supabase sopfiles table
- Updated sequence numbers and descriptions by Activity and FileName
- Activity selection and file list used
