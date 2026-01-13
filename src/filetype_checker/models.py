# define a single result object
from dataclasses import dataclass


@dataclass
class DetectionResult:
    ok: bool
    path: str
    file_type: str | None
    size_bytes: int | None
    matched: bool
    offset: int | None
    signature: str | None
    ext: str     
    mismatch: bool
    error: dict | None

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "path": self.path,
            "file_type": self.file_type,
            "size_bytes": self.size_bytes,
            "magic": {
                "matched": self.matched,
                "offset": self.offset,
                "signature": self.signature,
            },
            "ext": self.ext,
            "mismatch": self.mismatch,
            "error": self.error,
        }
    