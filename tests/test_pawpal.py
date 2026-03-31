import unittest
from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler

class TestPawPal(unittest.TestCase):

    def setUp(self):
        """Set up a standard task and pet for testing."""
        self.sample_task = Task(
            task_id=1,
            name="Feeding",
            description="Give 1 cup of kibble",
            estimated_time=10,
            due_date_time=datetime.now(),
            priority=5
        )
        self.sample_pet = Pet(
            pet_id=101,
            name="Barnaby",
            animal_type="Dog",
            breed="Golden Retriever",
            age=10.5,
            weight=32.0
        )

    def test_task_completion(self):
        """Verify that calling toggle_complete() actually changes the task's status."""
        # Ensure it starts as False
        self.assertFalse(self.sample_task.is_completed)
        
        # Act: Toggle the completion status
        self.sample_task.toggle_complete()
        
        # Assert: Check that it is now True
        self.assertTrue(self.sample_task.is_completed)
        
        # Act again: Toggle back to False
        self.sample_task.toggle_complete()
        self.assertFalse(self.sample_task.is_completed)

    def test_task_addition(self):
        """Verify that adding a task to a Pet increases that pet's task count."""
        # Initial state should be 0
        self.assertEqual(len(self.sample_pet.tasks), 0)
        
        # Act: Add the task to the pet
        self.sample_pet.add_task(self.sample_task)
        
        # Assert: Count should now be 1
        self.assertEqual(len(self.sample_pet.tasks), 1)
        self.assertIn(self.sample_task, self.sample_pet.tasks)

    def test_mark_daily_recurring_task_creates_next_instance(self):
        owner = Owner(name="Jen", phone="123", email="jen@example.com")
        pet = self.sample_pet
        self.sample_task.frequency = "daily"
        pet.add_task(self.sample_task)
        owner.add_pet(pet)

        scheduler = Scheduler()
        self.assertTrue(scheduler.mark_task_complete(owner, self.sample_task.task_id))

        self.assertTrue(self.sample_task.is_completed)
        all_tasks = owner.get_all_tasks()
        self.assertEqual(len(all_tasks), 2)

        next_task = [task for task in all_tasks if task.task_id != self.sample_task.task_id][0]
        self.assertFalse(next_task.is_completed)
        self.assertEqual(next_task.frequency, "daily")
        self.assertEqual(next_task.due_date_time, self.sample_task.due_date_time + timedelta(days=1))

    def test_generate_daily_plan_ignores_completed_tasks(self):
        owner = Owner(name="Jen", phone="123", email="jen@example.com")
        pet = self.sample_pet
        completed_task = Task(
            task_id=2,
            name="Check water",
            description="Refill bowl",
            estimated_time=5,
            due_date_time=datetime.now(),
            priority=3,
            is_completed=True,
        )
        pet.add_task(completed_task)
        owner.add_pet(pet)

        scheduler = Scheduler()
        plan = scheduler.generate_daily_plan(owner)
        self.assertEqual(plan, "No active tasks scheduled for today!")

    def test_sorting_correctness(self):
        """Verify tasks are returned in chronological order by due_date_time."""
        scheduler = Scheduler()
        time_now = datetime.now()
        task_later = Task(2, "Evening Walk", "Walk", 20, time_now + timedelta(hours=2))
        task_sooner = Task(3, "Morning Feed", "Feed", 10, time_now + timedelta(hours=1))
        
        sorted_tasks = scheduler.sort_by_time([task_later, task_sooner])
        
        # Assert ascending order
        self.assertEqual(sorted_tasks[0].task_id, 3)
        self.assertEqual(sorted_tasks[1].task_id, 2)

    def test_generate_plan_priority_and_time_tradeoff(self):
        """Verify generate_plan prefers higher priority, then earlier time."""
        owner = Owner("Jen", "123", "jen@example.com", daily_time_available=30)
        pet = self.sample_pet
        # High priority but later
        task_high_priority = Task(1, "Meds", "Give pill", 10, datetime.now() + timedelta(hours=5), priority=5)
        # Lower priority but sooner
        task_low_priority = Task(2, "Brush", "Grooming", 10, datetime.now() + timedelta(hours=1), priority=2)
        
        pet.add_task(task_high_priority)
        pet.add_task(task_low_priority)
        owner.add_pet(pet)
        
        scheduler = Scheduler()
        plan, _ = scheduler.generate_plan(owner)
        
        # Should pick high priority first regardless of time
        self.assertEqual(plan[0].task_id, 1)

    def test_recurrence_logic_weekly(self):
        """Confirm weekly recurrence creates a new task +7 days later."""
        owner = Owner("Jen", "123", "jen@example.com")
        self.sample_task.frequency = "weekly"
        self.sample_pet.add_task(self.sample_task)
        owner.add_pet(self.sample_pet)
        
        scheduler = Scheduler()
        scheduler.mark_task_complete(owner, self.sample_task.task_id)
        
        all_tasks = owner.get_all_tasks()
        next_task = [t for t in all_tasks if t.task_id != self.sample_task.task_id][0]
        
        # Assert +7 days
        expected_time = self.sample_task.due_date_time + timedelta(days=7)
        self.assertEqual(next_task.due_date_time, expected_time)

    def test_conflict_detection_flagging(self):
        """Verify that the Scheduler flags overlapping task durations."""
        start_time = datetime.now().replace(hour=10, minute=0)
        # Task 1: 10:00 to 10:30
        task1 = Task(1, "Long Groom", "Bath", 30, start_time, pet_name="Barnaby")
        # Task 2: 10:20 (Starts before Task 1 ends)
        task2 = Task(2, "Quick Feed", "Kibble", 10, start_time + timedelta(minutes=20), pet_name="Barnaby")
        
        scheduler = Scheduler()
        warnings = scheduler.detect_conflicts([task1, task2])
        
        # Should detect one conflict
        self.assertEqual(len(warnings), 1)
        self.assertIn("overlaps with", warnings[0])

    def test_conflict_detection_no_overlap_at_boundary(self):
        """Tasks ending exactly when the next starts should not conflict."""
        start_time = datetime.now().replace(hour=10, minute=0)
        task1 = Task(1, "Task A", "Desc", 30, start_time)
        task2 = Task(2, "Task B", "Desc", 10, start_time + timedelta(minutes=30))
        
        scheduler = Scheduler()
        warnings = scheduler.detect_conflicts([task1, task2])
        
        # 10:30 end vs 10:30 start is not a conflict in this logic
        self.assertEqual(len(warnings), 0)

    def test_daily_plan_time_boundaries(self):
        """Ensure tasks exactly at today_end are excluded from daily plan."""
        owner = Owner("Jen", "123", "jen@example.com")
        now = datetime.now()
        today_end = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Task exactly at midnight tomorrow
        edge_task = Task(3, "Late Task", "Midnight", 5, today_end, priority=3)
        self.sample_pet.add_task(edge_task)
        owner.add_pet(self.sample_pet)
        
        scheduler = Scheduler()
        plan_str = scheduler.generate_daily_plan(owner)
        
        # Should be excluded based on 'task.due_date_time < today_end' logic
        self.assertEqual(plan_str, "No active tasks scheduled for today!")

    def test_reminder_logic_activation(self):
        """Verify priority >= 4 and slack <= 60 sets is_reminder_active."""
        owner = Owner("Jen", "123", "jen@example.com")
        now = datetime.now()
        # High priority task due in 30 minutes (slack < 60)
        urgent_task = Task(4, "Emergency Meds", "Urgent", 10, now + timedelta(minutes=30), priority=5)
        
        self.sample_pet.add_task(urgent_task)
        owner.add_pet(self.sample_pet)
        
        scheduler = Scheduler()
        # Daily plan execution triggers reminder logic
        scheduler.generate_daily_plan(owner)
        
        self.assertTrue(urgent_task.is_reminder_active)
if __name__ == "__main__":
    unittest.main()