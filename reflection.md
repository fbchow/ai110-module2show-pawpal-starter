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

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
