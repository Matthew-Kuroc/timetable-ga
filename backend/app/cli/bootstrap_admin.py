from __future__ import annotations

import argparse
import getpass
import sys
from collections.abc import Sequence

from backend.app.services.user_service import (
    AccountConflictError,
    AccountValidationError,
    bootstrap_admin,
)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Tạo tài khoản ADMIN đầu tiên mà không dùng mật khẩu mặc định.",
    )
    parser.add_argument("--username", required=True, help="Tên đăng nhập quản trị viên.")
    parser.add_argument("--display-name", required=True, help="Tên hiển thị quản trị viên.")
    args = parser.parse_args(argv)

    password = getpass.getpass("Mật khẩu: ")
    confirmation = getpass.getpass("Nhập lại mật khẩu: ")
    if password != confirmation:
        print("Mật khẩu nhập lại không khớp.", file=sys.stderr)
        return 1

    try:
        user = bootstrap_admin(
            username=args.username,
            display_name=args.display_name,
            password=password,
        )
    except (AccountConflictError, AccountValidationError) as error:
        print(str(error), file=sys.stderr)
        return 1
    print(f"Đã tạo tài khoản ADMIN: {user.username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
