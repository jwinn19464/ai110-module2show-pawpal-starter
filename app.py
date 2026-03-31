import streamlit as st
import pandas as pd
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import datetime, timedelta

# --- Step 1: Manage the Application "Memory" ---
if "owner" not in st.session_state:
    # Initialize a default owner with a 2-hour daily time budget
    st.session_state.owner = Owner(
        name="Jenifer", 
        phone="555-0123", 
        email="jenifer@example.com", 
        daily_time_available=120
    )

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# st.markdown(
#     """
# Welcome to the PawPal+ starter app.

# This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
# but **it does not implement the project logic**. Your job is to design the system and build it.

# Use this app as your interactive demo once your backend classes/functions exist.
# """
# )

st.markdown("Optimize your pet care routine with priority-based scheduling and conflict detection.")

# with st.expander("Scenario", expanded=True):
#     st.markdown(
#         """
# **PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
# for their pet(s) based on constraints like time, priority, and preferences.

# You will design and implement the scheduling logic and connect it to this Streamlit UI.
# """
# )

# with st.expander("What you need to build", expanded=True):
#     st.markdown(
#         """
# At minimum, your system should:
# - Represent pet care tasks (what needs to happen, how long it takes, priority)
# - Represent the pet and the owner (basic info and preferences)
# - Build a plan/schedule for a day that chooses and orders tasks based on constraints
# - Explain the plan (why each task was chosen and when it happens)
# """
#     )

st.divider()

# --- Sidebar: System Controls & Debugging ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.owner.daily_time_available = st.number_input(
        "Daily Time Budget (mins)", 
        min_value=15, 
        value=st.session_state.owner.daily_time_available
    )
    
    st.divider()
    if st.button("Reset All Data", type="primary"):
        st.session_state.clear()
        st.rerun()

# --- Section 1: Manage Pets ---
st.subheader("1. Your Pets")
with st.expander("Add a New Pet"):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        new_pet_name = st.text_input("Name", value="Mochi")
        species = st.selectbox("Species", ["dog", "cat", "bird", "other"])
    with col_p2:
        age = st.number_input("Age (years)", min_value=0.1, value=2.0)
        weight = st.number_input("Weight (kg)", min_value=0.1, value=5.0)

    if st.button("Add Pet to Profile"):
        new_pet = Pet(
            pet_id=len(st.session_state.owner.pets) + 1,
            name=new_pet_name,
            animal_type=species,
            breed="Unknown",
            age=age,
            weight=weight
        )
        st.session_state.owner.add_pet(new_pet)
        st.success(f"Successfully added {new_pet_name}!")

if st.session_state.owner.pets:
    pet_cols = st.columns(len(st.session_state.owner.pets))
    for i, p in enumerate(st.session_state.owner.pets):
        with pet_cols[i]:
            st.info(f"**{p.name}**\n\n{p.animal_type.capitalize()}")

st.divider()

# --- Section 2: Manage Tasks & Conflict Detection ---
st.subheader("2. Task Management")

if st.session_state.owner.pets:
    with st.form("task_form"):
        target_pet_name = st.selectbox("Assign to:", [p.name for p in st.session_state.owner.pets])
        
        col1, col2 = st.columns(2)
        with col1:
            task_title = st.text_input("Task Title", value="Morning Walk")
            duration = st.number_input("Duration (minutes)", min_value=1, value=20)
        with col2:
            scheduled_time = st.time_input("Preferred Time", value=datetime.now().time())
            frequency = st.selectbox("Recurrence", ["None", "daily", "weekly"])
            
        priority_str = st.select_slider("Priority", options=["low", "medium", "high"], value="medium")
        
        if st.form_submit_button("Add Task"):
            p_map = {"low": 1, "medium": 3, "high": 5}
            dt = datetime.combine(datetime.now().date(), scheduled_time)
            
            new_task = Task(
                task_id=len(st.session_state.owner.get_all_tasks()) + 1,
                name=task_title,
                description=f"Scheduled for {target_pet_name}",
                estimated_time=int(duration),
                due_date_time=dt,
                priority=p_map[priority_str],
                frequency=None if frequency == "None" else frequency
            )
            
            for p in st.session_state.owner.pets:
                if p.name == target_pet_name:
                    p.add_task(new_task)
            st.rerun()

    # --- Conflict Detection Display ---
    all_tasks = st.session_state.owner.get_all_tasks()
    conflicts = st.session_state.scheduler.detect_conflicts(all_tasks)
    
    if conflicts:
        st.error("### ⚠️ Schedule Overlaps Found")
        for error in conflicts:
            st.warning(error)

    # --- Task Table View ---
    if all_tasks:
        st.write("### Current Task List")
        sorted_tasks = st.session_state.scheduler.sort_by_time(all_tasks)
        
        task_df = pd.DataFrame([{
            "Time": t.due_date_time.strftime("%H:%M"),
            "Pet": t.pet_name,
            "Task": t.name,
            "Mins": t.estimated_time,
            "Priority": t.priority,
            "Freq": t.frequency if t.frequency else "One-time",
            "Done": "✅" if t.is_completed else "⏳"
        } for t in sorted_tasks])
        
        st.table(task_df)

else:
    st.warning("Please add a pet to begin scheduling tasks.")

st.divider()

# --- Section 3: Smart Daily Plan ---
st.subheader("3. Generate Optimized Plan")
st.caption("This uses logic scoring based on urgency, pet age, and time available.")

if st.button("Build Today's Agenda", type="primary"):
    if not st.session_state.owner.pets:
        st.error("No pets found in profile.")
    elif not all_tasks:
        st.error("No tasks found. Add a task above first.")
    else:
        with st.spinner("Calculating optimal blocks..."):
            plan_text = st.session_state.scheduler.generate_daily_plan(st.session_state.owner)
            
            st.markdown("### 🗓️ Your Smart Schedule")
            if "⚠️" in plan_text:
                st.warning("Note: High workload or conflicts detected in this plan.")
                
            st.text_area("Daily Agenda Details", value=plan_text, height=350)
            st.balloons()