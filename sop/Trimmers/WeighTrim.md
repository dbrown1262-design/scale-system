# Weighing Trim Bags — Scale & Application SOP

## 1. Purpose

To standardize the process for accurately weighing trimmed cannabis flower, smalls, and trim bags using the Ohaus Scout or Ranger scale and the Weigh Trim Bags application.

---

## 2. Required Equipment

- Ohaus Scout scale (platform scale) or Ohaus Ranger scale (hanging scale)
- Handheld QR code scanner
- Metric tags (QR-coded labels for bags)
- Weigh Trim Bags application (Trimmers menu)

---

## 3. Set Up the Scale (If Necessary)

1. Ensure the Scout or Ranger scale is powered on.
2. Place the scale on a stable, level surface.
3. Tare the scale to zero before beginning.
4. Verify the USB cable is connected to the computer.

---

## 4. Operating the Weighing Application

1. Open the Trimmers menu.
2. Select **Weigh Trim Bags**.
3. Check the status indicators in the upper right:
	- **Scale: Connected** (green) — scale is ready.
	- **Scale: Not Found** (red) — check power and USB connection.
	- **QR: Connected** (green) — scanner is ready.
	- **QR: Not Found** (red) — turn on scanner and press trigger.
4. Select the **Crop** from the dropdown menu.
5. Select the **Strain** for the trim being weighed.
6. Select the **Type** of material being weighed:
	- **Flower** — trimmed buds.
	- **Smalls** — small buds separated during trimming.
	- **Trim** — leaf material removed during trimming.

---

## 5. Weighing a Trim Bag

1. Place the empty bag on the scale.
2. Tare the scale to zero to account for the bag weight.
3. Fill the bag with the trimmed material.
4. Verify the weight appears in the **Weight (g)** field on screen.
5. Scan the Metric Tag using the handheld QR scanner.
	- The Metric Tag number will automatically populate in the **Metric Tag** field.
6. Click **Save Weight** to record the bag data.
	- The system will save the crop, strain, type, metric tag, weight, and date.
7. The Metric Tag field will clear automatically for the next bag.

---

## 6. If a QR Code Does Not Scan

1. Manually type the Metric Tag number into the **Metric Tag** field.
2. Verify the weight is displayed.
3. Click **Save Weight**.

---

## 7. Printing a Label

After weighing a bag, you can print a label for the bag:

1. Verify all fields are populated:
	- Crop
	- Strain
	- Type
	- Metric Tag
	- Weight
2. Click **Print Label**.
3. The system will retrieve the harvest date from the crop records.
4. A PDF label will be generated and sent to the printer with:
	- Strain name
	- Type (Flower, Smalls, or Trim)
	- Harvest date
	- Metric Tag ID
	- Weight in grams
	- Company name

---

## 8. Duplicate Tag Warning

If a Metric Tag has already been recorded, the system will display a warning:

> **Tag In Use**  
> Metric tag [number] already has data. Update weight to [new weight] g?

- **Yes** — Update the existing bag record with the new weight.
- **No** — Cancel the operation.

> **Note:** This is useful for correcting weights or re-weighing bags.

---

## 9. Tag Mismatch Error

If a Metric Tag has been used for a different crop or strain, the system will display an error:

> **Tag Mismatch**  
> Metric tag [number] belongs to a different strain/crop. Cannot use this tag.

- Click **OK** and use a different Metric Tag.
- Each tag can only be used for one specific crop/strain combination.

---

## 10. Clearing the Form

To start fresh or correct a mistake:

1. Click **Clear**.
2. This will reset:
	- Crop to "Select"
	- Strain to "Select"
	- Type to "Flower"
	- Metric Tag field (empty)
	- Status message

> **Note:** The weight display will continue to show the current scale reading.

---

## 11. Refreshing Lists

If new crops or strains have been added to the database:

1. Click **Refresh Lists**.
2. The Crop dropdown will reload with the latest data.
3. The Strain dropdown will reset to "Select".

---

## 12. Troubleshooting

### Scale Not Reading

- Verify the scale is powered on.
- Check the USB cable connection.
- Check that the scale status shows **Scale: Connected** (green).
- Restart the application if necessary.

### QR Scanner Not Working

- Verify the scanner is powered on (check for beep when app starts).
- Press the trigger on the scanner.
- Check that the QR status shows **QR: Connected** (green).
- Manually enter the Metric Tag number if scanning fails.

### Weight Shows Zero

- Verify material is on the scale platform.
- Check that the scale is tared properly.
- Verify the correct scale (Scout or Ranger) is being used.

### Cannot Save Weight

- Verify all required fields are selected:
	- Crop
	- Strain
	- Type
	- Metric Tag
- Ensure weight is greater than zero.

### Label Won't Print

- Verify all fields are populated before clicking Print Label.
- Check that the printer is powered on and connected.
- Verify the harvest date exists for the selected crop.
- Check the C:\labels\ folder exists and is accessible.

---

## 13. Best Practices

- Always tare the scale with the empty bag before filling.
- Scan or enter the Metric Tag immediately after placing the bag on the scale.
- Verify the Type matches the material being weighed.
- Print labels immediately after weighing for proper bag identification.
- Keep Metric Tags organized and ensure they match the bags.
- Clear the form between bags to avoid mixing data.
