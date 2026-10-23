#!/usr/bin/env python3
"""Generate PDFs by running the existing Medanic document templates headlessly.

Input is one JSON object on stdin. All SQLite data is temporary and scoped to a
single render; the desktop database is never opened or modified.
"""

from __future__ import annotations

import importlib.util
import glob
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_APP = ROOT / "driving_school_single.py"


def expose_tkinter_extension():
    try:
        import _tkinter  # noqa: F401
        return
    except ModuleNotFoundError:
        version = f"{sys.version_info.major}.{sys.version_info.minor}"
        candidates = glob.glob(
            f"/nix/store/*-python{version}-tkinter-*/lib/"
            f"python{version}/site-packages"
        )
        if not candidates:
            raise RuntimeError("The document renderer requires the matching Tk package.")
        sys.path[:0] = sorted(candidates)
        import _tkinter  # noqa: F401


def snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def load_desktop_app():
    spec = importlib.util.spec_from_file_location("medanic_desktop_templates", DESKTOP_APP)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the existing document templates.")
    app = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = app
    spec.loader.exec_module(app)
    from reportlab.lib.enums import TA_LEFT

    app.TA_LEFT = TA_LEFT
    return app


def insert_records(connection: sqlite3.Connection, table: str, records: list[dict]):
    if not records:
        return
    columns = {
        row[1]
        for row in connection.execute(f'PRAGMA table_info("{table}")').fetchall()
    }
    if not columns:
        raise RuntimeError(f"Temporary document table is missing: {table}")
    for record in records:
        normalized = {
            snake_case(key): value
            for key, value in record.items()
            if snake_case(key) in columns and key != "passwordHash"
        }
        normalized = {key: value for key, value in normalized.items() if value is not None}
        if not normalized:
            continue
        names = list(normalized)
        placeholders = ", ".join("?" for _ in names)
        quoted_names = ", ".join(f'"{name}"' for name in names)
        connection.execute(
            f'INSERT OR REPLACE INTO "{table}" ({quoted_names}) VALUES ({placeholders})',
            [normalized[name] for name in names],
        )


def main():
    request = json.load(sys.stdin)
    document_type = request.get("type")
    output_path = Path(request["outputPath"]).resolve()
    temp_dir = Path(request["tempDir"]).resolve()
    temp_dir.mkdir(parents=True, exist_ok=True)
    database_path = temp_dir / "render.sqlite"
    tempfile.tempdir = str(temp_dir)

    expose_tkinter_extension()
    app = load_desktop_app()
    app.DB_PATH = str(database_path)
    app.LANG = "fr" if request.get("language") == "fr" else "ar"
    app.init_db()

    datasets = request.get("datasets", {})
    with sqlite3.connect(database_path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        if datasets.get("school"):
            insert_records(connection, "school_info", [{**datasets["school"], "id": 1}])
        for table in (
            "instructors",
            "vehicles",
            "candidates",
            "training_stages",
            "sessions",
            "payments",
            "expenses",
            "exam_results",
            "exam_attempts",
        ):
            insert_records(connection, table, datasets.get(table, []))
        connection.commit()

    frame = app.DocumentsFrame.__new__(app.DocumentsFrame)
    candidate_id = request.get("candidateId")
    frame.selected_candidate_id = candidate_id
    frame._check = lambda: bool(app.HAS_REPORTLAB)
    frame._get_candidate = lambda: (
        app.CandidateDB.get(candidate_id) if candidate_id else None
    )
    frame._ask_save = lambda _default_name: str(output_path)
    frame._ask_date_range_for_doc = lambda: (
        request.get("from", "") or "",
        request.get("to", "") or "",
    )
    def save_for_web(source, *_args, **_kwargs):
        source_path = Path(source)
        if source_path.is_file() and source_path.resolve() != output_path:
            shutil.copy2(source_path, output_path)
    frame._trigger_print = save_for_web
    app.filedialog.asksaveasfilename = lambda **_kwargs: str(output_path)
    app.show_info = lambda *_args, **_kwargs: None
    app.show_error = lambda message, *_args, **_kwargs: (_ for _ in ()).throw(
        RuntimeError(str(message))
    )

    if document_type == "dispatch_table":
        candidate_rows = app.CandidateDB.get_all()
        requested_ids = {int(value) for value in request.get("candidateIds", [])}
        if requested_ids:
            candidate_rows = [row for row in candidate_rows if int(row["id"]) in requested_ids]
        options = request.get("options", {})
        settings = {
            "dispatch_date": options.get("dispatchDate")
            or app.date.today().strftime("%d/%m/%Y"),
            "record_number": options.get("recordNumber", ""),
            "wilaya": options.get("wilaya") or app.SchoolInfoDB.get().get("wilaya", ""),
        }
        frame._generate_dispatch_table_pdf(
            str(output_path),
            candidate_rows,
            settings,
            direct_print=False,
            default_name="dispatch_table.pdf",
        )
    elif document_type == "exam_candidates_list":
        candidate_rows = app.CandidateDB.get_all()
        options = request.get("options", {})
        requested_ids = {int(value) for value in request.get("candidateIds", [])}
        if requested_ids:
            candidate_rows = [
                row for row in candidate_rows if int(row["id"]) in requested_ids
            ]
        license_type = options.get("licenseType")
        if license_type:
            candidate_rows = [
                row for row in candidate_rows if row.get("license_type") == license_type
            ]
        instructor_id = options.get("instructorId")
        if instructor_id:
            candidate_rows = [
                row
                for row in candidate_rows
                if str(row.get("instructor_id") or "") == str(instructor_id)
            ]
        app.DocumentsFrame._generate_exam_list_pdf(
            frame,
            str(output_path),
            candidate_rows,
            app.SchoolInfoDB.get(),
            options.get("examDate") or app.date.today().strftime("%d/%m/%Y"),
            options.get("examCenter", ""),
            options.get("documentReference", ""),
            options.get("wilaya") or app.SchoolInfoDB.get().get("wilaya", ""),
            options.get("stageType", "all"),
            default_name="exam_candidates.pdf",
            instructor_name=options.get("instructorName", ""),
            training_card_num=options.get("trainingCardNumber", ""),
            vehicle_nm=options.get("vehicleNumber", ""),
        )
    else:
        methods = {
            "exam_form": "_doc_exam_form",
            "training_card": "_doc_training_card",
            "contract": "_doc_contract",
            "certificate": "_doc_certificate",
            "payment_receipt": "_doc_payment_receipt",
            "candidates_list": "_doc_candidates_list",
            "instructors_list": "_doc_instructors_list",
            "expenses_report": "_doc_expenses_report",
            "payments_report": "_doc_payments_report",
        }
        method_name = methods.get(document_type)
        if not method_name:
            raise ValueError("Unknown official document type.")
        getattr(frame, method_name)()
        if document_type == "training_card":
            generated = sorted(
                Path(tempfile.gettempdir()).glob("training_card_*.pdf"),
                key=lambda item: item.stat().st_mtime,
                reverse=True,
            )
            if generated:
                os.replace(generated[0], output_path)

    if not output_path.is_file() or output_path.stat().st_size < 100:
        raise RuntimeError("The official document template did not create a PDF.")
    print(json.dumps({"ok": True, "size": output_path.stat().st_size}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
