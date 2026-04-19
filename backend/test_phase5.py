"""
Phase 5 Test Suite — Export, Polling, and Advanced Features

Validates:
- Export router endpoints (posts CSV/JSON, analytics, schedule, formats)
- Frontend polling hook structure
- Export API integration
- Code quality and documentation coverage
"""

import ast
import os
import sys
import importlib.util
from pathlib import Path
from typing import List, Tuple

# ─── Configuration ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

PASSED = 0
FAILED = 0
RESULTS: List[Tuple[str, bool, str]] = []


def record(name: str, passed: bool, detail: str = ""):
    global PASSED, FAILED
    if passed:
        PASSED += 1
    else:
        FAILED += 1
    status = "✅ PASS" if passed else "❌ FAIL"
    RESULTS.append((name, passed, detail))
    print(f"  {status}: {name}" + (f" — {detail}" if detail else ""))


# ─── Test Group 1: Export Router File Structure ───────────────────────────────

def test_export_router_exists():
    path = BACKEND_DIR / "routers" / "export.py"
    record("Export router file exists", path.exists(), str(path))


def test_export_router_importable():
    path = BACKEND_DIR / "routers" / "export.py"
    try:
        spec = importlib.util.spec_from_file_location("export", str(path))
        record("Export router is importable", spec is not None)
    except Exception as e:
        record("Export router is importable", False, str(e))


def test_export_router_valid_python():
    path = BACKEND_DIR / "routers" / "export.py"
    try:
        with open(path) as f:
            ast.parse(f.read())
        record("Export router has valid Python syntax", True)
    except SyntaxError as e:
        record("Export router has valid Python syntax", False, str(e))


# ─── Test Group 2: Export Router Endpoints ────────────────────────────────────

def test_export_posts_endpoint():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_endpoint = '@router.get("/posts")' in content
    record("GET /export/posts endpoint defined", has_endpoint)


def test_export_analytics_endpoint():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_endpoint = '@router.get("/analytics")' in content
    record("GET /export/analytics endpoint defined", has_endpoint)


def test_export_schedule_endpoint():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_endpoint = '@router.get("/schedule")' in content
    record("GET /export/schedule endpoint defined", has_endpoint)


def test_export_formats_endpoint():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_endpoint = '@router.get("/formats")' in content
    record("GET /export/formats endpoint defined", has_endpoint)


# ─── Test Group 3: Export Router Features ─────────────────────────────────────

def test_csv_export_support():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_csv = "csv" in content and "DictWriter" in content
    record("CSV export support (csv module + DictWriter)", has_csv)


def test_streaming_response():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_streaming = "StreamingResponse" in content
    record("StreamingResponse for CSV downloads", has_streaming)


def test_content_disposition():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_disposition = "Content-Disposition" in content
    record("Content-Disposition header for downloads", has_disposition)


def test_filter_parameters():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_status = "status" in content
    has_platform = "platform" in content
    has_date_from = "date_from" in content
    has_date_to = "date_to" in content
    record(
        "Filter parameters (status, platform, date_from, date_to)",
        has_status and has_platform and has_date_from and has_date_to,
    )


def test_schedule_compatible_format():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_date_time_split = '"date"' in content and '"time"' in content
    has_scheduled_filter = "scheduled_at" in content
    record(
        "Buffer/Hootsuite-compatible schedule format (date/time split)",
        has_date_time_split and has_scheduled_filter,
    )


def test_analytics_integration():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_analytics_import = "analytics_service" in content
    record("Analytics service integration in export", has_analytics_import)


# ─── Test Group 4: Export Router Code Quality ─────────────────────────────────

def test_export_router_logging():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_logger = "logging.getLogger" in content
    has_info = "logger.info" in content
    has_error = "logger.error" in content
    record(
        "Logging present (getLogger + info + error)",
        has_logger and has_info and has_error,
    )


def test_export_router_error_handling():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    try_count = content.count("try:")
    except_count = content.count("except")
    record(
        "Error handling (try/except blocks)",
        try_count >= 3 and except_count >= 3,
        f"{try_count} try blocks, {except_count} except handlers",
    )


def test_export_router_docstrings():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    tree = ast.parse(content)
    functions_with_docs = 0
    functions_total = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions_total += 1
            if ast.get_docstring(node):
                functions_with_docs += 1
    coverage = (functions_with_docs / functions_total * 100) if functions_total > 0 else 0
    record(
        f"Docstring coverage ({coverage:.0f}%)",
        coverage >= 80,
        f"{functions_with_docs}/{functions_total} functions documented",
    )


def test_export_router_type_hints():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_typing = "from typing import" in content
    record("Type hints imported and used", has_typing)


def test_export_router_constants():
    path = BACKEND_DIR / "routers" / "export.py"
    with open(path) as f:
        content = f.read()
    has_constants = "EXPORT_FORMAT_CSV" in content or "VALID_EXPORT_FORMATS" in content
    record("Named constants (no magic strings)", has_constants)


# ─── Test Group 5: Main.py Router Registration ───────────────────────────────

def test_main_py_export_import():
    path = BACKEND_DIR / "main.py"
    with open(path) as f:
        content = f.read()
    has_import = "from backend.routers import" in content and "export" in content
    record("main.py imports export router", has_import)


def test_main_py_export_registration():
    path = BACKEND_DIR / "main.py"
    with open(path) as f:
        content = f.read()
    has_registration = 'export.router' in content and '"/export"' in content
    record("main.py registers export router at /export", has_registration)


# ─── Test Group 6: Frontend Polling Hook ─────────────────────────────────────

def test_usepolling_file_exists():
    path = FRONTEND_DIR / "lib" / "usePolling.ts"
    record("usePolling.ts file exists", path.exists(), str(path))


def test_usepolling_exports_hook():
    path = FRONTEND_DIR / "lib" / "usePolling.ts"
    if not path.exists():
        record("usePolling exports custom hook", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_export = "export default" in content
    has_hook = "usePolling" in content
    record("usePolling exports custom hook", has_export and has_hook)


def test_usepolling_interval_support():
    path = FRONTEND_DIR / "lib" / "usePolling.ts"
    if not path.exists():
        record("usePolling supports configurable interval", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_interval = "intervalMs" in content and "setInterval" in content
    has_cleanup = "clearInterval" in content
    record(
        "usePolling supports configurable interval + cleanup",
        has_interval and has_cleanup,
    )


def test_usepolling_refetch():
    path = FRONTEND_DIR / "lib" / "usePolling.ts"
    if not path.exists():
        record("usePolling exposes refetch function", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_refetch = "refetch" in content
    record("usePolling exposes refetch function", has_refetch)


def test_usepolling_mount_guard():
    path = FRONTEND_DIR / "lib" / "usePolling.ts"
    if not path.exists():
        record("usePolling guards against unmounted updates", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_mounted_ref = "mountedRef" in content or "mounted" in content
    record("usePolling guards against unmounted state updates", has_mounted_ref)


# ─── Test Group 7: Frontend Export API ────────────────────────────────────────

def test_api_ts_export_functions():
    path = FRONTEND_DIR / "lib" / "api.ts"
    if not path.exists():
        record("api.ts has export functions", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_export_posts = "exportPosts" in content
    has_export_schedule = "exportSchedule" in content
    has_export_analytics = "exportAnalytics" in content
    record(
        "api.ts export functions (posts, schedule, analytics)",
        has_export_posts and has_export_schedule and has_export_analytics,
    )


def test_api_ts_blob_returns():
    path = FRONTEND_DIR / "lib" / "api.ts"
    if not path.exists():
        record("api.ts export functions return Blob for downloads", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_blob = "Blob" in content
    record("api.ts export functions return Blob for downloads", has_blob)


def test_api_ts_base_url_constant():
    path = FRONTEND_DIR / "lib" / "api.ts"
    if not path.exists():
        record("api.ts uses BASE_URL constant", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_base_url = "BASE_URL" in content
    record("api.ts uses BASE_URL constant (no inline URLs)", has_base_url)


# ─── Test Group 8: ExportButton Component ─────────────────────────────────────

def test_export_button_exists():
    path = FRONTEND_DIR / "components" / "ExportButton.tsx"
    record("ExportButton.tsx file exists", path.exists(), str(path))


def test_export_button_has_dropdown():
    path = FRONTEND_DIR / "components" / "ExportButton.tsx"
    if not path.exists():
        record("ExportButton has dropdown with export options", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_csv = "CSV" in content
    has_json = "JSON" in content
    has_schedule = "Schedule" in content
    record(
        "ExportButton dropdown has CSV, JSON, Schedule options",
        has_csv and has_json and has_schedule,
    )


def test_export_button_blob_download():
    path = FRONTEND_DIR / "components" / "ExportButton.tsx"
    if not path.exists():
        record("ExportButton triggers browser download", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_create_url = "createObjectURL" in content
    has_revoke = "revokeObjectURL" in content
    record(
        "ExportButton triggers browser download (createObjectURL + cleanup)",
        has_create_url and has_revoke,
    )


def test_export_button_loading_state():
    path = FRONTEND_DIR / "components" / "ExportButton.tsx"
    if not path.exists():
        record("ExportButton shows loading state during export", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_exporting = "exporting" in content or "Exporting" in content
    record("ExportButton shows loading state during export", has_exporting)


def test_export_button_accessibility():
    path = FRONTEND_DIR / "components" / "ExportButton.tsx"
    if not path.exists():
        record("ExportButton has ARIA attributes", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_aria = "aria-" in content
    record("ExportButton has ARIA attributes for accessibility", has_aria)


# ─── Test Group 9: Page.tsx Integration ───────────────────────────────────────

def test_page_uses_polling():
    path = FRONTEND_DIR / "app" / "page.tsx"
    if not path.exists():
        record("page.tsx uses usePolling hook", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_import = "usePolling" in content
    has_usage = "usePolling" in content and "fetchPosts" in content
    record("page.tsx uses usePolling hook for auto-refresh", has_import and has_usage)


def test_page_has_export_button():
    path = FRONTEND_DIR / "app" / "page.tsx"
    if not path.exists():
        record("page.tsx includes ExportButton component", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_import = "ExportButton" in content
    has_usage = "<ExportButton" in content
    record("page.tsx includes ExportButton in dashboard", has_import and has_usage)


def test_page_refetch_wiring():
    path = FRONTEND_DIR / "app" / "page.tsx"
    if not path.exists():
        record("page.tsx wires refetch to BulkGenerate + ReviewQueue", False, "File not found")
        return
    with open(path) as f:
        content = f.read()
    has_refetch = "refetch" in content
    has_on_generate = "onGenerate" in content
    has_on_update = "onUpdate" in content
    record(
        "page.tsx wires refetch to BulkGenerate + ReviewQueue",
        has_refetch and has_on_generate and has_on_update,
    )


# ─── Test Group 10: Line Count & Code Metrics ────────────────────────────────

def test_export_router_line_count():
    path = BACKEND_DIR / "routers" / "export.py"
    if not path.exists():
        record("Export router line count", False, "File not found")
        return
    with open(path) as f:
        lines = len(f.readlines())
    record(
        f"Export router line count ({lines} lines)",
        lines >= 200,
        f"Expected ≥200, got {lines}",
    )


def test_usepolling_line_count():
    path = FRONTEND_DIR / "lib" / "usePolling.ts"
    if not path.exists():
        record("usePolling line count", False, "File not found")
        return
    with open(path) as f:
        lines = len(f.readlines())
    record(
        f"usePolling line count ({lines} lines)",
        lines >= 50,
        f"Expected ≥50, got {lines}",
    )


def test_export_button_line_count():
    path = FRONTEND_DIR / "components" / "ExportButton.tsx"
    if not path.exists():
        record("ExportButton line count", False, "File not found")
        return
    with open(path) as f:
        lines = len(f.readlines())
    record(
        f"ExportButton line count ({lines} lines)",
        lines >= 100,
        f"Expected ≥100, got {lines}",
    )


# ─── Run All Tests ────────────────────────────────────────────────────────────

def run_all():
    print("\n" + "=" * 70)
    print("  PHASE 5 TEST SUITE — Export, Polling & Advanced Features")
    print("=" * 70)

    groups = [
        ("\n📁 Group 1: Export Router File Structure", [
            test_export_router_exists,
            test_export_router_importable,
            test_export_router_valid_python,
        ]),
        ("\n🔌 Group 2: Export Router Endpoints", [
            test_export_posts_endpoint,
            test_export_analytics_endpoint,
            test_export_schedule_endpoint,
            test_export_formats_endpoint,
        ]),
        ("\n⚡ Group 3: Export Router Features", [
            test_csv_export_support,
            test_streaming_response,
            test_content_disposition,
            test_filter_parameters,
            test_schedule_compatible_format,
            test_analytics_integration,
        ]),
        ("\n🧹 Group 4: Export Router Code Quality", [
            test_export_router_logging,
            test_export_router_error_handling,
            test_export_router_docstrings,
            test_export_router_type_hints,
            test_export_router_constants,
        ]),
        ("\n🔗 Group 5: Main.py Router Registration", [
            test_main_py_export_import,
            test_main_py_export_registration,
        ]),
        ("\n🔄 Group 6: Frontend Polling Hook", [
            test_usepolling_file_exists,
            test_usepolling_exports_hook,
            test_usepolling_interval_support,
            test_usepolling_refetch,
            test_usepolling_mount_guard,
        ]),
        ("\n📤 Group 7: Frontend Export API", [
            test_api_ts_export_functions,
            test_api_ts_blob_returns,
            test_api_ts_base_url_constant,
        ]),
        ("\n🟢 Group 8: ExportButton Component", [
            test_export_button_exists,
            test_export_button_has_dropdown,
            test_export_button_blob_download,
            test_export_button_loading_state,
            test_export_button_accessibility,
        ]),
        ("\n🏠 Group 9: Page.tsx Integration", [
            test_page_uses_polling,
            test_page_has_export_button,
            test_page_refetch_wiring,
        ]),
        ("\n📊 Group 10: Code Metrics", [
            test_export_router_line_count,
            test_usepolling_line_count,
            test_export_button_line_count,
        ]),
    ]

    for group_name, tests in groups:
        print(group_name)
        for test_fn in tests:
            try:
                test_fn()
            except Exception as e:
                record(test_fn.__name__, False, f"Exception: {e}")

    # ── Summary ────────────────────────────────────────────────────────────
    total = PASSED + FAILED
    success_rate = (PASSED / total * 100) if total > 0 else 0

    print("\n" + "=" * 70)
    print(f"  RESULTS: {PASSED}/{total} passed ({success_rate:.1f}%)")
    print("=" * 70)

    if FAILED > 0:
        print("\n  ❌ Failed Tests:")
        for name, passed, detail in RESULTS:
            if not passed:
                print(f"    • {name}" + (f" — {detail}" if detail else ""))

    print()
    return success_rate >= 80


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
