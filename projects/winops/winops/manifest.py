"""Winget baseline software manifest and PowerShell provisioning script generator."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class WingetPackage:
    """Represents a standardized enterprise workstation software package."""

    id: str
    name: str
    role: str


DEFAULT_BASELINE: tuple[WingetPackage, ...] = (
    WingetPackage(id="Git.Git", name="Git for Windows", role="Developer"),
    WingetPackage(id="Python.Python.3.12", name="Python 3.12", role="Developer"),
    WingetPackage(id="Microsoft.VisualStudioCode", name="Visual Studio Code", role="Developer"),
    WingetPackage(id="Google.Chrome", name="Google Chrome Enterprise", role="Standard"),
    WingetPackage(id="7zip.7zip", name="7-Zip Archiver", role="Standard"),
    WingetPackage(id="Notepad++.Notepad++", name="Notepad++", role="IT Support"),
)


def select_packages_for_profile(profile: str, manifest: list[WingetPackage] | None = None) -> list[dict]:
    """Filter baseline packages applicable to Standard, IT Support, or Developer workstations."""
    catalog = list(manifest) if manifest is not None else list(DEFAULT_BASELINE)
    normalized = profile.strip().lower()
    allowed_roles = {"standard"}
    if normalized in {"it_support", "it-support", "support"}:
        allowed_roles.add("it support")
    elif normalized in {"developer", "dev", "full"}:
        allowed_roles.update({"it support", "developer"})
    elif normalized != "standard":
        raise ValueError("Profile must be one of: standard, it_support, developer")

    return [asdict(pkg) for pkg in catalog if pkg.role.lower() in allowed_roles]


def render_provisioning_ps1(profile: str = "developer") -> str:
    """Generate an idempotent PowerShell Winget provisioning script for IT deployment."""
    packages = select_packages_for_profile(profile)
    lines = [
        f"# WinOps Baseline Provisioning Script (Profile: {profile})",
        "$ErrorActionPreference = 'Stop'",
        "$packages = @(",
    ]
    for pkg in packages:
        lines.append(f"    '{pkg['id']}'")
    lines.extend(
        [
            ")",
            "foreach ($pkgId in $packages) {",
            "    Write-Host \"Checking/Installing $pkgId...\"",
            "    winget install --id $pkgId --exact --silent --accept-package-agreements --accept-source-agreements",
            "}",
        ]
    )
    return "\n".join(lines)


def export_manifest_json(out_path: str | Path, profile: str = "developer") -> Path:
    """Write selected baseline package list to JSON."""
    target = Path(out_path)
    target.write_text(
        json.dumps({"profile": profile, "packages": select_packages_for_profile(profile)}, indent=2),
        encoding="utf-8",
    )
    return target
