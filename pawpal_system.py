from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class Task:
    """Represents a single actionable care item with priority and status."""
    task_id: int
    name: str
    description: str
    estimated_time: int  # in minutes
    due_date_time: datetime
    priority: int = 1  # 1 (Low) to 5 (High)
    is_completed: bool = False
    is_reminder_active: bool = False

    def toggle_complete(self):
        """Switches the completion status of the task between True and False."""
        self.is_completed = not self.is_completed

    def update_priority(self, new_priority: int):
        """Sets a new numerical priority weight for the task."""
        self.priority = new_priority

    def set_reminder(self, status: bool):
        """Enables or disables the notification alert for this task."""
        self.is_reminder_active = status


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
    tasks: List[Task] = field(default_factory=list)

    def get_profile(self) -> str:
        """Generates a string summary of the pet's identity and current task load."""
        return (f"Profile: {self.name} | {self.breed} ({self.animal_type})\n"
                f"Age: {self.age} | Weight: {self.weight}kg\n"
                f"Active Tasks: {len([t for t in self.tasks if not t.is_completed])}")

    def update_weight(self, new_weight: float):
        """Updates the stored body weight for the pet's health records."""
        self.weight = new_weight

    def add_task(self, task: Task):
        """Appends a new care task to the pet's specific requirements list."""
        self.tasks.append(task)


@dataclass
class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    name: str
    phone: str
    email: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Adds a new pet object to the owner's managed collection."""
        self.pets.append(pet)

    def delete_pet(self, pet_id: int):
        """Filters out a pet from the collection based on its unique ID."""
        self.pets = [p for p in self.pets if p.pet_id != pet_id]

    def get_all_tasks(self) -> List[Task]:
        """Collects every task assigned across all pets into a single list."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    """The 'Brain' that retrieves, organizes, and manages tasks across pets."""
    def __init__(self):
        """Initializes the scheduler with empty constraints and behavior logs."""
        self.constraints: List[str] = [] 
        self.behavior_log: Dict[int, List[str]] = {}

    def generate_daily_plan(self, owner: Owner) -> str:
        """Creates a prioritized, time-sorted agenda with an explanation of the logic."""
        tasks = owner.get_all_tasks()
        if not tasks:
            return "No tasks scheduled for today!"

        sorted_tasks = sorted(
            tasks, 
            key=lambda x: (x.is_completed, -x.priority, x.due_date_time)
        )

        plan_output = [f"--- Daily Plan for {datetime.now().strftime('%Y-%m-%d')} ---"]
        for task in sorted_tasks:
            status = "[X]" if task.is_completed else "[ ]"
            plan_output.append(f"{status} P{task.priority}: {task.name} ({task.estimated_time} min) @ {task.due_date_time.strftime('%H:%M')}")
        
        plan_output.append("\n**Logic:** High-priority (P5) health and feeding tasks are ranked first, followed by time-sensitive items.")
        return "\n".join(plan_output)

    def track_behavior(self, pet_id: int, note: str):
        """Records a timestamped observation about a pet's habits or health."""
        if pet_id not in self.behavior_log:
            self.behavior_log[pet_id] = []
        self.behavior_log[pet_id].append(f"{datetime.now()}: {note}")

    def modify_task_in_system(self, owner: Owner, task_id: int, **updates):
        """Locates a specific task by ID within the owner's pets and applies updates."""
        for pet in owner.pets:
            for task in pet.tasks:
                if task.task_id == task_id:
                    for key, value in updates.items():
                        setattr(task, key, value)
                    return True
        return False