"""Provision an existing Firebase account in the library database. Never creates passwords."""
import argparse
from firebase_admin import auth
from sqlmodel import Session, select
from app.models import User
from app.db.engine import engine
from app.services.firebase_auth import initialize_firebase

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True)
    parser.add_argument("--role", choices=["student", "staff", "admin"], default="student")
    args = parser.parse_args()
    initialize_firebase()
    account = auth.get_user_by_email(args.email)
    with Session(engine) as session:
        user = session.exec(select(User).where(User.firebase_uid == account.uid)).first()
        if user is None:
            user = session.exec(select(User).where(User.email == account.email)).first()
        if user is None:
            user = User(firebase_uid=account.uid, email=account.email, full_name=account.display_name or account.email)
        user.firebase_uid = account.uid
        user.role = args.role
        user.is_active = True
        session.add(user)
        session.commit()
    print(f"Library account provisioned with role: {args.role}")
