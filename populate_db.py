import os
import django
import random
from faker import Faker

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')  # <-- change this
django.setup()

from events.models import Participant, Category, Event


def populate_db():
    fake = Faker()

    # --- Create Categories (fixed choices) ---
    categories = []
    for key, label in Category.CATEGORY_CHOICES:
        category, created = Category.objects.get_or_create(
            name=key,
            defaults={"description": f"{label} related events"}
        )
        categories.append(category)
    print(f"Ensured {len(categories)} categories.")

    # --- Create Participants ---
    participants = []
    for _ in range(20):
        participant, _ = Participant.objects.get_or_create(
            email=fake.unique.email(),
            defaults={"name": fake.name()}
        )
        participants.append(participant)
    print(f"Created {len(participants)} participants.")

    # --- Create Events ---
    events = []
    for _ in range(15):
        event = Event.objects.create(
            name=fake.sentence(nb_words=3),
            description=fake.text(max_nb_chars=200),
            date=fake.date_between(start_date='-30d', end_date='+30d'),
            time=fake.time(),
            location=fake.city(),
            category=random.choice(categories)
        )
        # Assign random participants (1–5)
        event.included_in.set(random.sample(participants, random.randint(1, 5)))
        events.append(event)

    print(f"Created {len(events)} events.")
    print("✅ Database populated successfully!")


if __name__ == "__main__":
    populate_db()

