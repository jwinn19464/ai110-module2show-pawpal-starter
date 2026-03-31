# PawPal+ Project Reflection

Notes:
1. Track pet care tasks
    - add a pet to track
    - select pet to track
    - assign tasks needed for each pet
    - mark completion of tasks (tap/click checkmark)
    - set priority of each task
    - set date and time of each task
        -toggle reminders/alerts for each task
    - add/modify/delete tasks
2. Create and manage a profile
    - Owner enters their own info (name, phone, email)
    - Owner enters pet information (animal, breed/type, age (estimated if unknown), weight, photo (optional))
    -Each pet has their own profile
    -User can look at each pet profile upon selecting the pet's icon
3. Produce a daily plan and explain why
    - assign task weights
    - track behavior over time
    - considers constraints


## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

- What classes did you include, and what responsibilities did you assign to each?

Initially, I have the Owner, Pet, Task, and Planner classes. Users manage Pets and Tasks are assigned to each Pet. 
The Owner class includes the owner information and availability.
Pet includes information such as species, breed, age, weight, and any special care instructions.
Each Task has attributes of Name, Estimated_Duration, When_To_Do, Priority, Category and Short Description (optional). 
The Planner is in charge of producing a daily plan and explaining why it's the optimal plan. It should track the behavior/user inputs over time and consider it when planning and optimizing.
It considers weights and constraints given and learned when planning and scheduling tasks. There should also be a function for users to manually add/delete tasks.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
I decided not to implement behavior tracking over time that was intended to optimize scheduling as that added unnecessary complexity to the project.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The constraints considered are daily time available, priority, task duration and scheduled time.
The scheduler 
- How did you decide which constraints mattered most?
Priority along with owner's available time mattered most as the most important tasks must be completed without exceeding the time that the owner has available for the day.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The system assumes that tasks must be done sequentially and does not account for tasks that can be done simultaneously.
- Why is that tradeoff reasonable for this scenario?
It is a reasonable tradeoff to avoid having the system become too unnecessarily complex.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI to help me with brainstorming and refining ideas, debugging and refactoring, and to generate test cases.

- What kinds of prompts or questions were most helpful?
The most helpful questions were those that helped verify the algorithmic logic as well as simplify it.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
I did not accept a suggestion as-is if I cannot understand it due to the unnecessary complexity that was being added.

- How did you evaluate or verify what the AI suggested?
I evaluate the suggestions by reading project requirements, running test cases, and seeing what makes sense and what doesn't.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested task sorting, plan priority and time tradeoff for the scheduling logic, recurring task logic, and conflict detection.
  
- Why were these tests important?
These tests were important as they verify that the system works logically and correctly in all possible cases.

**b. Confidence**

- How confident are you that your scheduler works correctly? I am somewhat confident as I'm not sure what other edge cases I may have missed. However, the tests verify that the system works as intended.
- 
- What edge cases would you test next if you had more time?
I would test tasks without a scheduled time, in that it can be done at any time. I would also test cases where there's tasks that overlap and have the same priority as each other.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am satisfied with all of the tests working along with the system being able to function and meet the requirements.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would probably adjust the scheduling logic to allow for more flexibility as the logic is still somewhat rigid.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
I learned that I must be very clear with the logic and that a good system design will help to keep the project under control as AI has clear definitions and constraints to work with.

<img width="739" height="1343" alt="image" src="https://github.com/user-attachments/assets/04480961-5625-4647-b94f-4f6ecfe5821b" />

