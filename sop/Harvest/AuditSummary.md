# Audit Defense Summary

## Harvest, Inventory, and METRC Control System

### 1. Overview

The facility operates a **batch-controlled inventory system** in which cannabis material is tracked at the batch (package) level in METRC and at the sub-unit level in an internal database (Supabase).

This system ensures:

* Full traceability from plant to finished product
* Accurate mass balance reconciliation
* Compliance with METRC reporting requirements
* Operational efficiency without unnecessary handling

---

### 2. METRC Inventory Model

* Each harvest batch (Crop Number + Strain) is entered into METRC as:

  * A **single METRC package**

* METRC is used to track:

  * Regulatory inventory
  * Transfers
  * Final product disposition

* METRC packages are not subdivided unless:

  * Material is removed for independent handling
  * Material is transferred or processed separately

---

### 3. Internal Tracking System

The facility uses an internal system (Supabase) to track:

* Individual plant weights (wet and dry)
* Bucked flower totes (Tote ID and weight)
* Trimming outputs (flower, smalls, trim)

This provides:

* Detailed operational visibility
* Sub-unit tracking without excessive METRC entries
* Support for reconciliation and audit review

---

### 4. Physical Material Handling

**Totes**

* Represent sub-units of a batch
* Identified with internal Tote IDs
* Not independent inventory units

**Buckets**

* Used during manual trimming
* Temporary processing containers only
* Not inventory units
* Not tracked in METRC

All material:

* Remains associated with its originating batch
* Is not moved or processed independently without a METRC split

---

### 5. Processing Model

* Material is processed in **working quantities** (trays/buckets)
* Intermediate transfers are not individually weighed
* Trimming outputs are recorded at the batch level

This approach:

* Maintains efficiency
* Avoids unnecessary handling steps
* Preserves product quality

---

### 6. Mass Balance & Reconciliation

The facility maintains full mass balance using:

* Plant Weights Summary (plant-level inputs)
* Bucked tote weights (intermediate tracking)
* Trimming output records
* Harvest Summary report (final reconciliation)

Reconciliation confirms:

> Total Input = Flower + Smalls + Trim + Stems

Reconciliation is performed:

* At completion of trimming
* Prior to packaging or further processing

---

### 7. METRC Data Entry

* METRC harvest weights are entered using:

  * **Plant Weights Summary (dry weights by strain)**

* This ensures:

  * Accurate regulatory reporting
  * Alignment with plant-level records
  * Elimination of duplicate or derived data entry

---

### 8. Controls & Compliance Safeguards

The system includes the following controls:

* One strain processed at a time (no cross-contamination)
* Mandatory labeling of totes and buckets
* No independent handling without METRC split
* Dual verification of METRC entries
* Complete traceability to plant-level records
* Documented SOPs for all processes

---

### 9. Summary

This system provides:

* Accurate METRC reporting
* Complete traceability
* Verified mass balance
* Efficient processing workflow

The facility maintains control at all times while avoiding unnecessary complexity or redundant tracking.

---

**Approved By:** President/CEO
**Effective Date:** [Enter Date]
