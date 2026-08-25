"""Tests for AweClient and all resource sub-clients.

Each test verifies the HTTP verb, URL path, request body (where applicable),
and the return type / key fields of the parsed response.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import responses as rsps_lib

from pyawe import AweClient
from pyawe.models import (
    ChatMessage,
    ChatSession,
    CheckpointCheck,
    CheckpointCheckRun,
    CheckpointCheckScript,
    Connection,
    ConnectionTestResult,
    CreateLoopBlockResponse,
    ExecutionProfile,
    Job,
    JobWithWorkflows,
    LoginInfo,
    LoopBlock,
    PassthroughCheckpoints,
    Project,
    ProjectWithJobs,
    ResolvedConnection,
    ScheduledScript,
    ScheduledScriptDispatch,
    ScheduledScriptRun,
    Status,
    Task,
    TaskLink,
    TaskPortSpec,
    TaskPortValues,
    TaskRun,
    TaskScript,
    TaskStateHistoryEntry,
    TaskTeamRole,
    TaskWithContext,
    Workflow,
    WorkflowAllocation,
    WorkflowWithTasks,
    WorkItem,
    WorkItemBranch,
    WorkItemCheck,
    WorkItemCheckScript,
    WorkItemPortSpec,
    WorkItemScript,
    WorkItemTeamRole,
)

from .conftest import (
    API_URL,
    AUTH_URL,
    BRANCH_ID,
    CHECK_ID,
    CONN_ID,
    JOB_ID,
    LINK_FROM,
    LINK_TO,
    LOOP_ID,
    PORT_ID,
    PROFILE_ID,
    PROJECT_ID,
    ROLE_ID,
    RUN_ID,
    SCHEDULE_ID,
    SESSION_ID,
    TASK_ID,
    TEAM_ID,
    TS,
    WF_ID,
    WORK_ITEM_ID,
    chat_message_dict,
    chat_session_dict,
    checkpoint_check_dict,
    checkpoint_check_run_dict,
    checkpoint_check_script_dict,
    connection_dict,
    create_loop_block_response_dict,
    job_dict,
    job_with_wfs_dict,
    link_dict,
    login_response_dict,
    loop_block_dict,
    port_spec_dict,
    profile_dict,
    project_dict,
    run_dict,
    scheduled_script_dict,
    script_dict,
    task_dict,
    task_history_entry_dict,
    task_with_context_dict,
    team_role_dict,
    wf_dict,
    wf_with_tasks_dict,
    work_item_branch_dict,
    work_item_check_dict,
    work_item_check_script_dict,
    work_item_dict,
    work_item_port_dict,
    work_item_script_dict,
    work_item_team_role_dict,
)


def _body(call_index: int = 0) -> dict:
    """Parse the JSON body of the nth recorded request."""
    return json.loads(rsps_lib.calls[call_index].request.body)


def _url(call_index: int = 0) -> str:
    return rsps_lib.calls[call_index].request.url


def _method(call_index: int = 0) -> str:
    return rsps_lib.calls[call_index].request.method


# ── AweClient initialisation ──────────────────────────────────────────────────


def test_client_exposes_all_sub_clients():
    c = AweClient(API_URL, AUTH_URL)
    assert hasattr(c, "workflows")
    assert hasattr(c, "tasks")
    assert hasattr(c, "task_links")
    assert hasattr(c, "task_ports")
    assert hasattr(c, "task_scripts")
    assert hasattr(c, "task_secrets")
    assert hasattr(c, "task_runs")
    assert hasattr(c, "task_team_roles")
    assert hasattr(c, "jobs")
    assert hasattr(c, "projects")
    assert hasattr(c, "execution_profiles")
    assert hasattr(c, "loop_blocks")
    assert hasattr(c, "task_history")
    assert hasattr(c, "connections")
    assert hasattr(c, "work_items")
    assert hasattr(c, "checkpoint_checks")
    assert hasattr(c, "scheduled_scripts")
    assert hasattr(c, "ai_chat_sessions")
    assert not hasattr(c, "notes")
    assert not hasattr(c, "note_folders")
    assert not hasattr(c, "idea_boards")


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


@rsps_lib.activate
def test_workflows_set_duplicate_of(client: AweClient):
    other_id = "ffffffff-ffff-ffff-ffff-ffffffffffff"
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/workflows/{WF_ID}/duplicate-of", json=wf_dict())
    wf = client.workflows.set_duplicate_of(WF_ID, other_id)
    assert isinstance(wf, Workflow)
    assert _body() == {"duplicate_of_workflow_id": other_id}


@rsps_lib.activate
def test_workflows_clear_duplicate_of(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/workflows/{WF_ID}/duplicate-of", json=wf_dict())
    wf = client.workflows.clear_duplicate_of(WF_ID)
    assert isinstance(wf, Workflow)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_workflows_list_duplicates(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows/{WF_ID}/duplicates", json=[wf_dict()])
    result = client.workflows.list_duplicates(WF_ID)
    assert isinstance(result[0], Workflow)


@rsps_lib.activate
def test_workflows_save_as_template(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/workflows/{WF_ID}/save-as-template",
        json=wf_with_tasks_dict(),
    )
    result = client.workflows.save_as_template(WF_ID, name="My Template")
    assert isinstance(result, WorkflowWithTasks)
    assert _body() == {"name": "My Template"}


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
def test_tasks_update_decision_input_port_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, decision_input_port=None)
    body = _body()
    assert "decision_input_port" in body
    assert body["decision_input_port"] is None


@rsps_lib.activate
def test_tasks_update_decision_input_port_value_sends_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, decision_input_port="route")
    assert _body()["decision_input_port"] == "route"


@rsps_lib.activate
def test_tasks_update_effort_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, effort=None)
    body = _body()
    assert "effort" in body
    assert body["effort"] is None


@rsps_lib.activate
def test_tasks_update_effort_value_sends_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, effort=5)
    assert _body()["effort"] == 5


@rsps_lib.activate
def test_tasks_update_status_enum_sends_wire_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, status=Status.IN_PROGRESS)
    assert _body()["status"] == "In Progress"


@rsps_lib.activate
def test_tasks_update_due_time_omitted_does_not_send_key(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, name="x")
    assert "due_time" not in _body()


@rsps_lib.activate
def test_tasks_update_due_time_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, due_time=None)
    body = _body()
    assert "due_time" in body
    assert body["due_time"] is None


@rsps_lib.activate
def test_tasks_update_due_time_value_sends_isoformat(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    due = datetime(2026, 3, 1, 9, 0, tzinfo=timezone.utc)
    client.tasks.update(TASK_ID, due_time=due)
    assert _body()["due_time"] == due.isoformat()


@rsps_lib.activate
def test_tasks_update_branch_name_omitted_does_not_send_key(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, name="x")
    assert "branch_name" not in _body()


@rsps_lib.activate
def test_tasks_update_branch_name_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, branch_name=None)
    body = _body()
    assert "branch_name" in body
    assert body["branch_name"] is None


@rsps_lib.activate
def test_tasks_update_branch_name_value_sends_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, branch_name="feature/x")
    assert _body()["branch_name"] == "feature/x"


@rsps_lib.activate
def test_tasks_update_port_namespace_omitted_does_not_send_key(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, name="x")
    assert "port_namespace" not in _body()


@rsps_lib.activate
def test_tasks_update_port_namespace_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, port_namespace=None)
    body = _body()
    assert "port_namespace" in body
    assert body["port_namespace"] is None


@rsps_lib.activate
def test_tasks_update_port_namespace_value_sends_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/tasks/{TASK_ID}", json=task_dict())
    client.tasks.update(TASK_ID, port_namespace="review")
    assert _body()["port_namespace"] == "review"


@rsps_lib.activate
def test_tasks_request_rework(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/rework", json=task_dict(status="Reworked")
    )
    t = client.tasks.request_rework(TASK_ID)
    assert isinstance(t, Task)
    assert _method() == "POST"


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
def test_task_ports_get_workflow_ports(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/workflows/{WF_ID}/ports", json=[port_spec_dict()])
    result = client.task_ports.get_workflow_ports(WF_ID)
    assert isinstance(result[0], TaskPortSpec)


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


@rsps_lib.activate
def test_task_ports_patch_outputs(client: AweClient):
    rsps_lib.add(rsps_lib.PATCH, f"{API_URL}/tasks/{TASK_ID}/outputs", json=task_dict())
    result = client.task_ports.patch_outputs(TASK_ID, {"y": 2})
    assert isinstance(result, Task)
    assert _body() == {"values": {"y": 2}}


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


# ── TaskSecretsClient ─────────────────────────────────────────────────────────


@rsps_lib.activate
def test_task_secrets_patch(client: AweClient):
    rsps_lib.add(rsps_lib.PATCH, f"{API_URL}/tasks/{TASK_ID}/secrets", status=204)
    client.task_secrets.patch(TASK_ID, {"api_key": "s3cr3t", "old_key": None})
    assert _method() == "PATCH"
    assert _body() == {"values": {"api_key": "s3cr3t", "old_key": None}}


@rsps_lib.activate
def test_task_secrets_get(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/secrets", json={"values": {"api_key": "s3cr3t"}}
    )
    result = client.task_secrets.get(TASK_ID)
    assert result == {"api_key": "s3cr3t"}


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
        TASK_ID,
        "Failure",
        now,
        now,
        run_id=RUN_ID,
        runner_id="runner-1",
        error_message="boom",
        branch_name="feature/x",
    )
    body = _body()
    assert body["run_id"] == RUN_ID
    assert body["runner_id"] == "runner-1"
    assert body["error_message"] == "boom"
    assert body["branch_name"] == "feature/x"


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
        TASK_ID,
        "Success",
        now,
        now,
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
        json=wf_dict(),
    )
    result = client.jobs.clone_workflow(JOB_ID, WF_ID)
    assert isinstance(result, Workflow)
    assert "name" not in _body()


@rsps_lib.activate
def test_jobs_clone_workflow_with_name_override(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/jobs/{JOB_ID}/workflows/from-template/{WF_ID}",
        json=wf_dict(name="Renamed Clone"),
    )
    result = client.jobs.clone_workflow(JOB_ID, WF_ID, name="Renamed Clone")
    assert result.name == "Renamed Clone"
    assert _body()["name"] == "Renamed Clone"


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


@rsps_lib.activate
def test_jobs_get_workflow_allocations(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/jobs/{JOB_ID}/workflow-allocations",
        json=[
            {
                "workflow_id": WF_ID,
                "start_task_id": TASK_ID,
                "assigned_to": "user1",
                "team_role_ids": [ROLE_ID],
            }
        ],
    )
    result = client.jobs.get_workflow_allocations(JOB_ID)
    assert isinstance(result[0], WorkflowAllocation)
    assert result[0].workflow_id == uuid.UUID(WF_ID)


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


# ── ProjectsClient ────────────────────────────────────────────────────────────


@rsps_lib.activate
def test_projects_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/projects", json=[project_dict()])
    result = client.projects.list()
    assert isinstance(result[0], Project)


@rsps_lib.activate
def test_projects_list_with_team_id(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/projects", json=[])
    client.projects.list(team_id=TEAM_ID)
    assert f"team_id={TEAM_ID}" in _url()


@rsps_lib.activate
def test_projects_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/projects/{PROJECT_ID}", json=project_dict())
    result = client.projects.get(PROJECT_ID)
    assert isinstance(result, ProjectWithJobs)
    assert result.project.id == uuid.UUID(PROJECT_ID)


@rsps_lib.activate
def test_projects_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/projects/{PROJECT_ID}", status=204)
    client.projects.delete(PROJECT_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_projects_create_requires_project_code(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/projects", json=project_dict())
    p = client.projects.create("My Project", "P1")
    assert isinstance(p, Project)
    assert _body()["project_code"] == "P1"


@rsps_lib.activate
def test_projects_update_archived(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/projects/{PROJECT_ID}", json=project_dict(archived=True))
    p = client.projects.update(PROJECT_ID, archived=True)
    assert p.archived is True
    assert _body()["archived"] is True


# ── TaskHistoryClient ─────────────────────────────────────────────────────────


@rsps_lib.activate
def test_task_history_get_task_history(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/tasks/{TASK_ID}/history",
        json=[task_history_entry_dict()],
    )
    result = client.task_history.get_task_history(TASK_ID)
    assert isinstance(result[0], TaskStateHistoryEntry)


@rsps_lib.activate
def test_task_history_get_task_history_with_filters(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/tasks/{TASK_ID}/history",
        json=[],
    )
    client.task_history.get_task_history(
        TASK_ID, actor_type="user", from_status="Ready", to_status="In Progress", limit=10
    )
    url = _url()
    assert "actor_type=user" in url
    assert "limit=10" in url


@rsps_lib.activate
def test_task_history_get_job_task_history(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/jobs/{JOB_ID}/task-history",
        json=[task_history_entry_dict()],
    )
    result = client.task_history.get_job_task_history(JOB_ID, task_id=TASK_ID)
    assert isinstance(result[0], TaskStateHistoryEntry)
    assert f"task_id={TASK_ID}" in _url()


@rsps_lib.activate
def test_task_history_list(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/task-history",
        json=[task_history_entry_dict()],
    )
    result = client.task_history.list()
    assert isinstance(result[0], TaskStateHistoryEntry)


# ── ConnectionsClient ─────────────────────────────────────────────────────────


@rsps_lib.activate
def test_connections_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/connections", json=[connection_dict()])
    result = client.connections.list()
    assert isinstance(result[0], Connection)


@rsps_lib.activate
def test_connections_list_with_team_id(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/connections", json=[])
    client.connections.list(team_id=TEAM_ID)
    assert f"team_id={TEAM_ID}" in _url()


@rsps_lib.activate
def test_connections_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/connections", json=connection_dict())
    c = client.connections.create("Conn", "bearer_token", TEAM_ID)
    assert isinstance(c, Connection)
    assert _body()["connection_type"] == "bearer_token"


@rsps_lib.activate
def test_connections_patch_secret(client: AweClient):
    rsps_lib.add(rsps_lib.PATCH, f"{API_URL}/connections/{CONN_ID}/secret", status=204)
    client.connections.patch_secret(CONN_ID, "s3cr3t")
    assert _method() == "PATCH"
    assert _body()["value"] == "s3cr3t"


@rsps_lib.activate
def test_connections_test(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/connections/{CONN_ID}/test",
        json={"success": True, "message": "ok"},
    )
    result = client.connections.test(CONN_ID)
    assert isinstance(result, ConnectionTestResult)
    assert result.success is True


@rsps_lib.activate
def test_connections_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/connections/{CONN_ID}", status=204)
    client.connections.delete(CONN_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_connections_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/connections/{CONN_ID}", json=connection_dict())
    c = client.connections.get(CONN_ID)
    assert isinstance(c, Connection)
    assert c.id == uuid.UUID(CONN_ID)


@rsps_lib.activate
def test_connections_update(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT, f"{API_URL}/connections/{CONN_ID}", json=connection_dict(name="Renamed")
    )
    c = client.connections.update(CONN_ID, name="Renamed")
    assert c.name == "Renamed"
    assert _body() == {"name": "Renamed"}


@rsps_lib.activate
def test_connections_test_config(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/connections/test",
        json={"success": False, "message": "auth failed"},
    )
    result = client.connections.test_config("smtp", {"host": "smtp.example.com"}, "s3cr3t")
    assert isinstance(result, ConnectionTestResult)
    assert result.success is False
    assert _body() == {
        "connection_type": "smtp",
        "config": {"host": "smtp.example.com"},
        "secret": "s3cr3t",
    }


@rsps_lib.activate
def test_connections_list_mcp_tools(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/connections/{CONN_ID}/mcp-tools",
        json={"tools": [{"name": "search"}]},
    )
    tools = client.connections.list_mcp_tools(CONN_ID, "https://mcp.example.com")
    assert tools == [{"name": "search"}]
    assert _body()["mcp_server_url"] == "https://mcp.example.com"


@rsps_lib.activate
def test_connections_get_task_connection(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/tasks/{TASK_ID}/connection",
        json={"connection_type": "smtp", "config": {}, "secret": "s3cr3t"},
    )
    resolved = client.connections.get_task_connection(TASK_ID)
    assert isinstance(resolved, ResolvedConnection)
    assert resolved.secret == "s3cr3t"


# ── WorkItemsClient ───────────────────────────────────────────────────────────


@rsps_lib.activate
def test_work_items_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/work-items", json=[work_item_dict()])
    result = client.work_items.list()
    assert isinstance(result[0], WorkItem)


@rsps_lib.activate
def test_work_items_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/work-items", json=work_item_dict())
    w = client.work_items.create("WI")
    assert isinstance(w, WorkItem)
    assert _body()["name"] == "WI"


@rsps_lib.activate
def test_work_items_update_effort_omitted_does_not_send_key(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, name="x")
    assert "effort" not in _body()


@rsps_lib.activate
def test_work_items_update_effort_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, effort=None)
    body = _body()
    assert "effort" in body
    assert body["effort"] is None


@rsps_lib.activate
def test_work_items_update_effort_value_sends_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, effort=8)
    assert _body()["effort"] == 8


@rsps_lib.activate
def test_work_items_update_team_id_omitted_does_not_send_key(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, name="x")
    assert "team_id" not in _body()


@rsps_lib.activate
def test_work_items_update_team_id_none_sends_null(client: AweClient):
    """team_id=None makes the work item private."""
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, team_id=None)
    body = _body()
    assert "team_id" in body
    assert body["team_id"] is None


@rsps_lib.activate
def test_work_items_update_team_id_value_sends_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, team_id=TEAM_ID)
    assert _body()["team_id"] == TEAM_ID


@rsps_lib.activate
def test_work_items_update_port_namespace_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, port_namespace=None)
    body = _body()
    assert "port_namespace" in body
    assert body["port_namespace"] is None


@rsps_lib.activate
def test_work_items_update_decision_input_port_omitted_does_not_send_key(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, name="x")
    assert "decision_input_port" not in _body()


@rsps_lib.activate
def test_work_items_update_decision_input_port_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, decision_input_port=None)
    body = _body()
    assert "decision_input_port" in body
    assert body["decision_input_port"] is None


@rsps_lib.activate
def test_work_items_update_decision_input_port_value_sends_value(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, decision_input_port="route")
    assert _body()["decision_input_port"] == "route"


@rsps_lib.activate
def test_work_items_update_assigned_to_none_sends_null(client: AweClient):
    rsps_lib.add(rsps_lib.PUT, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    client.work_items.update(WORK_ITEM_ID, assigned_to=None)
    body = _body()
    assert "assigned_to" in body
    assert body["assigned_to"] is None


@rsps_lib.activate
def test_work_items_get(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/work-items/{WORK_ITEM_ID}", json=work_item_dict())
    w = client.work_items.get(WORK_ITEM_ID)
    assert isinstance(w, WorkItem)
    assert w.id == uuid.UUID(WORK_ITEM_ID)


@rsps_lib.activate
def test_work_items_list_ports(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/ports",
        json=[work_item_port_dict()],
    )
    result = client.work_items.list_ports(WORK_ITEM_ID)
    assert isinstance(result[0], WorkItemPortSpec)


@rsps_lib.activate
def test_work_items_create_port(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/ports",
        json=work_item_port_dict(),
    )
    p = client.work_items.create_port(WORK_ITEM_ID, "input", "text", "string")
    assert isinstance(p, WorkItemPortSpec)
    assert _body() == {"direction": "input", "name": "text", "value_type": "string"}


@rsps_lib.activate
def test_work_items_update_port(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/ports/{PORT_ID}",
        json=work_item_port_dict(name="renamed"),
    )
    p = client.work_items.update_port(WORK_ITEM_ID, PORT_ID, name="renamed")
    assert p.name == "renamed"
    assert _body() == {"name": "renamed"}


@rsps_lib.activate
def test_work_items_delete_port(client: AweClient):
    rsps_lib.add(
        rsps_lib.DELETE, f"{API_URL}/work-items/{WORK_ITEM_ID}/ports/{PORT_ID}", status=204
    )
    client.work_items.delete_port(WORK_ITEM_ID, PORT_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_work_items_get_script(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/script",
        json=work_item_script_dict(),
    )
    s = client.work_items.get_script(WORK_ITEM_ID)
    assert isinstance(s, WorkItemScript)


@rsps_lib.activate
def test_work_items_upsert_script(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/script",
        json=work_item_script_dict(script_type="shell"),
    )
    s = client.work_items.upsert_script(WORK_ITEM_ID, script_type="shell", script_body="echo hi")
    assert s.script_type == "shell"
    assert _body() == {"script_type": "shell", "script_body": "echo hi"}


@rsps_lib.activate
def test_work_items_delete_script(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/work-items/{WORK_ITEM_ID}/script", status=204)
    client.work_items.delete_script(WORK_ITEM_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_work_items_list_checks(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/checks",
        json=[work_item_check_dict()],
    )
    result = client.work_items.list_checks(WORK_ITEM_ID)
    assert isinstance(result[0], WorkItemCheck)


@rsps_lib.activate
def test_work_items_create_check(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/checks",
        json=work_item_check_dict(),
    )
    c = client.work_items.create_check(WORK_ITEM_ID, "QA", "manual")
    assert isinstance(c, WorkItemCheck)
    assert _body()["check_type"] == "manual"


@rsps_lib.activate
def test_work_items_update_check(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/checks/{CHECK_ID}",
        json=work_item_check_dict(name="Renamed"),
    )
    c = client.work_items.update_check(WORK_ITEM_ID, CHECK_ID, name="Renamed")
    assert c.name == "Renamed"
    assert _body() == {"name": "Renamed"}


@rsps_lib.activate
def test_work_items_delete_check(client: AweClient):
    rsps_lib.add(
        rsps_lib.DELETE, f"{API_URL}/work-items/{WORK_ITEM_ID}/checks/{CHECK_ID}", status=204
    )
    client.work_items.delete_check(WORK_ITEM_ID, CHECK_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_work_items_get_check_script(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/checks/{CHECK_ID}/script",
        json=work_item_check_script_dict(),
    )
    s = client.work_items.get_check_script(WORK_ITEM_ID, CHECK_ID)
    assert isinstance(s, WorkItemCheckScript)


@rsps_lib.activate
def test_work_items_upsert_check_script(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/checks/{CHECK_ID}/script",
        json=work_item_check_script_dict(locked_on_clone=True),
    )
    s = client.work_items.upsert_check_script(WORK_ITEM_ID, CHECK_ID, locked_on_clone=True)
    assert s.locked_on_clone is True
    assert _body() == {"locked_on_clone": True}


@rsps_lib.activate
def test_work_items_delete_check_script(client: AweClient):
    rsps_lib.add(
        rsps_lib.DELETE,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/checks/{CHECK_ID}/script",
        status=204,
    )
    client.work_items.delete_check_script(WORK_ITEM_ID, CHECK_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_work_items_list_team_roles(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/team-roles",
        json=[work_item_team_role_dict()],
    )
    result = client.work_items.list_team_roles(WORK_ITEM_ID)
    assert isinstance(result[0], WorkItemTeamRole)


@rsps_lib.activate
def test_work_items_assign_team_role(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/team-roles",
        json=work_item_team_role_dict(),
    )
    r = client.work_items.assign_team_role(WORK_ITEM_ID, ROLE_ID)
    assert isinstance(r, WorkItemTeamRole)
    assert _body() == {"team_role_id": ROLE_ID}


@rsps_lib.activate
def test_work_items_remove_team_role(client: AweClient):
    rsps_lib.add(
        rsps_lib.DELETE,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/team-roles/{ROLE_ID}",
        status=204,
    )
    client.work_items.remove_team_role(WORK_ITEM_ID, ROLE_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_work_items_list_branches(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/branches",
        json=[work_item_branch_dict()],
    )
    result = client.work_items.list_branches(WORK_ITEM_ID)
    assert isinstance(result[0], WorkItemBranch)


@rsps_lib.activate
def test_work_items_create_branch(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/branches",
        json=work_item_branch_dict(),
    )
    b = client.work_items.create_branch(WORK_ITEM_ID, "Approved", "Approved path")
    assert isinstance(b, WorkItemBranch)
    assert _body() == {"label": "Approved", "task_name": "Approved path"}


@rsps_lib.activate
def test_work_items_update_branch(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/branches/{BRANCH_ID}",
        json=work_item_branch_dict(label="Rejected"),
    )
    b = client.work_items.update_branch(WORK_ITEM_ID, BRANCH_ID, label="Rejected")
    assert b.label == "Rejected"
    assert _body() == {"label": "Rejected"}


@rsps_lib.activate
def test_work_items_delete_branch(client: AweClient):
    rsps_lib.add(
        rsps_lib.DELETE,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/branches/{BRANCH_ID}",
        status=204,
    )
    client.work_items.delete_branch(WORK_ITEM_ID, BRANCH_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_work_items_instantiate(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/work-items/{WORK_ITEM_ID}/instantiate",
        json={"primary_task": task_dict(), "branch_tasks": []},
    )
    result = client.work_items.instantiate(WORK_ITEM_ID, WF_ID)
    assert isinstance(result.primary_task, Task)
    assert _body()["workflow_id"] == WF_ID


@rsps_lib.activate
def test_work_items_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/work-items/{WORK_ITEM_ID}", status=204)
    client.work_items.delete(WORK_ITEM_ID)
    assert _method() == "DELETE"


# ── CheckpointChecksClient ────────────────────────────────────────────────────


@rsps_lib.activate
def test_checkpoint_checks_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/tasks/{TASK_ID}/checks", json=[checkpoint_check_dict()])
    result = client.checkpoint_checks.list(TASK_ID)
    assert isinstance(result[0], CheckpointCheck)


@rsps_lib.activate
def test_checkpoint_checks_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/tasks/{TASK_ID}/checks", json=checkpoint_check_dict())
    c = client.checkpoint_checks.create(TASK_ID, "QA", "manual")
    assert isinstance(c, CheckpointCheck)
    assert _body()["check_type"] == "manual"


@rsps_lib.activate
def test_checkpoint_checks_verify(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/tasks/{TASK_ID}/checks/{CHECK_ID}/verify",
        json=checkpoint_check_dict(status="passed"),
    )
    c = client.checkpoint_checks.verify(TASK_ID, CHECK_ID, True, note="looks good")
    assert c.status == "passed"
    assert _body()["passed"] is True
    assert _body()["note"] == "looks good"


@rsps_lib.activate
def test_checkpoint_checks_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/tasks/{TASK_ID}/checks/{CHECK_ID}", status=204)
    client.checkpoint_checks.delete(TASK_ID, CHECK_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_checkpoint_checks_update(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/tasks/{TASK_ID}/checks/{CHECK_ID}",
        json=checkpoint_check_dict(name="Renamed"),
    )
    c = client.checkpoint_checks.update(TASK_ID, CHECK_ID, name="Renamed")
    assert c.name == "Renamed"
    assert _body() == {"name": "Renamed"}


@rsps_lib.activate
def test_checkpoint_checks_list_passthrough(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/workflows/{WF_ID}/passthrough-checkpoints",
        json={"task_ids": [TASK_ID]},
    )
    result = client.checkpoint_checks.list_passthrough(WF_ID)
    assert isinstance(result, PassthroughCheckpoints)
    assert result.task_ids == [uuid.UUID(TASK_ID)]


@rsps_lib.activate
def test_checkpoint_checks_get_script(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/tasks/{TASK_ID}/checks/{CHECK_ID}/script",
        json=checkpoint_check_script_dict(),
    )
    s = client.checkpoint_checks.get_script(TASK_ID, CHECK_ID)
    assert isinstance(s, CheckpointCheckScript)


@rsps_lib.activate
def test_checkpoint_checks_upsert_script(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/tasks/{TASK_ID}/checks/{CHECK_ID}/script",
        json=checkpoint_check_script_dict(locked_on_clone=True),
    )
    s = client.checkpoint_checks.upsert_script(TASK_ID, CHECK_ID, locked_on_clone=True)
    assert s.locked_on_clone is True
    assert _body() == {"locked_on_clone": True}


@rsps_lib.activate
def test_checkpoint_checks_delete_script(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/tasks/{TASK_ID}/checks/{CHECK_ID}/script", status=204)
    client.checkpoint_checks.delete_script(TASK_ID, CHECK_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_checkpoint_checks_run(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/tasks/{TASK_ID}/checks/{CHECK_ID}/run",
        json=checkpoint_check_run_dict(),
    )
    r = client.checkpoint_checks.run(TASK_ID, CHECK_ID)
    assert isinstance(r, CheckpointCheckRun)


@rsps_lib.activate
def test_checkpoint_checks_list_runs(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/tasks/{TASK_ID}/checks/{CHECK_ID}/runs",
        json=[checkpoint_check_run_dict()],
    )
    result = client.checkpoint_checks.list_runs(TASK_ID, CHECK_ID)
    assert isinstance(result[0], CheckpointCheckRun)


# ── ScheduledScriptsClient ────────────────────────────────────────────────────


@rsps_lib.activate
def test_scheduled_scripts_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/scheduled-scripts", json=[scheduled_script_dict()])
    result = client.scheduled_scripts.list()
    assert isinstance(result[0], ScheduledScript)


@rsps_lib.activate
def test_scheduled_scripts_list_with_team_id(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/scheduled-scripts", json=[])
    client.scheduled_scripts.list(team_id=TEAM_ID)
    assert f"team_id={TEAM_ID}" in _url()


@rsps_lib.activate
def test_scheduled_scripts_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/scheduled-scripts", json=scheduled_script_dict())
    s = client.scheduled_scripts.create("Nightly", TEAM_ID, "0 0 * * *")
    assert isinstance(s, ScheduledScript)
    assert _body()["cron_expression"] == "0 0 * * *"


@rsps_lib.activate
def test_scheduled_scripts_trigger_accepted_with_empty_body_returns_none(client: AweClient):
    """The server returns 202 Accepted with no body — must not raise."""
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/scheduled-scripts/{SCHEDULE_ID}/trigger", status=202)
    result = client.scheduled_scripts.trigger(SCHEDULE_ID)
    assert result is None


@rsps_lib.activate
def test_scheduled_scripts_report_run(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/scheduled-scripts/{SCHEDULE_ID}/runs",
        json={
            "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "schedule_id": SCHEDULE_ID,
            "triggered_by": "schedule",
            "created_at": TS,
            "status": "Success",
        },
    )
    r = client.scheduled_scripts.report_run(SCHEDULE_ID, "schedule", "Success")
    assert isinstance(r, ScheduledScriptRun)
    assert _body()["triggered_by"] == "schedule"


@rsps_lib.activate
def test_scheduled_scripts_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/scheduled-scripts/{SCHEDULE_ID}", status=204)
    client.scheduled_scripts.delete(SCHEDULE_ID)
    assert _method() == "DELETE"


@rsps_lib.activate
def test_scheduled_scripts_get(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET, f"{API_URL}/scheduled-scripts/{SCHEDULE_ID}", json=scheduled_script_dict()
    )
    s = client.scheduled_scripts.get(SCHEDULE_ID)
    assert isinstance(s, ScheduledScript)
    assert s.id == uuid.UUID(SCHEDULE_ID)


@rsps_lib.activate
def test_scheduled_scripts_update(client: AweClient):
    rsps_lib.add(
        rsps_lib.PUT,
        f"{API_URL}/scheduled-scripts/{SCHEDULE_ID}",
        json=scheduled_script_dict(is_active=False),
    )
    s = client.scheduled_scripts.update(SCHEDULE_ID, is_active=False)
    assert s.is_active is False
    assert _body() == {"is_active": False}


@rsps_lib.activate
def test_scheduled_scripts_get_dispatch(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/scheduled-scripts/{SCHEDULE_ID}/dispatch",
        json={
            "id": SCHEDULE_ID,
            "script_type": "webhook",
            "timeout_secs": 30,
            "state": {},
            "endpoint": "https://example.com/hook",
        },
    )
    d = client.scheduled_scripts.get_dispatch(SCHEDULE_ID)
    assert isinstance(d, ScheduledScriptDispatch)
    assert d.connection is None


@rsps_lib.activate
def test_scheduled_scripts_list_runs(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/scheduled-scripts/{SCHEDULE_ID}/runs",
        json=[
            {
                "id": RUN_ID,
                "schedule_id": SCHEDULE_ID,
                "triggered_by": "schedule",
                "created_at": TS,
                "status": "Success",
            }
        ],
    )
    result = client.scheduled_scripts.list_runs(SCHEDULE_ID)
    assert isinstance(result[0], ScheduledScriptRun)


# ── AiChatSessionsClient ──────────────────────────────────────────────────────


@rsps_lib.activate
def test_ai_chat_sessions_list(client: AweClient):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/ai-sessions", json=[chat_session_dict()])
    result = client.ai_chat_sessions.list()
    assert isinstance(result[0], ChatSession)


@rsps_lib.activate
def test_ai_chat_sessions_create(client: AweClient):
    rsps_lib.add(rsps_lib.POST, f"{API_URL}/ai-sessions", json=chat_session_dict())
    s = client.ai_chat_sessions.create("New chat")
    assert isinstance(s, ChatSession)
    assert _body()["title"] == "New chat"


@rsps_lib.activate
def test_ai_chat_sessions_append_message(client: AweClient):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/ai-sessions/{SESSION_ID}/messages",
        json=chat_message_dict(),
    )
    m = client.ai_chat_sessions.append_message(SESSION_ID, "user", "hello")
    assert isinstance(m, ChatMessage)
    assert _body() == {"role": "user", "content": "hello"}


@rsps_lib.activate
def test_ai_chat_sessions_list_messages(client: AweClient):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/ai-sessions/{SESSION_ID}/messages",
        json=[chat_message_dict()],
    )
    result = client.ai_chat_sessions.list_messages(SESSION_ID)
    assert isinstance(result[0], ChatMessage)


@rsps_lib.activate
def test_ai_chat_sessions_delete(client: AweClient):
    rsps_lib.add(rsps_lib.DELETE, f"{API_URL}/ai-sessions/{SESSION_ID}", status=204)
    client.ai_chat_sessions.delete(SESSION_ID)
    assert _method() == "DELETE"


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
