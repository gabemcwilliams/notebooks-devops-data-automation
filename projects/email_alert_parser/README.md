# Email Alert Extraction & Parsing Pipeline

This three-script pipeline extracts `.msg` emails from Microsoft Outlook via COM automation,
parses their contents into structured metadata, and enables downstream inspection and
filtering of those messages for SOC, alerting, or automation workflows.

---

## Script 1: `.py`
**Purpose:**
- Connects to multiple Outlook folders (Alerts, Support, SOC)
- Filters messages from "Deleted Items" (potential false positives or routed alerts)
- Saves original `.msg` files
- Extracts structured metadata:
  - Sender
  - Recipient
  - Timestamp
  - Subject
  - Message body
  - Attachments
- Outputs: `D:/cache/mystery_emails/<account_name>/suspicious_msgs/*.msg`

**Why it's useful:**
Captures misrouted or silently dropped security/ops messages that require later analysis.

---

## Script 2: `.py`
**Purpose:**
- Walks through the `.msg` files saved by script 1
- Uses `extract_msg` to parse headers, body, and attachments
- Filters out internal/system destinations
- Extracts metadata and header content
- Saves:
  - `.json`: structured metadata for each message
  - `.txt`: original headers
  - `info.msg`: original `.msg` file
- Outputs: `D:/cache/parsed_emails/<account_name>/parsed_info/`
- Aggregates metadata to:
  - `combined_<timestamp>.csv`

**Why it's useful:**
Produces structured, inspectable data from binary `.msg` files. Enables ML labeling,
alert correlation, or manual triage.

---

## Script 3: `.py`
**Purpose:**
- Loads previously parsed CSVs from alerts, SOC, and support
- Combines them into a single DataFrame
- Extracts clean `from_email` and `to_email` addresses from message metadata
- Derives a `path_keyword` from the save path for identifying email groups
- Enables line-by-line header file loading and inspection from the parsed directories
- Supports subject-based filtering, sender frequency analysis, and manual exploration

**Why it's useful:**
This script closes the loop from raw `.msg` capture through to downstream triage,
allowing analysts or automated agents to filter, classify, or enrich the parsed records.

---

## Example Use Case
- Security alerts from `alerts@example.co` are deleted before triage
- Script 1 recovers them and saves `.msg` files
- Script 2 parses those into usable JSON + CSV rows for analyst workflows
- Script 3 joins and filters those records, enabling email-to-incident traceability

---

## Dependencies
- `pandas`, `numpy`, `re`, `datetime`, `traceback`
- `win32com.client` (for Outlook extraction)
- `extract_msg` (for parsing `.msg` files)
- `matplotlib`, `seaborn` (optional for inspection and visualization)
- `pathlib`, `shutil`

---

## Author
Gabe McWilliams
