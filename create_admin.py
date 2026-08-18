from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import get_settings
from backend.app.db.models import UserModel, UserRole
from backend.app.core.security import get_password_hash

settings = get_settings()
engine = create_engine(str(settings.database_url))
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = Session()

test_users = [
    {"username": "admin", "role": UserRole.ADMIN, "code": None},
    {"username": "pdt", "role": UserRole.TRAINING_OFFICE, "code": None},
    {"username": "gv001", "role": UserRole.LECTURER, "code": "GV001"} 
]

try:
    for u in test_users:
        existing_user = db.query(UserModel).filter(UserModel.username == u["username"]).first()
        if not existing_user:
            new_user = UserModel(
                username=u["username"],
                hashed_password=get_password_hash("123456"),
                role=u["role"],
                is_active=True,
                lecturer_code=u["code"]
            )
            db.add(new_user)
            print(f" Đã tạo tài khoản: {u['username']} (Role: {u['role'].value})")
        else:
            print(f" Tài khoản {u['username']} đã tồn tại.")
            
    db.commit()
    print(" Hoàn tất việc tạo tài khoản test!")
except Exception as e:
    print(f"Có lỗi xảy ra: {e}")
finally:
    db.close()