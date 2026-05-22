"""Tests for AweClient and all resource sub-clients.

Each test verifies the HTTP verb, URL path, request body (where applicable),
and the return type / key fields of the parsed response.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import pytest
import responses as rsps_lib

from pyawe import AweClient
from pyawe.exceptions import AweAuthError
from pyawe.models import (
    CreateLoopBlockResponse,
    ExecutionProfile,
    Job,
    JobWithWorkflows,
    LoginInfo,
    LoopBlock,
    Note,
    NoteFolder,
    Status,
    Task,
    TaskLink,
    TaskPortSpec,
    TaskPortValues,
    TaskRun,
    TaskScript,
    TaskTeamRole,
    TaskWithContext,
    Workflow,
    WorkflowWithTasks,
)

from .conftest import (
    API_URL,
    AUTH_URL,
    FOLDER_ID,
    INNER_WF_ID,
    JOB_ID,
    LINK_FROM,
    LINK_TO,
    LOOP_ID,
    NOTE_ID,
    PORT_ID,
    PROFILE_ID,
    ROLE_ID,
    RUN_ID,
    SCRIPT_ID,
    TASK_ID,
    TEAM_ID,
    TS,
    WF_ID,
    create_loop_block_response_dict,
    folder_dict,
    job_dict,
    job_with_wfs_dict,
    link_dict,
    login_response_dict,
    loop_block_dict,
    note_dict,
    port_spec_dict,
    profile_dict,
    run_dict,
    script_dict,
    task_dict,
    task_with_context_dict,
    team_role_dict,
    wf_dict,
    wf_with_tasks_dict,
)


def _body(call_index: int = 0) -> dict:
    """Parse the JSON body of the nth recorded request."""
    return json.loads(rsps_lib.calls[call_index].request.body)


def _url(call_index: int = 0) -> str:
    return rsps_lib.calls[call_index].request.url


def _method(call_index: int = 0) -> str:
    return rsps_lib.calls[call_index].request.method


# ── AweClient initialisation ──────────────────────────────────────────────────


def test_client_exposes_all_twelve_sub_clients():
    c = AweClient(API_URL, AUTH_URL)
    assert hasattr(c, "workflows")
    assert hasattr(c, "tasks")
    assert hasattr(c, "task_links")
    assert hasattr(c, "task_ports")
    assert hasattr(c, "task_scripts")
    assert hasattr(c, "task_runs")
    assert hasattr(c, "task_team_roles")
    assert hasattr(c, "jobs")
    assert hasattr(c, "execution_profiles")
    assert hasattr(c, "loop_blocks")
    assert hasattr(c, "notes")
    assert hasattr(c, "note_folders")


def test_auth_url_defaults_to_api_url():
    c = AweClient(API_URL)
    assert c._http._auth_url == API_URL


# ── AweClient.login ───────────────────────────────────────────────────────────


@rsps_lib.activate
def test_login_returns_login_info():
    rsps_lib.add(rsps_lib.POST, f"{AUTH_URL}/auth/login", json=login_response_dict())
    c = AweClient(API_URL, AUTH_URL)
    info = c.login("user@example.com", "secret")
    assert isinstance(info, LoginInfo)
    assert info.token == "test-token"


@rsps_lib.activate
def test_login_stores_token_and_sends_bearer_on_next_request():
    rsps_lib.add(rsps_lib.POST, f"{AUTH_URL}/auth/login", json=login_response_dict("tok99"))
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows", json=[])
    c = AweClient(API_URL, AUTH_URL)
    c.login("user@example.com", "secret")
    c.workflows.list()
    assert rsps_lib.calls[1].request.headers["Authorization"] == "Bearer tok99"


@rsps_lib.activate
def test_login_posts_credentials_to_auth_url():
    rsps_lib.add(rsps_lib.POST, f"{AUTH_URL}/auth/login", json=login_response_dict())
    c = AweClient(API_URL, AUTH_URL)
    c.login("u@example.com", "pw")
    body = _body(0)
    assert body["email"] == "u@example.com"
    assert body["password"] == "pw"


# ── WorkflowsClient ───────────────────────────────────────────────────────────


@rsps_lib.activate
def test_workflows_list_returns_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows", json=[wf_dict()])
    result = client.workflows.list()
    assert isinstance(result, list)
    assert isinstance(result[0], Workflow)
    assert result[0].name == "Test Workflow"


@rsps_lib.activate
def test_workflows_list_without_team_id_sends_no_params(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows", json=[])
    client.workflows.list()
    assert "team_id" not in _url()


@rsps_lib.activate
def test_workflows_list_with_team_id_sends_param(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows", json=[])
    client.workflows.list(team_id=TEAM_ID)
    assert f"team_id={TEAM_ID}" in _url()


@rsps_lib.activate
def test_workflows_list_accepts_uuid_team_id(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows", json=[])
    client.workflows.list(team_id=uuid.UUID(TEAM_ID))
    assert f"team_id={TEAM_ID}" in _url()


@rsps_lib.activate
def test_workflows_create_posts_and_returns_workflow(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/workflows", json=wf_dict())
    wf = client.workflows.create("Test Workflow")
    assert isinstance(wf, Workflow)
    assert _method() == "POST"
    assert _body()["name"] == "Test Workflow"


@rsps_lib.activate
def test_workflows_create_with_status_enum_sends_wire_value(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/workflows", json=wf_dict(status="In Progress"))
    client.workflows.create("WF", status=Status.IN_PROGRESS)
    assert _body()["status"] == "In Progress"


@rsps_lib.activate
def test_workflows_create_omits_none_fields(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/workflows", json=wf_dict())
    client.workflows.create("WF")
    body = _body()
    assert "description" not in body
    assert "job_id" not in body
    assert "team_id" not in body


@rsps_lib.activate
def test_workflows_get_returns_workflow_with_tasks(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows/{WF_ID}", json=wf_with_tasks_dict())
    result = client.workflows.get(WF_ID)
    assert isinstance(result, WorkflowWithTasks)
    assert _method() == "GET"


@rsps_lib.activate
def test_workflows_update_puts_with_id(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/workflows/{WF_ID}", json=wf_dict(name="Renamed"))
    wf = client.workflows.update(WF_ID, name="Renamed")
    assert isinstance(wf, Workflow)
    assert _method() == "PUT"
    assert _body()["name"] == "Renamed"


@rsps_lib.activate
def test_workflows_delete_sends_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/workflows/{WF_ID}", status=204)
    client.workflows.delete(WF_ID)
    assert _method() == "DELETE"
    assert WF_ID in _url()


@rsps_lib.activate
def test_workflows_set_team(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/workflows/{WF_ID}/team", json=wf_dict())
    wf = client.workflows.set_team(WF_ID, TEAM_ID)
    assert isinstance(wf, Workflow)
    assert _body()["team_id"] == TEAM_ID


@rsps_lib.activate
def test_workflows_clear_team(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/workflows/{WF_ID}/team", json=wf_dict())
    wf = client.workflows.clear_team(WF_ID)
    assert isinstance(wf, Workflow)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_workflows_merge(client: AweClient):
    other_id = "ffffffff-ffff-ffff-ffff-ffffffffffff"
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/workflows/{WF_ID}/merge/{other_id}", json=wf_dict())
    wf = client.workflows.merge(WF_ID, other_id)
    assert isinstance(wf, Workflow)
    assert _method() == "POST"


@rsps_lib.activate
def test_workflows_duplicate(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/workflows/{WF_ID}/duplicate", json=wf_with_tasks_dict())
    result = client.workflows.duplicate(WF_ID)
    assert isinstance(result, WorkflowWithTasks)


# ── TasksClient ───────────────────────────────────────────────────────────────


@rsps_lib.activate
def test_tasks_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks", json=[task_dict()])
    result = client.tasks.list()
    assert isinstance(result[0], Task)


@rsps_lib.activate
def test_tasks_list_with_workflow_id(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks", json=[])
    client.tasks.list(workflow_id=WF_ID)
    assert f"workflow_id={WF_ID}" in _url()


@rsps_lib.activate
def test_tasks_list_mine_no_params(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/mine", json=[task_with_context_dict()])
    result = client.tasks.list_mine()
    assert isinstance(result[0], TaskWithContext)
    assert "role_ids" not in _url()


@rsps_lib.activate
def test_tasks_list_mine_with_role_ids(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/mine", json=[])
    client.tasks.list_mine(role_ids=[ROLE_ID])
    assert f"role_ids={ROLE_ID}" in _url()


@rsps_lib.activate
def test_tasks_list_mine_empty_role_ids_sends_no_param(client: AweClient):
    """Empty list is falsy — no role_ids param should be sent."""
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/mine", json=[])
    client.tasks.list_mine(role_ids=[])
    assert "role_ids" not in _url()


@rsps_lib.activate
def test_tasks_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks", json=task_dict())
    t = client.tasks.create("Test Task", WF_ID)
    assert isinstance(t, Task)
    body = _body()
    assert body["name"] == "Test Task"
    assert body["workflow_id"] == WF_ID


@rsps_lib.activate
def test_tasks_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    t = client.tasks.get(TASK_ID)
    assert isinstance(t, Task)
    assert _method() == "GET"


@rsps_lib.activate
def test_tasks_update_with_name(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict(name="Renamed"))
    t = client.tasks.update(TASK_ID, name="Renamed")
    assert isinstance(t, Task)
    assert _body()["name"] == "Renamed"


@rsps_lib.activate
def test_tasks_update_assigned_to_omitted_does_not_send_key(client: AweClient):
    """Default _UNSET: assigned_to must not appear in the body."""
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, name="x")
    assert "assigned_to" not in _body()


@rsps_lib.activate
def test_tasks_update_assigned_to_none_sends_null(client: AweClient):
    """assigned_to=None should send null (clears assignment)."""
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, assigned_to=None)
    body = _body()
    assert "assigned_to" in body
    assert body["assigned_to"] is None


@rsps_lib.activate
def test_tasks_update_assigned_to_user_id_sends_value(client: AweClient):
    """assigned_to=<id> should set the assignment."""
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, assigned_to="user-uuid-123")
    assert _body()["assigned_to"] == "user-uuid-123"


@rsps_lib.activate
def test_tasks_update_status_enum_sends_wire_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, status=Status.IN_PROGRESS)
    assert _body()["status"] == "In Progress"


@rsps_lib.activate
def test_tasks_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/tasks/{TASK_ID}", status=204)
    client.tasks.delete(TASK_ID)
    assert _method() == "DELETE"
    assert TASK_ID in _url()


@rsps_lib.activate
def test_tasks_decide(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/decide", json=task_dict())
    t = client.tasks.decide(TASK_ID, "approved")
    assert isinstance(t, Task)
    assert _body()["branch_label"] == "approved"


@rsps_lib.activate
def test_tasks_clear_rework(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/tasks/{TASK_ID}/rework", json=task_dict())
    t = client.tasks.clear_rework(TASK_ID)
    assert isinstance(t, Task)
    assert _method() == "DELETE"


# ── TaskLinksClient ───────────────────────────────────────────────────────────


@rsps_lib.activate
def test_task_links_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/task-links", json=link_dict())
    lk = client.task_links.create(LINK_FROM, LINK_TO)
    assert isinstance(lk, TaskLink)
    body = _body()
    assert body["from_task_id"] == LINK_FROM
    assert body["to_task_id"] == LINK_TO


@rsps_lib.activate
def test_task_links_create_with_branch_label(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/task-links", json=link_dict(branch_label="yes"))
    client.task_links.create(LINK_FROM, LINK_TO, branch_label="yes")
    assert _body()["branch_label"] == "yes"


@rsps_lib.activate
def test_task_links_create_without_branch_label_omits_key(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/task-links", json=link_dict())
    client.task_links.create(LINK_FROM, LINK_TO)
    assert "branch_label" not in _body()


@rsps_lib.activate
def test_task_links_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/task-links/{LINK_FROM}/{LINK_TO}", status=204)
    client.task_links.delete(LINK_FROM, LINK_TO)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_task_links_get_next(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/next", json=[task_dict()])
    result = client.task_links.get_next(TASK_ID)
    assert isinstance(result[0], Task)


@rsps_lib.activate
def test_task_links_get_previous(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/previous", json=[task_dict()])
    result = client.task_links.get_previous(TASK_ID)
    assert isinstance(result[0], Task)


@rsps_lib.activate
def test_task_links_get_outgoing(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/links", json=[link_dict()])
    result = client.task_links.get_outgoing(TASK_ID)
    assert isinstance(result[0], TaskLink)


@rsps_lib.activate
def test_task_links_update_bindings(client: AweClient):
    from pyawe.models import DataBinding
    bindings = [DataBinding(from_port="out", to_port="in")]
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/task-links/{LINK_FROM}/{LINK_TO}/bindings",
        json=link_dict(),
    )
    lk = client.task_links.update_bindings(LINK_FROM, LINK_TO, bindings)
    assert isinstance(lk, TaskLink)
    body = _body()
    assert body["bindings"] == [{"from": "out", "to": "in"}]


# ── TaskPortsClient ───────────────────────────────────────────────────────────


@rsps_lib.activate
def test_task_ports_list_specs(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/ports", json=[port_spec_dict()])
    result = client.task_ports.list_specs(TASK_ID)
    assert isinstance(result[0], TaskPortSpec)


@rsps_lib.activate
def test_task_ports_create_spec(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/ports", json=port_spec_dict())
    ps = client.task_ports.create_spec(TASK_ID, "input", "data_in", "string")
    assert isinstance(ps, TaskPortSpec)
    body = _body()
    assert body["direction"] == "input"
    assert body["name"] == "data_in"
    assert body["value_type"] == "string"


@rsps_lib.activate
def test_task_ports_update_spec(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}/ports/{PORT_ID}", json=port_spec_dict())
    ps = client.task_ports.update_spec(TASK_ID, PORT_ID, name="new_name")
    assert isinstance(ps, TaskPortSpec)
    assert _body()["name"] == "new_name"


@rsps_lib.activate
def test_task_ports_delete_spec(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/tasks/{TASK_ID}/ports/{PORT_ID}", status=204)
    client.task_ports.delete_spec(TASK_ID, PORT_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_task_ports_get_inputs(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/tasks/{TASK_ID}/inputs",
        json={"specs": [port_spec_dict()], "values": None},
    )
    result = client.task_ports.get_inputs(TASK_ID)
    assert isinstance(result, TaskPortValues)


@rsps_lib.activate
def test_task_ports_patch_inputs(client: AweClient):
    rsps_lib.add(
        rsps_lib.PATCH,
        f"{API_URL}/tasks/{TASK_ID}/inputs",
        json={"specs": [], "values": {"x": 1}},
    )
    result = client.task_ports.patch_inputs(TASK_ID, {"x": 1})
    assert isinstance(result, TaskPortValues)
    assert _body() == {"values": {"x": 1}}


@rsps_lib.activate
def test_task_ports_get_outputs(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/tasks/{TASK_ID}/outputs",
        json={"specs": [], "values": None},
    )
    result = client.task_ports.get_outputs(TASK_ID)
    assert isinstance(result, TaskPortValues)


# ── TaskScriptsClient ─────────────────────────────────────────────────────────


@rsps_lib.activate
def test_task_scripts_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/script", json=script_dict())
    ts = client.task_scripts.get(TASK_ID)
    assert isinstance(ts, TaskScript)


@rsps_lib.activate
def test_task_scripts_upsert(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}/script", json=script_dict())
    ts = client.task_scripts.upsert(TASK_ID, endpoint="https://hook.example.com/cb")
    assert isinstance(ts, TaskScript)
    assert _body()["endpoint"] == "https://hook.example.com/cb"


@rsps_lib.activate
def test_task_scripts_upsert_omits_none_fields(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}/script", json=script_dict())
    client.task_scripts.upsert(TASK_ID, script_type="webhook")
    body = _body()
    assert "script_body" not in body
    assert "endpoint" not in body


@rsps_lib.activate
def test_task_scripts_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/tasks/{TASK_ID}/script", status=204)
    client.task_scripts.delete(TASK_ID)
    assert _method() == "DELETE"


# ── TaskRunsClient ────────────────────────────────────────────────────────────


@rsps_lib.activate
def test_task_runs_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/runs", json=[run_dict()])
    result = client.task_runs.list(TASK_ID)
    assert isinstance(result[0], TaskRun)


@rsps_lib.activate
def test_task_runs_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/runs", json=run_dict())
    now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    r = client.task_runs.create(TASK_ID, "Success", now, now)
    assert isinstance(r, TaskRun)
    body = _body()
    assert body["outcome"] == "Success"
    assert "started_at" in body
    assert "completed_at" in body


@rsps_lib.activate
def test_task_runs_create_with_optional_fields(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/runs", json=run_dict())
    now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    client.task_runs.create(
        TASK_ID, "Failure", now, now,
        run_id=RUN_ID,
        runner_id="runner-1",
        error_message="boom",
    )
    body = _body()
    assert body["run_id"] == RUN_ID
    assert body["runner_id"] == "runner-1"
    assert body["error_message"] == "boom"


@rsps_lib.activate
def test_task_runs_create_omits_optional_fields_when_absent(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/runs", json=run_dict())
    now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    client.task_runs.create(TASK_ID, "Success", now, now)
    body = _body()
    assert "run_id" not in body
    assert "runner_id" not in body
    assert "error_message" not in body


@rsps_lib.activate
def test_task_runs_create_with_input_and_output_json(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/runs", json=run_dict())
    now = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    client.task_runs.create(
        TASK_ID, "Success", now, now,
        input_json={"a": 1},
        output_json={"b": 2},
    )
    body = _body()
    assert body["input_json"] == {"a": 1}
    assert body["output_json"] == {"b": 2}


@rsps_lib.activate
def test_task_runs_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/runs/{RUN_ID}", json=run_dict())
    r = client.task_runs.get(TASK_ID, RUN_ID)
    assert isinstance(r, TaskRun)


# ── TaskTeamRolesClient ───────────────────────────────────────────────────────


@rsps_lib.activate
def test_task_team_roles_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/team-roles", json=[team_role_dict()])
    result = client.task_team_roles.list(TASK_ID)
    assert isinstance(result[0], TaskTeamRole)


@rsps_lib.activate
def test_task_team_roles_assign(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/team-roles", json=team_role_dict())
    r = client.task_team_roles.assign(TASK_ID, ROLE_ID)
    assert isinstance(r, TaskTeamRole)
    assert _body()["team_role_id"] == ROLE_ID


@rsps_lib.activate
def test_task_team_roles_remove(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/tasks/{TASK_ID}/team-roles/{ROLE_ID}", status=204)
    client.task_team_roles.remove(TASK_ID, ROLE_ID)
    assert _method() == "DELETE"
    assert ROLE_ID in _url()


# ── JobsClient ────────────────────────────────────────────────────────────────


@rsps_lib.activate
def test_jobs_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/jobs", json=[job_dict()])
    result = client.jobs.list()
    assert isinstance(result[0], Job)


@rsps_lib.activate
def test_jobs_list_with_team_id(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/jobs", json=[])
    client.jobs.list(team_id=TEAM_ID)
    assert f"team_id={TEAM_ID}" in _url()


@rsps_lib.activate
def test_jobs_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/jobs", json=job_dict())
    j = client.jobs.create("Test Job")
    assert isinstance(j, Job)
    assert _body()["name"] == "Test Job"


@rsps_lib.activate
def test_jobs_create_with_status_enum(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/jobs", json=job_dict(status="In Progress"))
    client.jobs.create("J", status=Status.IN_PROGRESS)
    assert _body()["status"] == "In Progress"


@rsps_lib.activate
def test_jobs_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/jobs/{JOB_ID}", json=job_with_wfs_dict())
    result = client.jobs.get(JOB_ID)
    assert isinstance(result, JobWithWorkflows)


@rsps_lib.activate
def test_jobs_update(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/jobs/{JOB_ID}", json=job_dict(name="Renamed"))
    j = client.jobs.update(JOB_ID, name="Renamed")
    assert isinstance(j, Job)
    assert _body()["name"] == "Renamed"


@rsps_lib.activate
def test_jobs_update_omits_none_fields(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/jobs/{JOB_ID}", json=job_dict())
    client.jobs.update(JOB_ID, name="X")
    body = _body()
    assert "status" not in body
    assert "archived" not in body


@rsps_lib.activate
def test_jobs_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/jobs/{JOB_ID}", status=204)
    client.jobs.delete(JOB_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_jobs_clone_workflow(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/jobs/{JOB_ID}/workflows/from-template/{WF_ID}",
        json=wf_with_tasks_dict(),
    )
    result = client.jobs.clone_workflow(JOB_ID, WF_ID)
    assert isinstance(result, WorkflowWithTasks)


@rsps_lib.activate
def test_jobs_set_team(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/jobs/{JOB_ID}/team", json=job_dict())
    j = client.jobs.set_team(JOB_ID, TEAM_ID)
    assert isinstance(j, Job)
    assert _body()["team_id"] == TEAM_ID


@rsps_lib.activate
def test_jobs_clear_team(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/jobs/{JOB_ID}/team", json=job_dict())
    j = client.jobs.clear_team(JOB_ID)
    assert isinstance(j, Job)
    assert _method() == "DELETE"


# ── ExecutionProfilesClient ───────────────────────────────────────────────────


@rsps_lib.activate
def test_execution_profiles_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/execution-profiles", json=[profile_dict()])
    result = client.execution_profiles.list()
    assert isinstance(result[0], ExecutionProfile)


@rsps_lib.activate
def test_execution_profiles_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/execution-profiles", json=profile_dict())
    ep = client.execution_profiles.create("Python 3.12", "python:3.12-slim")
    assert isinstance(ep, ExecutionProfile)
    body = _body()
    assert body["name"] == "Python 3.12"
    assert body["image"] == "python:3.12-slim"


@rsps_lib.activate
def test_execution_profiles_create_omits_none_optionals(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/execution-profiles", json=profile_dict())
    client.execution_profiles.create("P", "img")
    body = _body()
    assert "description" not in body
    assert "cpu_request" not in body


@rsps_lib.activate
def test_execution_profiles_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/execution-profiles/{PROFILE_ID}", json=profile_dict())
    ep = client.execution_profiles.get(PROFILE_ID)
    assert isinstance(ep, ExecutionProfile)


@rsps_lib.activate
def test_execution_profiles_update(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/execution-profiles/{PROFILE_ID}", json=profile_dict())
    ep = client.execution_profiles.update(PROFILE_ID, cpu_limit="2")
    assert isinstance(ep, ExecutionProfile)
    assert _body()["cpu_limit"] == "2"


@rsps_lib.activate
def test_execution_profiles_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/execution-profiles/{PROFILE_ID}", status=204)
    client.execution_profiles.delete(PROFILE_ID)
    assert _method() == "DELETE"


# ── LoopBlocksClient ──────────────────────────────────────────────────────────


@rsps_lib.activate
def test_loop_blocks_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/loop-blocks", json=create_loop_block_response_dict())
    result = client.loop_blocks.create("Loop 1", WF_ID, "count", {"count": 5})
    assert isinstance(result, CreateLoopBlockResponse)
    body = _body()
    assert body["name"] == "Loop 1"
    assert body["workflow_id"] == WF_ID
    assert body["loop_type"] == "count"
    assert body["loop_config"] == {"count": 5}


@rsps_lib.activate
def test_loop_blocks_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/loop-blocks/{LOOP_ID}", json=loop_block_dict())
    lb = client.loop_blocks.get(LOOP_ID)
    assert isinstance(lb, LoopBlock)


@rsps_lib.activate
def test_loop_blocks_update(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/loop-blocks/{LOOP_ID}", json=loop_block_dict())
    lb = client.loop_blocks.update(LOOP_ID, name="New Name")
    assert isinstance(lb, LoopBlock)
    assert _body()["name"] == "New Name"


@rsps_lib.activate
def test_loop_blocks_update_omits_none_fields(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/loop-blocks/{LOOP_ID}", json=loop_block_dict())
    client.loop_blocks.update(LOOP_ID, name="X")
    body = _body()
    assert "loop_type" not in body
    assert "loop_config" not in body


@rsps_lib.activate
def test_loop_blocks_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/loop-blocks/{LOOP_ID}", status=204)
    client.loop_blocks.delete(LOOP_ID)
    assert _method() == "DELETE"


# ── NotesClient ───────────────────────────────────────────────────────────────


@rsps_lib.activate
def test_notes_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/notes", json=[note_dict()])
    result = client.notes.list()
    assert isinstance(result[0], Note)


@rsps_lib.activate
def test_notes_list_with_entity_filter(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/notes", json=[])
    client.notes.list(entity_type="task", entity_id=TASK_ID)
    assert "entity_type=task" in _url()
    assert f"entity_id={TASK_ID}" in _url()


@rsps_lib.activate
def test_notes_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/notes", json=note_dict())
    n = client.notes.create("task", TASK_ID, "My Note")
    assert isinstance(n, Note)
    body = _body()
    assert body["entity_type"] == "task"
    assert body["entity_id"] == TASK_ID
    assert body["title"] == "My Note"
    assert body["is_shared"] is False


@rsps_lib.activate
def test_notes_create_with_body(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/notes", json=note_dict())
    client.notes.create("task", TASK_ID, "Title", body="body text")
    assert _body()["body"] == "body text"


@rsps_lib.activate
def test_notes_create_without_body_omits_key(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/notes", json=note_dict())
    client.notes.create("task", TASK_ID, "Title")
    assert "body" not in _body()


@rsps_lib.activate
def test_notes_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/notes/{NOTE_ID}", json=note_dict())
    n = client.notes.get(NOTE_ID)
    assert isinstance(n, Note)


@rsps_lib.activate
def test_notes_update(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/notes/{NOTE_ID}", json=note_dict())
    n = client.notes.update(NOTE_ID, title="New Title")
    assert isinstance(n, Note)
    assert _body()["title"] == "New Title"


@rsps_lib.activate
def test_notes_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/notes/{NOTE_ID}", status=204)
    client.notes.delete(NOTE_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_notes_list_replies(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/notes/{NOTE_ID}/replies", json=[note_dict()])
    result = client.notes.list_replies(NOTE_ID)
    assert isinstance(result[0], Note)


@rsps_lib.activate
def test_notes_create_reply(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/notes/{NOTE_ID}/replies", json=note_dict())
    n = client.notes.create_reply(NOTE_ID, "reply text")
    assert isinstance(n, Note)
    assert _body()["body"] == "reply text"


@rsps_lib.activate
def test_notes_move_to_folder(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/notes/{NOTE_ID}/folder", json=note_dict())
    n = client.notes.move(NOTE_ID, FOLDER_ID)
    assert isinstance(n, Note)
    assert _body()["folder_id"] == FOLDER_ID


@rsps_lib.activate
def test_notes_move_to_none_sends_null(client: AweClient):
    """Passing folder_id=None should unfile the note (send null, not omit)."""
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/notes/{NOTE_ID}/folder", json=note_dict())
    client.notes.move(NOTE_ID, None)
    body = _body()
    assert "folder_id" in body
    assert body["folder_id"] is None


# ── NoteFoldersClient ─────────────────────────────────────────────────────────


@rsps_lib.activate
def test_note_folders_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/note-folders", json=[folder_dict()])
    result = client.note_folders.list()
    assert isinstance(result[0], NoteFolder)


@rsps_lib.activate
def test_note_folders_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/note-folders", json=folder_dict())
    f = client.note_folders.create("My Folder")
    assert isinstance(f, NoteFolder)
    assert _body()["name"] == "My Folder"


@rsps_lib.activate
def test_note_folders_update(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/note-folders/{FOLDER_ID}", json=folder_dict())
    f = client.note_folders.update(FOLDER_ID, "Renamed")
    assert isinstance(f, NoteFolder)
    assert _body()["name"] == "Renamed"


@rsps_lib.activate
def test_note_folders_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/note-folders/{FOLDER_ID}", status=204)
    client.note_folders.delete(FOLDER_ID)
    assert _method() == "DELETE"
    assert FOLDER_ID in _url()


# ── UUID coercion in URL paths ────────────────────────────────────────────────


@rsps_lib.activate
def test_workflow_get_accepts_uuid_object(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows/{WF_ID}", json=wf_with_tasks_dict())
    client.workflows.get(uuid.UUID(WF_ID))
    assert WF_ID in _url()


@rsps_lib.activate
def test_task_get_accepts_uuid_object(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.get(uuid.UUID(TASK_ID))
    assert TASK_ID in _url()
