"""Shared fixtures and sample data factories for pyawe tests."""

from __future__ import annotations

import pytest

from pyawe import AweClient

# ── fixed UUIDs ──────────────────────────────────────────────────────────────

WF_ID = "11111111-1111-1111-1111-111111111111"
TASK_ID = "22222222-2222-2222-2222-222222222222"
JOB_ID = "33333333-3333-3333-3333-333333333333"
CONN_ID = "44444444-4444-4444-4444-444444444444"
WORK_ITEM_ID = "55555555-5555-5555-5555-555555555555"
PROFILE_ID = "66666666-6666-6666-6666-666666666666"
LINK_FROM = "77777777-7777-7777-7777-777777777777"
LINK_TO = "88888888-8888-8888-8888-888888888888"
PORT_ID = "99999999-9999-9999-9999-999999999999"
SCRIPT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
RUN_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
ROLE_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
TEAM_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"
LOOP_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
INNER_WF_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff"
PROJECT_ID = "12121212-1212-1212-1212-121212121212"
CHECK_ID = "13131313-1313-1313-1313-131313131313"
SCHEDULE_ID = "14141414-1414-1414-1414-141414141414"
SESSION_ID = "15151515-1515-1515-1515-151515151515"
MESSAGE_ID = "16161616-1616-1616-1616-161616161616"
BRANCH_ID = "17171717-1717-1717-1717-171717171717"

TS = "2024-01-15T12:00:00Z"

API_URL = "http://test-api"
AUTH_URL = "http://test-auth"

# ── response dict factories ──────────────────────────────────────────────────


def wf_dict(**kw: object) -> dict:
    d: dict = {
        "id": WF_ID,
        "name": "Test Workflow",
        "is_template": False,
        "created_at": TS,
        "updated_at": TS,
        "status": "Not Started",
        "schedule_status": "N/A",
        "is_shared": False,
    }
    d.update(kw)
    return d


def wf_with_tasks_dict(**kw: object) -> dict:
    d = {**wf_dict(), "tasks": [], "links": []}
    d.update(kw)
    return d


def task_dict(**kw: object) -> dict:
    d: dict = {
        "id": TASK_ID,
        "name": "Test Task",
        "is_template": False,
        "created_at": TS,
        "updated_at": TS,
        "status": "Not Started",
        "schedule_status": "N/A",
        "workflow_id": WF_ID,
        "is_start": False,
        "is_end": False,
        "task_type": "standard",
    }
    d.update(kw)
    return d


def task_with_context_dict(**kw: object) -> dict:
    d = {**task_dict(), "workflow_name": "WF1"}
    d.update(kw)
    return d


def job_dict(**kw: object) -> dict:
    d: dict = {
        "id": JOB_ID,
        "name": "Test Job",
        "status": "Not Started",
        "schedule_status": "N/A",
        "created_at": TS,
        "updated_at": TS,
        "archived": False,
    }
    d.update(kw)
    return d


def job_with_wfs_dict(**kw: object) -> dict:
    d = {**job_dict(), "workflows": []}
    d.update(kw)
    return d


def profile_dict(**kw: object) -> dict:
    d: dict = {
        "id": PROFILE_ID,
        "name": "Python 3.12",
        "image": "python:3.12-slim",
        "cpu_request": "100m",
        "cpu_limit": "1",
        "memory_request": "128Mi",
        "memory_limit": "512Mi",
        "created_by": "user1",
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def port_spec_dict(**kw: object) -> dict:
    d: dict = {
        "id": PORT_ID,
        "task_id": TASK_ID,
        "direction": "input",
        "name": "data_in",
        "value_type": "string",
        "required": True,
        "sort_order": 0,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def script_dict(**kw: object) -> dict:
    d: dict = {
        "id": SCRIPT_ID,
        "task_id": TASK_ID,
        "script_type": "webhook",
        "timeout_secs": 30,
        "retry_limit": 3,
        "created_at": TS,
        "updated_at": TS,
        "endpoint": "https://hook.example.com/cb",
    }
    d.update(kw)
    return d


def run_dict(**kw: object) -> dict:
    d: dict = {
        "id": RUN_ID,
        "task_id": TASK_ID,
        "created_at": TS,
        "outcome": "Success",
        "started_at": TS,
        "completed_at": TS,
    }
    d.update(kw)
    return d


def team_role_dict(**kw: object) -> dict:
    d: dict = {
        "task_id": TASK_ID,
        "team_role_id": ROLE_ID,
        "assigned_at": TS,
    }
    d.update(kw)
    return d


def loop_block_dict(**kw: object) -> dict:
    d: dict = {
        "id": LOOP_ID,
        "task_id": TASK_ID,
        "outer_workflow_id": WF_ID,
        "inner_workflow_id": INNER_WF_ID,
        "loop_type": "count",
        "loop_config": {"count": 5},
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def create_loop_block_response_dict(**kw: object) -> dict:
    return {
        "task": task_dict(task_type="loop_block"),
        "loop_block": loop_block_dict(),
        **kw,
    }


def link_dict(**kw: object) -> dict:
    d: dict = {
        "from_task_id": LINK_FROM,
        "to_task_id": LINK_TO,
    }
    d.update(kw)
    return d


def project_dict(**kw: object) -> dict:
    d: dict = {
        "id": PROJECT_ID,
        "name": "Test Project",
        "status": "Not Started",
        "created_by": "user1",
        "created_at": TS,
        "updated_at": TS,
        "project_code": "P1",
        "archived": False,
    }
    d.update(kw)
    return d


def task_history_entry_dict(**kw: object) -> dict:
    d: dict = {
        "id": MESSAGE_ID,
        "transitioned_at": TS,
        "task_id": TASK_ID,
        "task_name": "Do the thing",
        "workflow_id": WF_ID,
        "workflow_name": "Test Workflow",
        "job_id": JOB_ID,
        "job_name": "Test Job",
        "from_status": "Ready",
        "to_status": "In Progress",
        "actor_type": "user",
    }
    d.update(kw)
    return d


def connection_dict(**kw: object) -> dict:
    d: dict = {
        "id": CONN_ID,
        "name": "Test Connection",
        "connection_type": "bearer_token",
        "team_id": TEAM_ID,
        "config": {},
        "has_secret": False,
        "created_by": "user1",
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def work_item_dict(**kw: object) -> dict:
    d: dict = {
        "id": WORK_ITEM_ID,
        "name": "Test Work Item",
        "task_type": "standard",
        "is_start": False,
        "is_end": False,
        "is_locked": False,
        "is_shared": False,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def checkpoint_check_dict(**kw: object) -> dict:
    d: dict = {
        "id": CHECK_ID,
        "task_id": TASK_ID,
        "name": "Test Check",
        "check_type": "manual",
        "required": True,
        "sort_order": 0,
        "status": "pending",
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def scheduled_script_dict(**kw: object) -> dict:
    d: dict = {
        "id": SCHEDULE_ID,
        "team_id": TEAM_ID,
        "name": "Nightly Sync",
        "is_active": True,
        "cron_expression": "0 0 * * *",
        "script_type": "webhook",
        "timeout_secs": 30,
        "state": {},
        "next_run_at": TS,
        "created_by": "user1",
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def work_item_port_dict(**kw: object) -> dict:
    d: dict = {
        "id": PORT_ID,
        "work_item_id": WORK_ITEM_ID,
        "direction": "input",
        "name": "text",
        "value_type": "string",
        "required": False,
        "sort_order": 0,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def work_item_script_dict(**kw: object) -> dict:
    d: dict = {
        "id": SCRIPT_ID,
        "work_item_id": WORK_ITEM_ID,
        "script_type": "webhook",
        "timeout_secs": 30,
        "retry_limit": 0,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def work_item_check_dict(**kw: object) -> dict:
    d: dict = {
        "id": CHECK_ID,
        "work_item_id": WORK_ITEM_ID,
        "name": "QA",
        "check_type": "manual",
        "required": True,
        "sort_order": 0,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def work_item_check_script_dict(**kw: object) -> dict:
    d: dict = {
        "id": SCRIPT_ID,
        "check_id": CHECK_ID,
        "script_type": "webhook",
        "timeout_secs": 30,
        "retry_limit": 0,
        "locked_on_clone": False,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def work_item_team_role_dict(**kw: object) -> dict:
    d: dict = {
        "work_item_id": WORK_ITEM_ID,
        "team_role_id": ROLE_ID,
        "assigned_at": TS,
    }
    d.update(kw)
    return d


def work_item_branch_dict(**kw: object) -> dict:
    d: dict = {
        "id": BRANCH_ID,
        "work_item_id": WORK_ITEM_ID,
        "label": "Approved",
        "task_name": "Approved path",
        "sort_order": 0,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def checkpoint_check_script_dict(**kw: object) -> dict:
    d: dict = {
        "id": SCRIPT_ID,
        "check_id": CHECK_ID,
        "script_type": "webhook",
        "timeout_secs": 30,
        "retry_limit": 0,
        "locked_on_clone": False,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def checkpoint_check_run_dict(**kw: object) -> dict:
    d: dict = {
        "id": RUN_ID,
        "check_id": CHECK_ID,
        "created_at": TS,
    }
    d.update(kw)
    return d


def chat_session_dict(**kw: object) -> dict:
    d: dict = {
        "id": SESSION_ID,
        "username": "alice",
        "title": "New chat",
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def chat_message_dict(**kw: object) -> dict:
    d: dict = {
        "id": MESSAGE_ID,
        "session_id": SESSION_ID,
        "role": "user",
        "content": "hello",
        "created_at": TS,
    }
    d.update(kw)
    return d


def login_response_dict(token: str = "test-token") -> dict:
    return {
        "token": token,
        "user": {"id": "uid1", "email": "user@example.com", "username": "alice"},
        "roles": ["member"],
        "permissions": ["read"],
    }


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def client() -> AweClient:
    """AweClient with token pre-set — skips login for most tests."""
    c = AweClient(API_URL, AUTH_URL)
    c._http.set_token("test-token")
    return c
