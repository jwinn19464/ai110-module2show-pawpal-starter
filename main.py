from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Jenifer Nguyen", daily_time_available=120)

# Kora (Yorkie) and Gertrude (Calico)
pet1 = Pet("Kora", "Dog")
pet2 = Pet("Gertrude", "Cat")

# 1. Adding tasks with Weights (Priority) and Time
task1 = Task("Morning walk", duration_minutes=30, priority=8, time=480, pet_name=pet1.name) # 8:00 AM
task2 = Task("Feed Kora", duration_minutes=10, priority=10, time=490, pet_name=pet1.name)   # 8:10 AM
task3 = Task("Clean litter box", duration_minutes=10, priority=5, time=540, pet_name=pet2.name) 
task4 = Task("Brush Gertrude", duration_minutes=15, priority=3, time=1140, pet_name=pet2.name) # 7:00 PM

pet1.add_task(task1)
pet1.add_task(task2)
pet2.add_task(task3)
pet2.add_task(task4)

owner.add_pet(pet1)
owner.add_pet(pet2)

scheduler = Scheduler()

# -------------------------
# 2. DYNAMIC SCHEDULING & REASONING
# -------------------------
# Urgency Score P = W / (Time_Until_Due), priority weight W is assigned based on task importance (e.g., feeding = 10, grooming = 3)
plan, explanation = scheduler.generate_plan(owner)

print("=== PawPal+ Smart Schedule ===")
total = 0
for task in plan:
    status = "✅" if task.completed else "⏳"
    print(f"{status} [#{task.number}] {task.description} - {task.duration_minutes} min (Priority Weight: {task.priority})")
    total += task.duration_minutes

print(f"\nTotal scheduled time: {total} min (Limit: {owner.daily_time_available} min)\n")

print("=== Reasoning (Logic Improvements) ===")
for line in explanation:
    print("-", line)

# -------------------------
# 3. RELATIVE RECURRENCE (SLIDING WINDOW)
# -------------------------
print("\n=== Mark Task Complete (Relative Recurrence) ===")
# Frequency triggers logic to schedule the NEXT task relative to completion time
daily_meds = Task("Heartworm Meds", duration_minutes=5, priority=10, time=600, pet_name=pet1.name, frequency="daily")
pet1.add_task(daily_meds)

print(f"Before: {daily_meds.description} due at {daily_meds.time} min")

# Logic: Next dose = Now + Interval (1440 mins for daily)
result_daily = scheduler.mark_task_complete(owner, daily_meds.number)

# Find the newly generated recurring task
new_tasks = [t for t in pet1.get_tasks() if t.description == "Heartworm Meds" and not t.completed]
if new_tasks:
    print(f"After: Next {new_tasks[0].description} automatically moved to {new_tasks[0].time} min (24h from now)")

print("=== Detect Conflicts (Overlapping Windows) ===")

# Task 1: Starts at 9:20 AM, lasts 20 mins (Ends at 9:40 AM)
time1 = datetime.now().replace(hour=9, minute=20, second=0, microsecond=0)
conflict_task1 = Task(task_id=101, name="Deep Clean Kennel", description="Scrubbing", 
                      estimated_time=20, due_date_time=time1, priority=3, pet_name=pet1.name)

# Task 2: Starts at 9:30 AM (This overlaps with Task 1)
time2 = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
conflict_task2 = Task(task_id=102, name="Nail trim", description="Clipping", 
                      estimated_time=15, due_date_time=time2, priority=3, pet_name=pet2.name)

pet1.add_task(conflict_task1)
pet2.add_task(conflict_task2)

# Run detection logic
warnings = scheduler.detect_conflicts(owner.get_all_tasks())

if not warnings:
    print("No conflicts detected.")
else:
    for warning in warnings:
        print(f"CONFLICT! {warning}")