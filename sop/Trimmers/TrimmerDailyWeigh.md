# Daily Trim Weight Entry — Scale & Application SOP

### 1. Purpose

To standardize the process for accurately recording daily trim weights using the Ohaus Scout scale and the Trim Weight Entry application. This ensures proper tracking of trimmer productivity, calculation of paid hours, and accurate inventory management for trimmed flower and smalls.

---

### 2. Required Equipment

- Ohaus Scout scale
- Trim Weight Entry application (Trimmers menu)
- Containers for weighing trimmed product
- Daily trim tracking sheets (optional backup)

---

### 3. Set Up the Scale (If Necessary)

1. Place the Ohaus Scout scale on a stable, level surface.
2. Power on the scale.
3. Allow the scale to warm up and stabilize (approximately 30 seconds).
4. Tare the scale to zero with no weight on the platform.

---

### 4. Operating the Trim Weight Entry Application

1. Open the Trimmers menu.
2. Select **Trim Weight Entry**.
3. Check the scale status indicator in the upper right corner:
	- **Scale: Connected** (green) — Scout scale is ready
	- **Scale: Not Found** (red) — Check power and USB connection
4. The weight display will automatically update from the scale.

---

### 5. Recording Trim Weights

Trimmers must weigh and record their production at three specific times each day:
- **Lunch time** (typically around 12:00 PM)
- **End of shift** (typically around 5:00 PM)
- **When a strain is finished** (any time during the shift)

#### 5.1 Select Trimmer and Date

1. Select your name from the **Trimmer** dropdown.
2. Verify the **Trim Date** is correct.
	- The date defaults to today's date
	- Use the calendar picker to select a different date if needed

#### 5.2 Select Crop and Strain

1. Select the **Crop No** from the dropdown.
	- Crops are displayed in format: "CropNo - HarvestDate"
	- The strain list will automatically populate for the selected crop
2. Select the **Strain** you are trimming.

#### 5.3 Select Type

1. Select the product **Type** from the dropdown:
	- **Flower** — Premium trimmed buds
	- **Smalls** — Smaller buds and trim

#### 5.4 Select Time Period

1. Select **AM/PM** to indicate the time period:
	- **Morning** — Restricts time selection to 8:00 AM - 1:00 PM
	- **Afternoon** — Restricts time selection to 12:00 PM - 5:00 PM
2. Select **Start Time** from the dropdown.
	- Times are displayed in 15-minute intervals
3. Select **End Time** from the dropdown.
	- End time must be equal to or later than start time

> **Important:** Accurate start and end times are required to calculate total hours worked. Trimmers must work at least 6 hours per day to be paid for lunch.

#### 5.5 Weigh and Record

1. Place the container of trimmed product on the scale.
2. Wait for the weight to stabilize.
3. Verify the weight appears in the **Weight (g)** field.
4. Click **Save Entry**.
5. The system will validate all fields and save the entry.
6. A confirmation message will appear: "Trim weight recorded."
7. The fields will clear, ready for the next entry.

---

### 6. Multiple Entries Per Session

If weighing multiple batches during the same time period:

1. After saving an entry, the Trimmer, Crop, Strain, Type, AM/PM, Start Time, and End Time remain selected.
    - Change the selections to match the next batch to weigh
    - For example, if a Trimmer just weighed the bigs for the morning and needs to weigh the smalls, they only have to change the type.
    - When changing to a new Trimmer, verify/change all selections before saving.
2. Place the next batch on the scale.
3. Verify the new weight appears.
4. Click **Save Entry**.
5. Repeat for each batch.

---

### 7. Changing Strains

When switching to a different strain:

1. Select the new **Strain** from the dropdown.
2. Update **Type** if needed (Flower or Smalls may differ).
3. Continue weighing and recording as normal.

---

### 8. Time Tracking for Lunch Pay

The system automatically calculates total hours worked based on start and end times entered throughout the day:

- **6 hours or more** — Trimmer is paid for 30-minute lunch break
- **Less than 6 hours** — Trimmer is not paid for lunch break

**Best Practices:**
- Record accurate start times when beginning work
- Record accurate end times for each weigh session
- If working through lunch, ensure total hours exceed 6 to qualify for paid lunch

**Example:**
- Start: 8:00 AM, End: 12:00 PM (morning entry)
- Start: 12:30 PM, End: 5:00 PM (afternoon entry)
- Total: 8.5 hours worked → Lunch is paid

---

### 9. Using the Buttons

**Save Entry**
- Saves the current trim weight record to the database
- Validates all required fields before saving
- Automatically prints confirmation and clears weight for next entry

**Clear**
- Clears the Weight field and time selections
- Useful if you need to re-enter information

**Refresh Lists**
- Reloads Trimmer and Crop lists from database
- Use if new trimmers or crops have been added

**Close**
- Closes the application and returns to the main menu

---

### 10. Validation Messages

The application will display color-coded status messages:

**Green (Info):**
- "Trim weight recorded." — Entry saved successfully

**Orange (Warning):**
- "Please choose a Trimmer." — No trimmer selected
- "Please choose a Crop No." — No crop selected
- "Please choose a Strain." — No strain selected
- "Please choose Morning or Afternoon." — AM/PM not selected
- "Please choose a Start Time." — Start time missing
- "Please choose an End Time." — End time missing
- "Start Time must be before or equal to End Time." — Time conflict
- "Please enter Grams." — No weight entered
- "Grams must be a positive number." — Invalid weight value

**Red (Error):**
- "Could not save entry: [error]" — Database save failed

---

### 11. Quality & Compliance Checks

- Verify the scale is tared before each weighing session
- Ensure containers are clean and dry before weighing
- Record weights immediately after trimming for accuracy
- Double-check crop and strain selection to avoid data entry errors
- Review start and end times for accuracy before saving
- Keep trimmed product separated by strain and type until recorded

---

### 12. Troubleshooting

**Scale not reading:**
- Verify scale status shows "Scale: Connected"
- Check scale power and USB connection
- Ensure scale is tared to zero
- Restart the application if scale was connected after app startup

**Weight appears as "Error":**
- The scale is disconnected or experiencing communication issues
- Check USB connection
- Power cycle the scale
- Restart the application

**Cannot save entry:**
- Verify all required fields are filled
- Check that start time is before or equal to end time
- Ensure weight is a positive number
- Verify database connection (contact administrator)

**Trimmer name not in list:**
- Click **Refresh Lists** to reload trimmers
- Contact administrator to add new trimmer

**Crop or Strain not in list:**
- Click **Refresh Lists** to reload data
- Verify crop is marked as "Active" in the system
- Contact administrator if crop should be available

**Time selection limited:**
- Time options change based on AM/PM selection
- Morning: 8:00 AM - 1:00 PM
- Afternoon: 12:00 PM - 5:00 PM
- Change AM/PM selection to access different time ranges

---

### 13. End of Day Procedures

1. Record final weights for all product trimmed during the day.
2. Verify all entries have been saved (check for confirmation messages).
3. Ensure total hours worked are accurately recorded for payroll.
4. Clean and tare the scale for the next day.
5. Close the application.
