# File Type Checker (Magic Numbers)
A Python CLI tool that detects file types by reading "magic numbers" or file signatures.

Command: `ftcheck`

## Install

### Setup (dev)
```bash
python -m pip install -e ".[dev]"
source .venv/Scripts/activate
```

## Usage
### Check one or more paths (file or directories)
```bash
ftcheck PATH [PATH ...]
```

### Scan directories recursively
```bash
ftcheck -r PATH [PATH ...]
```

### JSON output (single JSON document)
```bash
ftcheck --json PATH [PATH ...]
```
## Output modes
### Human output (default)
Prints one line per scanned file. If the detected type does not match the file extension, it appends (extension mismatch: .ext)

At the end, it prints a summary to stderr:
```text
Scanned: 2 files (matched: 2, unknown: 0, errors: 0)
```

### JSON output (--json)
When --json is provided, ftcheck prints one JSON document to stdout:

- ok: true if no errors occurred
- summary: counts for this run
- results: list of per-file success items and error items

## JSON schema
### Top-level document
```json
{
    "ok":true,
    "summary": {
        "inputs": 1,
        "files_scanned": 2,
        "matched": 2,
        "unknown": 0,
        "errors": 0
    },
    "results":[]
}
```

### Success Item
```json
{
    "ok": true,
    "path": "path/to/file",
    "file_type": "PDF Document",
    "size_bytes": 18342,
    "magic": {
        "matched": true,
        "offset": 0,
        "signature": "255044462D"
    },
    "ext": ".pdf",
    "mismatch": false
}
```

### Error Item
```json
{
    "ok": false,
    "path": "path/to/file",
    "error": {
        "code": "ENOENT",
        "message": "File not found: path/to/file-or-input",
        "details": {
            "path": "path/to/file-or-input"
        }
    }
}
```

## Exit codes
- 0 = no errors and all scanned files matched a known type
- 1 = no errors, but at least one scanned file was Unknown File Type
- 2 = at least one error occurred (missing path, permissions, I/O, etc.)

## Supported file types
Current supported signatures: 
1. PNG 
2. JPEG 
3. GIF (GIF87a / GIF89a) 
4. PDF 
5. ZIP 

## Example
## Recursive scan with JSON output
```bash
ftcheck path/to/file -r --json
```
Example output (truncated):
```json
{
    "ok": true,
    "summary": {
        "inputs": 1,
        "files_scanned": 2,
        "matched": 2,
        "unknown": 0,
        "errors": 0
    },
    "results": [
    {
        "ok": true,
        "path": "samples/photo.jpg",
        "file_type": "JPEG Image",
        "size_bytes": 10592782,
        "magic": { "matched": true, "offset": 0, "signature": "FFD8FF" },
        "ext": ".jpg",
        "mismatch": false
    }
    ]
}
```
