# Assignment

Verbatim from elearn:

> You must choose an LLM and a task, and evaluate your chosen LLM on the task. You can choose any LLM and any task. We will cover evaluation in Topic 5, thus you will have 1 week to complete the assignment.
>
> You may choose a task and evaluation method that we discuss in class during Topic 5, or you may choose your own task.
>
> There are 2 deliverables for this assignment. (1) in-class presentation (2 minutes only) and (2) the report itself (average length 2-5 pages, include link to code).
>
> The 2-min presentation should describe what you chose as LLM and task, the results/findings, and any lessons learnt of note.

## My email to Professor Wynter to Clarify Assignment and Her Reply

> Hi Kimsia
> The topic is a good one. What I would like to add to it is a quantitative way to assess the results for each of the tasks x LLM. If the output of the code is correct? Any other metrics for evaluation? If it is a UI for example, is "correct" easy to define? Point being to think about the EVALUATION of it as well as setting up the tasks themselves


From: SIM Kim Sia <xx.xx>
Sent: Thursday, May 15, 2025 12:51 PM
To: WYNTER Laura <xx.xx>
Subject: Evaluation assignment

> On a different topic, I am checking directionally, if the following evaluation for the individual assignment is acceptable.
>
> 1. Develop 7 (+-2) code related tasks (where some involve extensive UI/UX changes) for implementing new features within an existing codebase
> 2. Evaluate two LLM models within an AI Assisted code IDE like Cursor
> 3. See how many of these tasks are solved within 1 pass, and how many passes before reaching max 10 pass.
>
> The reason I want to do it this way is because I understand that most LLM benchmarks often assume iid (independent and identically distributed), but in my experience using LLM esp at work for web development, contextual understanding is key. So I want to work towards something like this.
>
> Also given the growth of LLM powered apps like IDE, I want to test the LLM within real world uses such as AI Assisted IDE.
>
> I am deeply interested in this area since I use AI Assisted IDE a lot for my own web development work, and is tangentially related to my potential capstone project as part of my masters degree.
>
> Thank you.

## Idea in Broadstroke

1. Generate a couple of django projects using a generator

2. Using these generator and hand evaluate based on a few tasks that involve both code and UI/UX design.

3. Test against cursor while setting to specific prompts.

4. Evaluate against Claude 3.7 vs Gemini Pro 2.5

### The Plan Fleshed Out

1. Generate a few Django toy projects (7 +- 2) first
2. Then use Cursor IDE to test both LLMs (Claude 3.7 and Gemini Pro 2.5) on specific tasks within these projects
3. Evaluate their performance directly in the IDE environment, which is more realistic to real-world usage

This is actually a better approach because:

1. It's more realistic - I'm testing in the actual environment where developers use these LLMs
2. It allows for better contextual understanding - the LLMs can see the existing codebase
3. It's more practical - I can directly see how the LLMs handle real coding tasks.

The one project codebase is `law_firm_docs_10lzj5`

## Project Structure Explained

