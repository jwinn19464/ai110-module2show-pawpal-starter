import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler
from datetime import datetime, timedelta

# Step 2: Manage the Application "Memory"
# Initialize the persistent "vault" for our objects so they survive reruns
if "owner" not in st.session_state:
    # Creating a default owner based on the initial scenario
    st.session_state.owner = Owner(name="Jordan", phone="555-0123", email="jordan@example.com")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
)

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Step 3: Wiring UI Actions to Logic - Managing Pets
st.subheader("1. Manage Pets")
col_p1, col_p2 = st.columns(2)
with col_p1:
    new_pet_name = st.text_input("Pet Name", value="Mochi")
with col_p2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet to Profile"):
    # Create a new Pet object and add it to the Owner in session_state
    new_pet = Pet(
        pet_id=len(st.session_state.owner.pets) + 1,
        name=new_pet_name,
        animal_type=species,
        breed="Unknown",
        age=1.0,
        weight=5.0
    )
    st.session_state.owner.add_pet(new_pet)
    st.success(f"{new_pet_name} added! Total pets: {len(st.session_state.owner.pets)}")

if st.session_state.owner.pets:
    st.write("Your Pets:")
    for p in st.session_state.owner.pets:
        st.info(p.get_profile()) # Uses the method from your logic layer

st.divider()

st.subheader("2. Add Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

# Select which pet to assign the task to
if st.session_state.owner.pets:
    target_pet_name = st.selectbox("Assign task to:", [p.name for p in st.session_state.owner.pets])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority_str = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    if st.button("Add task"):
        # Map UI strings to our backend priority weights
        p_map = {"low": 1, "medium": 3, "high": 5}
        
        # Create the Task object
        new_task = Task(
            task_id=len(st.session_state.owner.get_all_tasks()) + 1,
            name=task_title,
            description=f"Scheduled task for {target_pet_name}",
            estimated_time=int(duration),
            due_date_time=datetime.now() + timedelta(hours=2), # Default to 2 hours from now
            priority=p_map[priority_str]
        )
        
        # Find the correct pet and add the task
        for p in st.session_state.owner.pets:
            if p.name == target_pet_name:
                p.add_task(new_task)
                st.success(f"Added '{task_title}' for {target_pet_name}")
else:
    st.warning("Please add a pet before assigning tasks.")

st.divider()

# Step 3: Wiring UI Actions to Logic - Generating the Schedule
st.subheader("3. Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not st.session_state.owner.pets or not st.session_state.owner.get_all_tasks():
        st.error("You need at least one pet and one task to generate a plan.")
    else:
        # Call the Scheduler "Brain" to process the Owner's data
        with st.spinner("Calculating optimal schedule..."):
            schedule_results = st.session_state.scheduler.generate_daily_plan(st.session_state.owner)
            
            st.markdown("### 🗓️ Your Daily Care Plan")
            st.code(schedule_results, language="text") # Display the prioritized list and logic
            
            st.balloons()

# Debugging: Show the raw data currently in the "Vault"
with st.sidebar:
    st.header("System Internals")
    if st.checkbox("Show Session State"):
        st.write("Owner Object:", st.session_state.owner)
    if st.button("Reset App"):
        st.session_state.clear()
        st.rerun()