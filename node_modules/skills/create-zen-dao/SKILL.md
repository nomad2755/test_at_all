---
name: create-zen-dao
description: ZenTao API client for bug tracking and project management. Supports login, bug submission, and other ZenTao API operations.
license: MIT
---

# ZenTao DAO Client

A Python client for interacting with ZenTao (禅道) API for bug tracking and project management.

## Features

- Login and obtain authentication token
- Submit bugs to ZenTao
- Extensible for other ZenTao API operations

## Usage

### Basic Usage

```python
from scripts.zentao_client import ZenTaoClient

# Initialize client
client = ZenTaoClient("http://your-zentao-server:port")

# Login
if client.login(account="your_account", password="your_password"):
    # Submit a bug
    bug_data = {
        "title": "Bug Title",
        "severity": 2,
        "pri": 1,
        "project": 1,
        "execution": 17,
        "type": "codeerror",
        "openedBuild": ["trunk"],
        "assignedTo": "Assignee Name",
        "steps": "Bug reproduction steps..."
    }
    result = client.submit_bug(product_id=1, bug_data=bug_data)
```

### Configuration

Default server URL: `http://192.168.0.28:9980`

You can override this by passing a different URL to the constructor.

## API Reference

### ZenTaoClient

**Constructor:**
- `base_url` (str): ZenTao server address (default: "http://192.168.0.28:9980")

**Methods:**

| Method | Description | Parameters |
|--------|-------------|------------|
| `login(account, password)` | Login and obtain token | account: str, password: str |
| `submit_bug(product_id, bug_data)` | Submit a bug | product_id: int, bug_data: dict |

## Bug Data Fields

| Field | Type | Description |
|-------|------|-------------|
| title | str | Bug title (required) |
| severity | int | Severity level (1-4) |
| pri | int | Priority (1-4) |
| project | int | Project ID |
| execution | int | Execution ID |
| type | str | Bug type (codeerror, config, install, etc.) |
| openedBuild | list | Build versions |
| assignedTo | str | Assignee name |
| steps | str | Reproduction steps |

## Example: Submit Bug from Command Line

```bash
python scripts/zentao_client.py
```

## Error Handling

The client handles common errors:
- Network connection failures
- Authentication failures
- API response errors

All errors are printed to console for debugging.
