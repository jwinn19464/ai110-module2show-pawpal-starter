from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta

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
    frequency: Optional[str] = None
    pet_name: str = "" # Added for filtering logic

    @property
    def time_minutes(self) -> int:
        """Helper for sorting: minutes since midnight."""
        return self.due_date_time.hour * 60 + self.due_date_time.minute

    def toggle_complete(self):
        """Toggle the task completion status between complete and incomplete."""
        self.is_completed = not self.is_completed

    def mark_complete(self):
        """Mark this task as completed without toggling it back."""
        self.is_completed = True

    def get_recurrence_delta(self) -> Optional[timedelta]:
        """Return the timedelta increment for the task's recurrence frequency."""
        if self.frequency == "daily":
            return timedelta(days=1)
        if self.frequency == "weekly":
            return timedelta(days=7)
        return None

    def create_next_occurrence(self, task_id: int) -> Optional["Task"]:
        """Create the next scheduled task occurrence based on the current frequency."""
        delta = self.get_recurrence_delta()
        if not delta:
            return None

        return Task(
            task_id=task_id,
            name=self.name,
            description=self.description,
            estimated_time=self.estimated_time,
            due_date_time=self.due_date_time + delta,
            priority=self.priority,
            is_completed=False,
            is_reminder_active=False,
            frequency=self.frequency,
            pet_name=self.pet_name,
        )

@dataclass
class Pet:
    pet_id: int
    name: str
    animal_type: str
    breed: str
    age: float
    weight: float
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Assign a new task to this pet and attach the pet's name to the task."""
        task.pet_name = self.name # Syncs pet name to task for filtering
        self.tasks.append(task)

@dataclass
class Owner:
    name: str
    phone: str
    email: str
    daily_time_available: int = 60
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a new pet to the owner's list of managed animals."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Collect every task across all pets into a single list."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

class Scheduler:
    def __init__(self):
        """Initialize scheduler state, including optional planning constraints."""
        self.constraints: List[str] = [] 

    
    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sorts tasks by their due time using a lambda key."""
        return sorted(tasks, key=lambda t: t.due_date_time)

    def filter_tasks(self, tasks: List[Task], status: Optional[bool] = None, pet_name: Optional[str] = None) -> List[Task]:
        """Filters tasks by completion status or specific pet name."""
        filtered = tasks
        if status is not None:
            filtered = [t for t in filtered if t.is_completed == status]
        if pet_name:
            filtered = [t for t in filtered if t.pet_name.lower() == pet_name.lower()]
        return filtered

    def generate_plan(self, owner: Owner) -> Tuple[List[Task], List[str]]:
        """Select tasks that fit within the owner's daily time budget.

        Returns a tuple containing the scheduled tasks and a human-readable explanation.
        """
        available_minutes = owner.daily_time_available
        explanation = []
        selected = []
        
        # Sort by priority (descending) then time (ascending)
        tasks = sorted(owner.get_all_tasks(), key=lambda t: (-t.priority, t.due_date_time))

        for task in tasks:
            if task.is_completed:
                explanation.append(f"Skipped '{task.name}' (already completed).")
                continue
            if task.estimated_time <= available_minutes:
                selected.append(task)
                available_minutes -= task.estimated_time
                explanation.append(f"Scheduled '{task.name}' (Priority {task.priority}).")
            else:
                explanation.append(f"Skipped '{task.name}' (insufficient time).")
        
        return selected, explanation

    def generate_daily_plan(self, owner: Owner) -> str:
        """Build a prioritized, time-aware daily agenda for the owner.

        This method filters to today’s active tasks, computes urgency and score,
        assigns simple time blocks, and returns a human-readable plan.
        """
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        active_tasks = []
        for pet in owner.pets:
            for task in pet.tasks:
                if task.is_completed:
                    continue
                if not (today_start <= task.due_date_time < today_end):
                    continue
                active_tasks.append((pet, task))

        if not active_tasks:
            return "No active tasks scheduled for today!"

        total_minutes = sum(task.estimated_time for _, task in active_tasks)
        workload_note = ""
        if total_minutes > 180:
            workload_note = "⚠️ Heavy day: move lower priority items if possible."
        elif total_minutes > 120:
            workload_note = "⚠️ Moderate workload."

        entries = []
        for pet, task in active_tasks:
            slack = ((task.due_date_time - now).total_seconds() / 60) - task.estimated_time
            urgency = max(0.0, 60.0 - slack) / 15.0
            pet_age_factor = min(max(pet.age / 12.0, 0.0), 3.0)
            score = task.priority * 2.0 + urgency + pet_age_factor

            if task.priority >= 4 and slack <= 60:
                task.is_reminder_active = True

            entries.append({
                "pet": pet,
                "task": task,
                "slack": slack,
                "score": score,
            })

        entries.sort(key=lambda item: (item["slack"], -item["score"], item["pet"].name, item["task"].due_date_time))
        scheduled = self._assign_time_blocks(entries, now)

        lines = [f"--- Daily Plan for {today_start.strftime('%Y-%m-%d')} ---"]
        for item in scheduled:
            task = item["task"]
            pet = item["pet"]
            reminder = " 🔔" if task.is_reminder_active else ""
            conflict = " ⚠️" if item["conflict"] else ""
            lines.append(
                f"{item['start'].strftime('%H:%M')} - {item['end'].strftime('%H:%M')} | P{task.priority}: {task.name} ({pet.name})"
                f"{reminder}{conflict} due {task.due_date_time.strftime('%H:%M')}"
            )

        lines.append(f"\nTotal estimated time: {total_minutes} minutes. {workload_note}")
        lines.append(
            "**Logic:** Uses today’s active tasks, urgency based on deadline slack, weighted score,"
            " and simple time-block placement to avoid unnecessary task switching."
        )
        return "\n".join(lines)

    def _assign_time_blocks(self, entries: List[Dict], now: datetime) -> List[Dict]:
        """Place each scheduled entry into a start/end window and detect conflicts."""
        current = max(now, now.replace(hour=6, minute=0, second=0, microsecond=0))
        scheduled = []
        last_heavy = False

        for item in entries:
            task = item["task"]
            pet = item["pet"]
            start = max(current, now)
            latest_start = task.due_date_time - timedelta(minutes=task.estimated_time)

            if last_heavy and task.estimated_time >= 30:
                start += timedelta(minutes=10)

            if start > latest_start:
                conflict = True
            else:
                conflict = False

            end = start + timedelta(minutes=task.estimated_time)
            scheduled.append({
                "pet": pet,
                "task": task,
                "start": start,
                "end": end,
                "conflict": conflict,
            })
            current = end
            last_heavy = task.estimated_time >= 30

        return scheduled

    def _get_next_task_id(self, owner: Owner) -> int:
        """Compute a new unique task identifier across all owner tasks."""
        tasks = owner.get_all_tasks()
        if not tasks:
            return 1
        return max(task.task_id for task in tasks) + 1

    def mark_task_complete(self, owner: Owner, task_id: int) -> bool:
        """Mark the specified task complete and create its next recurrence if applicable."""
        for pet in owner.pets:
            for task in pet.tasks:
                if task.task_id == task_id:
                    if task.is_completed:
                        return False
                    task.mark_complete()
                    next_task = task.create_next_occurrence(self._get_next_task_id(owner))
                    if next_task:
                        pet.add_task(next_task)
                    return True
        return False

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Check for overlapping task windows and return conflict warnings."""
        warnings = []
        # Sort chronologically to check adjacent overlaps
        ts = self.sort_by_time([t for t in tasks if not t.is_completed])
        
        for i in range(len(ts) - 1):
            curr, nxt = ts[i], ts[i+1]
            # Calculate when the current task ends
            curr_end = curr.due_date_time + timedelta(minutes=curr.estimated_time)
            
            # If the current task ends after the next one starts, it's a conflict
            if curr_end > nxt.due_date_time:
                warning = (f"Conflict: '{curr.name}' ({curr.pet_name}) scheduled at "
                           f"{curr.due_date_time.strftime('%H:%M')} overlaps with "
                           f"'{nxt.name}' ({nxt.pet_name}) at {nxt.due_date_time.strftime('%H:%M')}.")
                warnings.append(warning)
        return warnings