"""Record this local rebuild without rewriting historical release/import evidence."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "CorpNetSearchHubReference_1_0_0_0_unmanaged.zip"


def main():
    with zipfile.ZipFile(PACKAGE) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP integrity failed.")
        entries = [{"path": name, "sha256": hashlib.sha256(archive.read(name)).hexdigest()}
                   for name in archive.namelist()]
    result = {
        "builtUtc": datetime.now(timezone.utc).isoformat(),
        "artifact": PACKAGE.name,
        "artifactSha256": hashlib.sha256(PACKAGE.read_bytes()).hexdigest(),
        "artifactBytes": PACKAGE.stat().st_size,
        "zipEntries": entries,
        "newTenantImport": "UNVERIFIED",
        "newTenantRuntime": "UNVERIFIED",
        "note": "Local build record only; does not renew historical release, roundtrip or runtime evidence.",
    }
    (ROOT / "build.local.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("Local artifact SHA-256: " + result["artifactSha256"])


if __name__ == "__main__":
    main()
