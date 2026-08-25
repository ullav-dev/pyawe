# Getting Started

This guide walks through the most common workflows: connecting to the API, creating a job with a workflow, managing tasks, and handling errors.

## Prerequisites

Install pyawe:

```bash
pip install pyawe
```

You need a running AWE server and credentials for the `ullav-user-management` auth service.

## Connecting and authenticating

```python
from pyawe import AweClient

client = AweClient(
    api_url="http://localhost:8080",
    auth_url="http://localhost:8081",
)
info = client.login(email="you@example.com", password="secret")
print(info.username, info.roles)
```

If your AWE server and auth service share a hostname (e.g. behind a reverse proxy), you can omit `auth_url`:

```python
client = AweClient("https://awe.example.com")
client.login(email="you@example.com", password="secret")
```

## Creating a job and workflow

Jobs group related workflow instances together. Create a job first, then create a workflow inside it:

```python
job = client.jobs.create("Q3 Onboarding Campaign")
wf  = client.workflows.create("Employee Onboarding", job_id=job.id)
print(wf.id, wf.status)  # UUID, Status.NOT_STARTED
```

## Building a workflow with tasks

Every workflow needs a start task and an end task. Add tasks, then link them:

```python
start   = client.tasks.create("Kick-off",       workflow_id=wf.id, is_start=True)
send_hw = client.tasks.create("Send Hardware",   workflow_id=wf.id)
it_acct = client.tasks.create("Create Accounts", workflow_id=wf.id)
finish  = client.tasks.create("Day-1 Complete",  workflow_id=wf.id, is_end=True)

client.task_links.create(start.id,   send_hw.id)
client.task_links.create(start.id,   it_acct.id)
client.task_links.create(send_hw.id, finish.id)
client.task_links.create(it_acct.id, finish.id)
```

## Updating task status

Move a task through its lifecycle using [`tasks.update()`][pyawe.client.TasksClient.update]:

```python
from pyawe import Status

client.tasks.update(start.id, status=Status.IN_PROGRESS)
# ... work is done ...
client.tasks.update(start.id, status=Status.COMPLETE)
```

You can pass enum members or plain strings — both work:

```python
client.tasks.update(start.id, status="In Progress")
```

## Assigning tasks

`assigned_to` is a **tri-state** field:

```python
# Set assignment
client.tasks.update(task.id, assigned_to="user-uuid-here")

# Clear assignment (pass None explicitly)
client.tasks.update(task.id, assigned_to=None)

# Leave assignment unchanged (omit the argument entirely)
client.tasks.update(task.id, name="New name")
```

## Listing your tasks

[`tasks.list_mine()`][pyawe.client.TasksClient.list_mine] returns tasks directly assigned to you, with workflow and job context:

```python
my_tasks = client.tasks.list_mine()

for t in my_tasks:
    context = t.workflow_name
    if t.job_name:
        context = f"{t.job_name} / {t.workflow_name}"
    print(f"[{t.task.status}]  {t.task.name}  ({context})")
```

To include tasks assigned via team roles, pass `role_ids`:

```python
my_tasks = client.tasks.list_mine(role_ids=["role-uuid-1", "role-uuid-2"])
```

## Decision tasks

A decision task routes execution down one of several branches. Create links with `branch_label`, then call [`tasks.decide()`][pyawe.client.TasksClient.decide]:

```python
from pyawe import TaskType

gate = client.tasks.create("Approval Gate", workflow_id=wf.id, task_type=TaskType.DECISION)
approved = client.tasks.create("Proceed",  workflow_id=wf.id)
rejected = client.tasks.create("Escalate", workflow_id=wf.id)

client.task_links.create(gate.id, approved.id, branch_label="Approved")
client.task_links.create(gate.id, rejected.id, branch_label="Rejected")

# Later, when the decision is made:
client.tasks.decide(gate.id, branch_label="Approved")
# Tasks on the rejected branch are automatically cancelled.
```

## Automated tasks and execution profiles

For automated tasks, attach a script and optionally an execution profile:

```python
from pyawe import TaskType

auto_task = client.tasks.create(
    "Send Welcome Email",
    workflow_id=wf.id,
    task_type=TaskType.AUTOMATED,
)

client.task_scripts.upsert(
    auto_task.id,
    script_type="webhook",
    endpoint="https://hooks.example.com/send-email",
    timeout_secs=30,
    retry_limit=3,
)
```

## Duplicating workflow templates

Mark a workflow as a template and clone it into new jobs:

```python
template = client.workflows.create("Standard Onboarding", is_template=True)
# ... populate template with tasks ...

new_job = client.jobs.create("October Intake")
instance = client.jobs.clone_workflow(new_job.id, template.id)
```

## Error handling reference

| Exception | Raised when |
|---|---|
| [`AweAuthError`][pyawe.AweAuthError] | `login()` not called; 401 or 403 response |
| [`AweNotFoundError`][pyawe.AweNotFoundError] | 404 — resource does not exist |
| [`AweValidationError`][pyawe.AweValidationError] | 400 — invalid input |
| [`AweServerError`][pyawe.AweServerError] | 5xx — server-side fault |
| [`AweError`][pyawe.AweError] | Base class; catches all of the above |
