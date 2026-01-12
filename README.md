# File Type Checker (Magic Numbers)
A Python CLI tool that detects file types by reading "magic numbers" or file signatures

Command: `ftcheck`

## Install

## Setup (dev)
```bash
python -m pip install -e ".[dev]"
```

## Usage
```bash
ftcheck path/to/file --json
```

## JSON schema
when `--json` is provided, `ftcheck` prints only JSON to stdout

## Success
ok (bool): true 
path (string): input path
file_type (string): detected type label (or "Unknown File Type")
size_bytes (int): total file size in bytes
magic (object):
    matched (bool)
    offset (int|null)
    signature (string|null): matched signature bytes (hex)

## Error
ok (bool): false \ 
path (string|null) \
error (object): \
    code (string): stable error code (e.g. ENOENT) \
    message (string) \
    details (object, optional) \

## Exit codes
0 success \
1 other errors (I/O, internal) \
2 CLI usage error (e.g., missing path) \
3 path not found (ENOENT) \ 
4 permission denied (EACCES) \
5 path is a directory / invalid file type (EISDIR / ENOTFILE) \ 

## Supported file types
Current supported signatures: \
(1) PNG \
(2) JPEG \
(3) GIF (GIF87a / GIF89a) \
(4) PDF \
(5) ZIP \

## Example
```bash
ftcheck path/to/file --json
```
## Output
{ \ 
    "ok": true, \ 
    "path": "path/to/file", \
    "file_type": "PDF Document", \
    "size_bytes": 18342, \
    "magic": { \
        "matched": true, \
        "offset": 0, \
        "signature": "25504446" \
    } \ 
} \
