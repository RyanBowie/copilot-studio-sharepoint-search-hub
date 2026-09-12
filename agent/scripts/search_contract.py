"""Offline, fail-closed policy validation for the native search/export builder."""

import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from uuid import UUID


ROOT = Path(__file__).resolve().parents[1]
CONTENT_SCOPE = '(contentclass:"STS_ListItem_DocumentLibrary" OR contentclass:"STS_ListItem_WebPageLibrary")'
LIMITS = {"scopeCharacters": 2800, "sitesPerBatch": 20, "maxBatches": 12}
DEPARTMENTS = {"CorpNet", "HR", "Finance", "IT"}


def load_policy(path=None):
    policy = json.loads(Path(path or ROOT / "runtime" / "search-policy.json").read_text(encoding="utf-8-sig"))
    validate_policy(policy)
    return policy


def validate_policy(policy):
    if policy.get("configurationMode") not in {"fictional-reference", "configured"}:
        raise ValueError("Explicit fictional-reference or configured mode is required")
    if policy.get("agentSchema") != "cnh_corpnetSearchHub":
        raise ValueError("Unexpected agent schema; review and rebind the whole source together")
    if policy.get("scopeMode") != "approved-inventory":
        raise ValueError("Only an explicit approved inventory is supported")
    origin = policy.get("tenantOrigin", "")
    if not re.fullmatch(r"https://[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.sharepoint\.com", origin):
        raise ValueError("Configure one HTTPS SharePoint Online tenant origin, without a path")
    if policy.get("limits") != LIMITS:
        raise ValueError("Changing safety limits requires a reviewed compiler update")
    UUID(policy["hubSiteCollectionId"])
    sites = policy.get("sites", [])
    if not sites:
        raise ValueError("An empty inventory must never become an unscoped query")
    if len(sites) > LIMITS["sitesPerBatch"] * LIMITS["maxBatches"]:
        raise ValueError("Scope exceeds the bounded site-batch budget")
    seen_ids, seen_urls = set(), set()
    for site in sites:
        identifier = str(UUID(site["siteId"]))
        if identifier in seen_ids:
            raise ValueError("A site collection must appear only once in the approved inventory")
        seen_ids.add(identifier)
        url = site["url"]
        parsed = urlsplit(url)
        if (
            f"{parsed.scheme}://{parsed.netloc}" != origin
            or not re.fullmatch(r"/sites/[A-Za-z0-9_-]+", parsed.path)
            or parsed.query or parsed.fragment or len(url) > 240
            or url.lower() in seen_urls
            or site.get("department") not in DEPARTMENTS
        ):
            raise ValueError("Invalid, cross-tenant or duplicate approved site")
        seen_urls.add(url.lower())
    if policy.get("searchSiteUrl", "").lower() not in seen_urls:
        raise ValueError("The search endpoint must be an approved site")
    if policy["configurationMode"] == "configured":
        flags = ("hubRegistrationVerified", "hubSearchVerified", "metadataFieldsVerified", "searchLocatorFieldsVerified")
        if not all(policy.get(flag) is True for flag in flags):
            raise ValueError("Configured mode requires independently verified hub, index, metadata and locators")
        if origin == "https://contoso.sharepoint.com" or any(
            value.startswith("00000000-") for value in [policy["hubSiteCollectionId"], *seen_ids]
        ):
            raise ValueError("Replace all fictional tenant and resource placeholders before configured mode")
