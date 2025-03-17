"""
Unit tests for Room models.
"""
import unittest
from datetime import datetime
import uuid

from app.models.room import CreateRoom, RoomDB, RoomResponse, RoomUpdate

class TestRoomModels(unittest.TestCase):
    """Test suite for Room models."""

    def test_create_room_valid(self):
        """Test that valid room creation data passes validation."""
        room_data = {
            "name": "Living Room",
            "home_id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "living",
            "floor": 1,
            "size_sqm": 25.5,
            "devices": ["dev1", "dev2"]
        }
        room = CreateRoom(**room_data)
        self.assertEqual(room.name, "Living Room")
        self.assertEqual(room.type, "living")
        self.assertEqual(room.floor, 1)
        self.assertEqual(room.devices, ["dev1", "dev2"])

    def test_create_room_minimal(self):
        """Test that minimal valid room creation data passes validation."""
        room_data = {
            "name": "Kitchen",
            "home_id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "kitchen"
        }
        room = CreateRoom(**room_data)
        self.assertEqual(room.name, "Kitchen")
        self.assertEqual(room.type, "kitchen")
        self.assertEqual(room.floor, 1)  # Default value
        self.assertEqual(room.devices, [])  # Default value

    def test_create_room_invalid_name_too_short(self):
        """Test that a room name that's too short fails validation."""
        room_data = {
            "name": "K",  # Too short
            "home_id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "kitchen"
        }
        with self.assertRaises(ValueError) as context:
            CreateRoom(**room_data)
        self.assertIn("2 characters", str(context.exception))

    def test_create_room_invalid_name_too_long(self):
        """Test that a room name that's too long fails validation."""
        room_data = {
            "name": "K" * 51,  # Too long
            "home_id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "kitchen"
        }
        with self.assertRaises(ValueError) as context:
            CreateRoom(**room_data)
        self.assertIn("50 characters", str(context.exception))

    def test_create_room_invalid_floor_too_low(self):
        """Test that a floor number that's too low fails validation."""
        room_data = {
            "name": "Basement",
            "home_id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "storage",
            "floor": -6  # Too low
        }
        with self.assertRaises(ValueError) as context:
            CreateRoom(**room_data)
        self.assertIn("-5", str(context.exception))

    def test_create_room_invalid_floor_too_high(self):
        """Test that a floor number that's too high fails validation."""
        room_data = {
            "name": "Sky Lounge",
            "home_id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "lounge",
            "floor": 201  # Too high
        }
        with self.assertRaises(ValueError) as context:
            CreateRoom(**room_data)
        self.assertIn("200", str(context.exception))

    def test_room_db_model(self):
        """Test RoomDB model creation with default values."""
        room_db = RoomDB(
            user_id="user123",
            home_id="home123",
            name="Bedroom",
            type="bedroom"
        )
        # Check that ID is a valid UUID (try to parse it, should not raise an error)
        try:
            uuid.UUID(room_db.id)
        except ValueError:
            self.fail("id is not a valid UUID")

        self.assertEqual(room_db.user_id, "user123")
        self.assertEqual(room_db.home_id, "home123")
        self.assertEqual(room_db.name, "Bedroom")
        self.assertEqual(room_db.type, "bedroom")
        self.assertEqual(room_db.floor, 1)  # Default value
        self.assertEqual(room_db.devices, [])  # Default value
        self.assertIsNone(room_db.description)
        self.assertTrue(room_db.active)
        self.assertIsInstance(room_db.created, datetime)
        self.assertIsNone(room_db.updated)

    def test_room_response_model(self):
        """Test RoomResponse model creation."""
        room_response = RoomResponse(
            id="room123",
            name="Dining Room",
            home_id="home123",
            type="dining",
            floor=1,
            created=datetime(2023, 1, 1, 12, 0, 0)
        )
        self.assertEqual(room_response.id, "room123")
        self.assertEqual(room_response.name, "Dining Room")
        self.assertEqual(room_response.home_id, "home123")
        self.assertEqual(room_response.type, "dining")
        self.assertEqual(room_response.floor, 1)
        self.assertEqual(room_response.devices, [])
        self.assertEqual(room_response.created, datetime(2023, 1, 1, 12, 0, 0))

    def test_room_update_valid(self):
        """Test that valid room update data passes validation."""
        update_data = {
            "name": "Updated Room",
            "description": "This is an updated description",
            "floor": 2
        }
        room_update = RoomUpdate(**update_data)
        self.assertEqual(room_update.name, "Updated Room")
        self.assertEqual(room_update.description, "This is an updated description")
        self.assertEqual(room_update.floor, 2)
        self.assertIsNone(room_update.type)
        self.assertIsNone(room_update.devices)

    def test_room_update_invalid_name(self):
        """Test that an invalid name in update data fails validation."""
        update_data = {
            "name": "A"  # Too short
        }
        with self.assertRaises(ValueError) as context:
            RoomUpdate(**update_data)
        self.assertIn("2 characters", str(context.exception))

    def test_room_update_invalid_floor(self):
        """Test that an invalid floor in update data fails validation."""
        update_data = {
            "floor": -10  # Too low
        }
        with self.assertRaises(ValueError) as context:
            RoomUpdate(**update_data)
        self.assertIn("-5", str(context.exception))


if __name__ == "__main__":
    unittest.main()
