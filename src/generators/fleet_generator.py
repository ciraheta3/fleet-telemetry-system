import json
import uuid
import random
from datetime import datetime, timezone
from pathlib import Path
from faker import Faker
from src.models.telemetry import FleetTelemetryEvent

fake = Faker()

class FleetDataGenerator:
    def __init__(self, vehicle_count: int = 10):
        self.vehicles = [f"VEH-{1000 + i}" for i in range(vehicle_count)]
        self.drivers = [f"DRV-{5000 + i}" for i in range(vehicle_count)]
        self.status_options = ["IN_TRANSIT", "IN_TRANSIT", "IDLE", "MAINTENANCE_REQUIRED"]

    def generate_event(self) -> FleetTelemetryEvent:
        idx = random.randint(0, len(self.vehicles) - 1)
        return FleetTelemetryEvent(
            event_id=str(uuid.uuid4()),
            vehicle_id=self.vehicles[idx],
            driver_id=self.drivers[idx],
            timestamp=datetime.now(timezone.utc),
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude()),
            speed_mph=round(random.uniform(0.0, 75.0), 2),
            fuel_level_pct=round(random.uniform(10.0, 100.0), 2),
            engine_temp_f=round(random.uniform(180.0, 220.0), 1),
            status=random.choice(self.status_options)
        )

    def write_batch_to_json(self, output_path: str, batch_size: int = 50):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        events = [self.generate_event().model_dump(mode='json') for _ in range(batch_size)]
        
        with open(path, "w") as f:
            json.dump(events, f, indent=2)
        print(f"Successfully generated {batch_size} events at {output_path}")

if __name__ == "__main__":
    generator = FleetDataGenerator(vehicle_count=5)
    generator.write_batch_to_json("data/raw/telemetry_batch_1.json", batch_size=20)