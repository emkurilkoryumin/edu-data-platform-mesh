from __future__ import annotations

import json
import os
import random
import time
import uuid
from datetime import UTC, datetime

from kafka import KafkaProducer


EVENT_TYPES = ["artwork_viewed", "artwork_liked", "comment_added", "submission_started", "virtual_room_entered"]
EXHIBITIONS = ["spring_colors", "city_dreams", "animals_and_friends", "digital_future"]
ROOMS = ["main_hall", "watercolor_room", "digital_room", "mentor_choice"]


def build_event() -> dict[str, object]:
    event_type = random.choices(EVENT_TYPES, weights=[60, 18, 8, 6, 8], k=1)[0]
    return {
        "event_id": str(uuid.uuid4()),
        "event_ts": int(datetime.now(UTC).timestamp() * 1000),
        "event_type": event_type,
        "visitor_id": f"visitor_{random.randint(1, 700):05d}",
        "artist_id": f"artist_{random.randint(1, 80):04d}",
        "artwork_id": f"art_{random.randint(1, 2000):05d}",
        "exhibition_id": random.choice(EXHIBITIONS),
        "room_id": random.choice(ROOMS),
        "session_id": f"session_{random.randint(1, 200):05d}",
        "source_system": "online_gallery_web",
    }


def main() -> None:
    topic = os.getenv("KAFKA_EVENTS_TOPIC", "gallery.events")
    bootstrap_servers = os.getenv("KAFKA_PUBLIC_BOOTSTRAP_SERVERS") or os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
    )
    delay_seconds = float(os.getenv("GENERATOR_DELAY_SECONDS", "0.25"))

    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        linger_ms=50,
    )

    try:
        while True:
            event = build_event()
            producer.send(topic, value=event)
            print(json.dumps(event, ensure_ascii=False))
            time.sleep(delay_seconds)
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()

