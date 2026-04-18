## Section 1 — Purpose
To establish a procedure for locating and retrieving prior revisions of Standard Operating Procedures (SOPs) stored in the Git repository.

## Section 2 — Scope
This procedure applies to all SOP files maintained in the organization’s Git repository, including current and superseded versions.

## Section 3 — Responsibilities

### 3.1 Authorized Personnel
Only the President or CEO is authorized to retrieve, review, or restore prior SOP versions from the Git repository.

### 3.2 Personnel
Personnel may request review of a prior SOP version when needed for audit, investigation, training, or document control purposes, but may not directly alter repository history.

## Section 4 — When Prior Versions May Be Retrieved
Prior SOP versions may be retrieved for the following reasons:

- Audit or regulatory review
- Internal investigation or deviation review
- Verification of the SOP version in effect on a specific date
- Review of document revision history
- Recovery of a prior approved version

## Section 5 — Procedure for Locating Prior Versions in Git

### 5.1 Identify the SOP File
Identify the SOP file name and file path within the repository.

Example:
`scale/sop/Harvest/WeighHarvest.md`

### 5.2 Open the Repository
Open the local repository in a terminal, command prompt, VS Code, or other approved Git interface.

### 5.3 View Revision History for a Specific SOP
- Use the following command to view the commit history for the SOP file:
- git log --follow -- scale/sop/Harvest/WeighHarvest.md

## Section 6 — Revision History

Revision: 1  
Effective Date: 2026-04-09  
Approved By: President/CEO

Change Summary:  
Rev 1 – Initial release
