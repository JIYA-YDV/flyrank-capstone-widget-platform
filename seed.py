# seed.py
"""
Seed script — creates demo data for the widget platform.
Run: python seed.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.db.session import SessionLocal, engine, Base
from app.models import User, Widget, Submission
from app.core.security import hash_password
from datetime import datetime, timezone, timedelta
import uuid
import json
import random


def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if already seeded
        existing_user = db.query(User).filter(User.email == "demo@example.com").first()
        if existing_user:
            print("Database already seeded. Clearing and re-seeding...")
            db.query(Submission).delete()
            db.query(Widget).delete()
            db.query(User).delete()
            db.commit()

        # Create demo user
        user = User(
            id=uuid.uuid4(),
            email="demo@example.com",
            hashed_password=hash_password("demo1234"),
            company_name="Demo Corp",
        )
        db.add(user)
        db.flush()
        print(f"Created user: demo@example.com / demo1234  (id: {user.id})")

        # Create a second user (to prove tenant isolation)
        user2 = User(
            id=uuid.uuid4(),
            email="other@example.com",
            hashed_password=hash_password("other1234"),
            company_name="Other Corp",
        )
        db.add(user2)
        db.flush()
        print(f"Created user: other@example.com / other1234  (id: {user2.id})")

        # Create widgets for demo user
        contact_widget = Widget(
            id=uuid.uuid4(),
            owner_id=user.id,
            name="Contact Form",
            widget_type="contact_form",
            title="Get in Touch",
            description="We'd love to hear from you. Fill out the form below.",
            fields_config=[
                {"name": "name", "label": "Full Name", "field_type": "text", "required": True, "placeholder": "John Doe"},
                {"name": "email", "label": "Email Address", "field_type": "email", "required": True, "placeholder": "john@example.com"},
                {"name": "message", "label": "Message", "field_type": "textarea", "required": True, "placeholder": "Your message..."},
            ],
            button_text="Send Message",
            display_options={"theme": "light"},
            allowed_origins=[],
        )
        db.add(contact_widget)
        db.flush()
        print(f"Created widget: Contact Form  (id: {contact_widget.id})")

        signup_widget = Widget(
            id=uuid.uuid4(),
            owner_id=user.id,
            name="Newsletter Signup",
            widget_type="signup_form",
            title="Subscribe to Our Newsletter",
            description="Get the latest updates delivered to your inbox.",
            fields_config=[
                {"name": "email", "label": "Email", "field_type": "email", "required": True, "placeholder": "you@example.com"},
                {"name": "first_name", "label": "First Name", "field_type": "text", "required": False, "placeholder": "Jane"},
            ],
            button_text="Subscribe",
            display_options={"theme": "dark"},
            allowed_origins=[],
        )
        db.add(signup_widget)
        db.flush()
        print(f"Created widget: Newsletter Signup  (id: {signup_widget.id})")

        # Create widget for other user (tenant isolation proof)
        other_widget = Widget(
            id=uuid.uuid4(),
            owner_id=user2.id,
            name="Other Corp Form",
            widget_type="contact_form",
            title="Contact Other Corp",
            fields_config=[
                {"name": "name", "label": "Name", "field_type": "text", "required": True},
                {"name": "email", "label": "Email", "field_type": "email", "required": True},
            ],
            button_text="Submit",
        )
        db.add(other_widget)
        db.flush()
        print(f"Created widget: Other Corp Form  (id: {other_widget.id})")

        # Create sample submissions
        countries = ["United States", "United Kingdom", "Germany", "France", "Canada", "Australia", "Japan", "Brazil"]
        cities = ["New York", "London", "Berlin", "Paris", "Toronto", "Sydney", "Tokyo", "São Paulo"]

        now = datetime.now(timezone.utc)
        for i in range(25):
            country_idx = random.randint(0, len(countries) - 1)
            sub = Submission(
                widget_id=contact_widget.id,
                tenant_id=user.id,
                data={
                    "name": f"Test User {i+1}",
                    "email": f"user{i+1}@example.com",
                    "message": f"This is test message number {i+1}.",
                },
                ip_address=f"203.0.113.{random.randint(1, 254)}",
                country=countries[country_idx],
                city=cities[country_idx],
                region="Test Region",
                geo_provider="seed-data",
                user_agent="Mozilla/5.0 (seed script)",
                created_at=now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
            )
            db.add(sub)

        for i in range(10):
            country_idx = random.randint(0, len(countries) - 1)
            sub = Submission(
                widget_id=signup_widget.id,
                tenant_id=user.id,
                data={
                    "email": f"subscriber{i+1}@example.com",
                    "first_name": f"Subscriber {i+1}",
                },
                ip_address=f"198.51.100.{random.randint(1, 254)}",
                country=countries[country_idx],
                city=cities[country_idx],
                geo_provider="seed-data",
                user_agent="Mozilla/5.0 (seed script)",
                created_at=now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23)),
            )
            db.add(sub)

        db.commit()
        print(f"\nCreated 35 sample submissions")

        # Print useful info
        print("\n" + "=" * 60)
        print("SEED COMPLETE")
        print("=" * 60)
        print(f"\nLogin credentials:")
        print(f"  Email: demo@example.com")
        print(f"  Password: demo1234")
        print(f"\nWidget IDs:")
        print(f"  Contact Form: {contact_widget.id}")
        print(f"  Newsletter:   {signup_widget.id}")
        print(f"\nUpdate test_site/index.html with this widget ID:")
        print(f'  <script src="http://localhost:8000/widget.js?id={contact_widget.id}"></script>')
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()