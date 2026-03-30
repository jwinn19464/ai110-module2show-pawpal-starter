from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Task:
    """Represents a single actionable care item."""
    task_id: int
    name: str
    description: str
    estimated_time: int  # in minutes
    due_date_time: datetime
    priority: int = 1  # Task weight
    is_completed: bool = False
    is_reminder_active: bool = False

    def toggle_complete(self):
        """Mark task as finished or unfinished."""
        pass

    def update_priority(self, new_priority: int):
        """Change the weight/importance of the task."""
        pass

    def set_reminder(self, status: bool):
        """Toggle alerts for this specific task."""
        pass


@dataclass
class Pet:
    """Stores biological data and acts as a profile container for an animal."""
    pet_id: int
    name: str
    animal_type: str
    breed: str
    age: float
    weight: float
    photo_url: Optional[str] = None
    base_requirements: List[Task] = field(default_factory=list)

    def get_profile(self) -> str:
        """Return a formatted summary of the pet's info."""
        pass

    def update_weight(self, new_weight: float):
        """Update the pet's physical records."""
        pass


@dataclass
class User:
    """Top-level manager for the account and pet collection."""
    name: str
    phone: str
    email: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a new pet profile to the user."""
        pass

    def delete_pet(self, pet_id: int):
        """Remove a pet and its associated data."""
        pass

    def update_profile(self, **kwargs):
        """Modify owner contact information."""
        pass


class DailyPlanner:
    """The logic engine that organizes tasks and explains the 'why'."""
    def __init__(self, current_date: datetime):
        self.current_date = current_date
        self.active_tasks: List[Task] = []
        self.constraints: List[str] = [] # e.g., "Work from 9-5", "No car today"
        self.behavior_log: dict = {} # Tracks pet habits over time

    def add_task(self, task: Task):
        """Add a specific instance of a task to today's schedule."""
        pass

    def modify_task(self, task_id: int, **updates):
        """Edit details of an existing task in the planner."""
        pass

    def delete_task(self, task_id: int):
        """Remove a task from the daily agenda."""
        pass

    def generate_daily_plan(self) -> str:
        """
        Sorts tasks by weight and constraints.
        Returns the plan plus the explanation of why tasks are ordered this way.
        """
        pass

    def track_behavior(self, pet_id: int, notes: str):
        """Logs pet behavior observations to refine future planning."""
        pass