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

if __name__ == "__main__":
    unittest.main()