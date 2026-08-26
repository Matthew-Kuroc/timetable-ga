from __future__ import annotations

import argparse
import json
from pathlib import Path

from backend.app.db.models import AppUserModel
from backend.app.db.session import get_session_local
from backend.app.services.user_service import provision_lecturer_accounts


def main() -> int:
    parser = argparse.ArgumentParser(description="Cấp tài khoản Lecturer từ batch đã xác nhận.")
    parser.add_argument("--lecturer-code", action="append", dest="lecturer_codes", default=[])
    parser.add_argument("--all-lecturers", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(".tmp/lecturer-credentials.json"))
    args = parser.parse_args()
    if not args.all_lecturers and not args.lecturer_codes:
        parser.error("Cần --lecturer-code hoặc --all-lecturers")
    with get_session_local()() as session:
        actor = session.query(AppUserModel).filter(AppUserModel.role == "ADMIN", AppUserModel.active.is_(True)).first()
        if actor is None:
            parser.error("Chưa có tài khoản ADMIN đang hoạt động.")
        if args.dry_run:
            from backend.app.services.runtime_store import list_confirmed_lecturers
            catalog = list_confirmed_lecturers()
            available = {str(item.get("lecturer_code")) for item in catalog.get("lecturers", []) if isinstance(item, dict)}
            selected = available if args.all_lecturers else set(args.lecturer_codes)
            existing = {str(item.lecturer_code) for item in session.query(AppUserModel).filter(AppUserModel.lecturer_code.is_not(None)).all()}
            print(json.dumps({"batch_code": catalog.get("batch_code"), "would_create": sorted(selected - existing), "would_skip": sorted(selected & existing)}, ensure_ascii=False, indent=2))
            return 0
        result = provision_lecturer_accounts(actor=actor, lecturer_codes=args.lecturer_codes, all_lecturers=args.all_lecturers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"batch_code": result.get("batch_code"), "created": len(result["created"]), "skipped": len(result["skipped"]), "conflicts": len(result["conflicts"]), "credentials_file": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
