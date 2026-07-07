# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
- Briefly describe your initial UML design.
The UML diagram represents the actions an owner can take in a pet care management app. Three core actions a user should be able to perform are:  
  - Add a pet.
  - Schedule a task
  - See today's tasks.
- What classes did you include, and what responsibilities did you assign to each?
  - Pet
    - attributes
      - name
      - species
    - methods
      - eat
      - sleep
  - Task
    - attributes
      - title
      - duration_minutes
      - priority
    - methods
      - schedule a task
      - cancel a task
  - Schedule
    -  attributes
       -  tasks list
    -  methods
       -  list today's tasks
       -  add a task to the schedule
       -  build plan for schedule
   - Owner
     - attributes
       - name
       - experience
       - pets
     - methods
       - add pet to registry



**b. Design changes**

- Did your design change during implementation? If yes, describe at least one change and why you made it.
- Initially, I created a `Walk` class. But that was too specific. So I replaced `Walk` with a general `Task` class, which contains an attribute where you can specify the activity type is a walk.  
- Also, there were several relationships missing from the draft. The `Pet` had a `Schedule` and the `Owner` had `Pet`s, but the link between `Owner` and `Schedule` was missing. Afterall, the owner is the one acting on the schedule, so the connection is an important missing link.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  - Time
  - Priority
  - Frequency
- How did you decide which constraints mattered most?
  - I did not think frequency was important, so I removed it from the Pawpal System. There are already too many variables to keep track of. I think it's better to focus on only two features of the scheduler (time and priority) because that mimics what a human planning their daily schedule would value first. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
  - The choice is to only allow the owner to perform one task at a time linearly. I think the tradeoff to leave out the ability to multi-task or have multiple tasks in the same allotment of time is a simpler first pass implementation. As well, as a subtle user experience suggestion: "Yeah, you could multi-task but it's probably unhealthy. So I will leave out that option to discourage multi-tasking behavior."
  - The schedule sorts by time ascending, ties broken by priority (with High first), then untimed tasks. That means the user has both pets tasks mixed together -- instead of batched together by pet. That may cause more context switching between pets. But it seems reasonable given the demands of modern society. There will be vet visits and appointments that inevitably overlap.  
- It only detects conflicts when two tasks share the exact same "HH:MM" slot — it ignores overlapping durations.
The method groups timed tasks by their exact start-time string and flags a slot only when 2+ tasks land on it. So a 60-minute task at "09:00" and another task at "09:30" genuinely overlap in real time, but because their start slots differ, find_conflicts reports nothing.
-The tradeoff is:
  - Gained: simplicity and safety. No time-math, no parsing (it leans on the zero-padded "HH:MM" lexicographic trick used in sort_by_time), and no risk of crashing on malformed data. duration_minutes never enters the comparison.
  - Given up: correctness for real overlap. Interval collisions that don't start at the identical minute slip through undetected.
  - A couple of related tradeoffs are marked in the same neighborhood if useful: untimed tasks (time is None) are silently excluded from conflict detection entirely, and build_plan uses a greedy priority fill that can leave the time budget underused rather than solving for optimal packing.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  - Attach my classes sketch and ask for feedback.
  - Write type of tests needed and ask for help drafting tests. 
- What kinds of prompts or questions were most helpful?
  - Explicitly saying: "provide tests for this function."
  - "Update display logic for this function."


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  - Initially suggested sort by pet. I think that is less helpful for an owner trying to juggle taking care of 2 or more pets at the same time. 
  - I rejected suggestion to add monthly frequency. I think there is too much detail added all at once. I would rather create a simpler app and build up functionalities from there rather than do so many complex actions all at once.
- How did you evaluate or verify what the AI suggested?
  - I look at Plan Mode. Then manually accept edits step by step. I would check the app logic, run the tests, and manually click actions on the web app to evaluate the suggestions.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  - Sort tasks by chronological order
    - Tasks without a time, go last
    - If times are equal, then sort by insertion order of task.
  - Sort tasks by priority (from highest to lowest)
  - When you  hit done, a new recurring daily task spawns.
  - Time conflict raises warning.
  - Plan fits under overall time budget.  
  
- Why were these tests important?
  - I think the most important feature is prioritization by level of urgency/importance and time. That is the main use case of the app. The other edge cases are nice to haves for an user.  

**b. Confidence**

- How confident are you that your scheduler works correctly?
  - 3-4 ish. I think there might still be some case the system breaks.
  - The cases where mutiple tasks share the same titles may be confusing. For example: you can make both a task that says "walk dog" daily and another one that is just a single occurence. The daily one will spawn another one after it's marked complete. But the single time task won't. I think that may be confusing for a user. 
- What edge cases would you test next if you had more time?
  - If the user marks a tasks as done, would that still cause time conflicts with tasks in the future?
  - If tasks overlapped by ending with 1 minute left and another starting at the same 1 minute time overalap, what would happen to the system?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  - I'm most satisfied with following through with the process. I enjoyed starting with a class and method sketch, then iterating upon that.  

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  - Although it's part of the spec to create recurring tasks spawned, I think I would remove that functionality because it overcomplicates the app on a first pass. 
  - I would add logic to handle the cases where time duration of events overlap with the start of the next event. I think that is a very realistic use case.
  - I would take the time to learn how to edit my `CLAUDE.MD` file to generalize this context. And force any `python` code to run with `python3`.  


**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?  
  - AI loves complexity! I think it's important to tell it to stay simple as possible. So much is suggested to change at one time, I don't think it's very functional to test. I think I need to work on writing prompts that are even more restrictive about staying focused on one scope and testing that first.  
