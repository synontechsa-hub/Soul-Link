"""
Z-CAD Python — Job persistence (JSON)
"""
import json
import os
from datetime import datetime
from pathlib import Path
from .models import Job, Sheet, Piece


def job_to_dict(job: Job) -> dict:
    return {
        "version": "1.0",
        "saved_at": datetime.now().isoformat(),
        "name": job.name,
        "customer": job.customer,
        "notes": job.notes,
        "material_name": job.material_name,
        "blade_kerf": job.blade_kerf,
        "hourly_rate": job.hourly_rate,
        "markup_percent": job.markup_percent,
        "sheets": [
            {
                "id": s.id,
                "width": s.width,
                "height": s.height,
                "active": s.active,
                "quantity": s.quantity,
                "buy_price": s.buy_price,
                "sell_price": s.sell_price,
                "thickness": s.thickness,
                "label": s.label,
            }
            for s in job.sheets
        ],
        "pieces": [
            {
                "id": p.id,
                "quantity": p.quantity,
                "width": p.width,
                "height": p.height,
                "can_rotate": p.can_rotate,
                "label": p.label,
                "grain_locked": p.grain_locked,
            }
            for p in job.pieces
        ],
    }


def job_from_dict(data: dict) -> Job:
    job = Job(
        name=data.get("name", ""),
        customer=data.get("customer", ""),
        notes=data.get("notes", ""),
        material_name=data.get("material_name", ""),
        blade_kerf=data.get("blade_kerf", 4),
        hourly_rate=data.get("hourly_rate", 0.0),
        markup_percent=data.get("markup_percent", 0.0),
    )
    for s in data.get("sheets", []):
        job.sheets.append(Sheet(
            id=s.get("id", ""),
            width=s.get("width", 0),
            height=s.get("height", 0),
            active=s.get("active", True),
            quantity=s.get("quantity", 1),
            buy_price=s.get("buy_price", 0.0),
            sell_price=s.get("sell_price", 0.0),
            thickness=s.get("thickness", 0.0),
            label=s.get("label", ""),
        ))
    for p in data.get("pieces", []):
        job.pieces.append(Piece(
            id=p.get("id", ""),
            quantity=p.get("quantity", 0),
            width=p.get("width", 0),
            height=p.get("height", 0),
            can_rotate=p.get("can_rotate", True),
            label=p.get("label", ""),
            grain_locked=p.get("grain_locked", False),
        ))
    return job


def save_job(job: Job, filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(job_to_dict(job), f, indent=2, ensure_ascii=False)


def load_job(filepath: str) -> Job:
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return job_from_dict(data)


def load_zad_file(filepath: str) -> Job:
    """Import a legacy Z-CAD .ZAD file."""
    with open(filepath, "rb") as f:
        content = f.read().decode("latin-1")

    lines = content.replace("\r\n", "\n").split("\n")
    job = Job()
    job.name = Path(filepath).stem

    for line in lines:
        parts = line.split("\t")
        if line.startswith("Material:"):
            job.material_name = parts[1].strip() if len(parts) > 1 else ""

        elif line.startswith("Mat.\t"):
            # Mat. [idx] [active] [-1] [width] [height] [?] [buy] [sell] [thick] [kerf] [rate]
            if len(parts) >= 7:
                active = parts[2].strip() == "1"
                w = int(parts[4]) if parts[4].strip() != "0" else 0
                h = int(parts[5]) if parts[5].strip() != "0" else 0
                if active and w > 0 and h > 0:
                    sheet = Sheet(width=w, height=h, active=True)
                    if len(parts) >= 12:
                        try:
                            sheet.buy_price = float(parts[7])
                            sheet.sell_price = float(parts[8])
                            sheet.thickness = float(parts[9])
                            job.blade_kerf = int(parts[10])
                            job.hourly_rate = float(parts[11])
                        except (ValueError, IndexError):
                            pass
                    job.sheets.append(sheet)

        elif line.startswith("Auftrag:"):
            job.customer = parts[1].strip() if len(parts) > 1 else ""

        elif line.startswith("Sonstiges:"):
            job.notes = parts[1].strip() if len(parts) > 1 else ""

        elif line.startswith("Pos.\t"):
            # Pos. [idx] [qty] [width] [height] [rotation]
            if len(parts) >= 5:
                qty = int(parts[2]) if parts[2].strip() else 0
                w = int(parts[3]) if parts[3].strip() else 0
                h = int(parts[4].strip()) if parts[4].strip() else 0
                if qty > 0 and w > 0 and h > 0:
                    job.pieces.append(Piece(quantity=qty, width=w, height=h))

    return job


def get_recent_jobs(jobs_dir: str, max_count: int = 10) -> list[dict]:
    """Return list of recent job files sorted by modification time."""
    path = Path(jobs_dir)
    if not path.exists():
        return []
    files = sorted(path.glob("*.zcad"), key=lambda p: p.stat().st_mtime, reverse=True)
    result = []
    for f in files[:max_count]:
        result.append({
            "path": str(f),
            "name": f.stem,
            "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d.%m.%Y %H:%M"),
        })
    return result
