import os
import django
import random
from faker import Faker
from datetime import date, timedelta

# --- Set up Django environment ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Participant, Category, Event


def populate_db():
    fake = Faker()

    # --- 1. Ensure some sample Categories exist ---
    sample_category_names = ['Conference', 'Workshop', 'Seminar', 'Webinar', 'Meetup']
    categories = []
    for name in sample_category_names:
        category, _ = Category.objects.get_or_create(
            name=name,
            defaults={"description": f"{name} related events"}
        )
        categories.append(category)
    print(f"Ensured {len(categories)} categories.")

    # --- 2. Create Participants ---
    participants = []
    for _ in range(20):
        participant, _ = Participant.objects.get_or_create(
            email=fake.unique.email(),
            defaults={"name": fake.name()}
        )
        participants.append(participant)
    print(f"Created {len(participants)} participants.")

    # --- 3. Create Events ---
    events = []
    for _ in range(15):
        event_date = date.today() + timedelta(days=random.randint(0, 30))  # today + 30 days
        event = Event.objects.create(
            name=fake.sentence(nb_words=3),
            description=fake.text(max_nb_chars=200),
            date=event_date,
            time=fake.time(),
            location=fake.city(),
            category=random.choice(categories)
        )
    # Assign random participants (1–5)
    event.participants.set(random.sample(participants, random.randint(1, 5)))
        events.append(event)

    print(f"Created {len(events)} events.")
    print("✅ Database populated successfully!")


if __name__ == "__main__":
    populate_db()
