"""Tests for pyawe dataclass models and helper functions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime

from pyawe.models import (
    BranchTaskResult,
    ChatMessage,
    ChatSession,
    CheckpointCheck,
    CheckpointCheckRun,
    CheckpointCheckScript,
    Connection,
    ConnectionTestResult,
    CreateLoopBlockResponse,
    DataBinding,
    ExecutionProfile,
    InstantiateWorkItemResponse,
    Job,
    JobWithWorkflows,
    LoginInfo,
    LoopBlock,
    LoopType,
    PassthroughCheckpoints,
    PortDirection,
    PortValueType,
    Project,
    ResolvedConnection,
    ScheduledScript,
    ScheduledScriptDispatch,
    ScheduledScriptRun,
    ScheduleStatus,
    ScriptType,
    Status,
    Task,
    TaskLink,
    TaskPortSpec,
    TaskPortValues,
    TaskRun,
    TaskScript,
    TaskTeamRole,
    TaskType,
    TaskWithContext,
    Workflow,
    WorkflowWithTasks,
    WorkItem,
    WorkItemBranch,
    WorkItemCheck,
    WorkItemCheckScript,
    WorkItemPortSpec,
    WorkItemScript,
    WorkItemTeamRole,
    _dt,
    _uuid,
)

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
LOOP_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
INNER_WF_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff"
PROJECT_ID = "12121212-1212-1212-1212-121212121212"
CHECK_ID = "13131313-1313-1313-1313-131313131313"
SCHEDULE_ID = "14141414-1414-1414-1414-141414141414"
SESSION_ID = "15151515-1515-1515-1515-151515151515"
TEAM_ID = "dddddddd-dddd-dddd-dddd-dddddddddddd"
TS = "2024-01-15T12:00:00Z"


# ── _dt ───────────────────────────────────────────────────────────────────────


def test_dt_parses_iso_without_tz():
    result = _dt("2024-01-15T12:00:00")
    assert isinstance(result, datetime)
    assert result.year == 2024
    assert result.month == 1
    assert result.day == 15


def test_dt_z_suffix_becomes_utc():
    result = _dt("2024-01-15T12:00:00Z")
    assert result is not None
    assert result.tzinfo is not None
    assert result.utcoffset().total_seconds() == 0  # type: ignore[union-attr]


def test_dt_none_returns_none():
    assert _dt(None) is None


def test_dt_with_utc_offset():
    result = _dt("2024-01-15T12:00:00+05:30")
    assert result is not None
    assert result.utcoffset().total_seconds() == 5.5 * 3600  # type: ignore[union-attr]


# ── _uuid ─────────────────────────────────────────────────────────────────────


def test_uuid_parses_string():
    result = _uuid(WF_ID)
    assert isinstance(result, uuid.UUID)
    assert str(result) == WF_ID


def test_uuid_none_returns_none():
    assert _uuid(None) is None


# ── enums ─────────────────────────────────────────────────────────────────────


def test_status_values_match_wire_format():
    assert Status.NOT_STARTED == "Not Started"
    assert Status.READY == "Ready"
    assert Status.IN_PROGRESS == "In Progress"
    assert Status.ON_HOLD == "On Hold"
    assert Status.COMPLETE == "Complete"
    assert Status.CANCELLED == "Cancelled"
    assert Status.REWORKED == "Reworked"
    assert Status.FAILED == "Failed"


def test_status_round_trips_new_system_managed_variants():
    """Reworked/Failed must parse from the wire without raising — this was the
    single highest-severity bug identified in the awe-server sync: any task or
    workflow read with one of these statuses used to raise ValueError."""
    assert Status("Reworked") is Status.REWORKED
    assert Status("Failed") is Status.FAILED
    t = Task.from_dict(_task(status="Reworked"))
    assert t.status == Status.REWORKED
    t2 = Task.from_dict(_task(status="Failed"))
    assert t2.status == Status.FAILED


def test_status_is_str_subclass():
    assert isinstance(Status.IN_PROGRESS, str)


def test_status_serializes_correctly_in_json():
    """json.dumps must use the wire value, not the Python name."""
    payload = json.dumps({"status": Status.IN_PROGRESS})
    assert '"In Progress"' in payload
    assert "IN_PROGRESS" not in payload


def test_schedule_status_values():
    assert ScheduleStatus.NA == "N/A"
    assert ScheduleStatus.ON_TIME == "On Time"
    assert ScheduleStatus.AT_RISK == "At Risk"
    assert ScheduleStatus.LATE == "Late"


def test_task_type_values():
    assert TaskType.STANDARD == "standard"
    assert TaskType.DECISION == "decision"
    assert TaskType.AUTOMATED == "automated"
    assert TaskType.LOOP_BLOCK == "loop_block"
    assert TaskType.CHECKPOINT == "checkpoint"


def test_port_direction_values():
    assert PortDirection.INPUT == "input"
    assert PortDirection.OUTPUT == "output"


def test_port_value_type_values():
    assert PortValueType.STRING == "string"
    assert PortValueType.NUMBER == "number"
    assert PortValueType.BOOLEAN == "boolean"
    assert PortValueType.JSON == "json"
    assert PortValueType.FILE == "file"
    assert PortValueType.DAM_ASSET == "dam_asset"
    assert PortValueType.SECRET == "secret"


def test_script_type_values():
    assert ScriptType.WEBHOOK == "webhook"
    assert ScriptType.SHELL == "shell"
    assert ScriptType.PYTHON == "python"
    assert ScriptType.MCP_TOOL == "mcp_tool"
    assert ScriptType.EMAIL == "email"


def test_loop_type_values():
    assert LoopType.COUNT == "count"
    assert LoopType.WHILE == "while"
    assert LoopType.FOR_EACH == "for_each"


# ── LoginInfo ─────────────────────────────────────────────────────────────────


def test_login_info_from_dict_full():
    d = {
        "token": "tok123",
        "user": {"id": "uid1", "email": "a@b.com", "username": "alice"},
        "roles": ["admin"],
        "permissions": ["read", "write"],
    }
    info = LoginInfo.from_dict(d)
    assert info.token == "tok123"
    assert info.user_id == "uid1"
    assert info.email == "a@b.com"
    assert info.username == "alice"
    assert info.roles == ["admin"]
    assert info.permissions == ["read", "write"]


def test_login_info_defaults_empty_lists():
    d = {"token": "t", "user": {"id": "u", "email": "e@e.com", "username": "u"}}
    info = LoginInfo.from_dict(d)
    assert info.roles == []
    assert info.permissions == []


# ── Workflow ──────────────────────────────────────────────────────────────────


def _wf(**kw: object) -> dict:
    d: dict = {
        "id": WF_ID,
        "name": "WF",
        "is_template": False,
        "created_at": TS,
        "updated_at": TS,
        "status": "Not Started",
        "schedule_status": "N/A",
        "is_shared": False,
    }
    d.update(kw)
    return d


def test_workflow_from_dict_minimal():
    wf = Workflow.from_dict(_wf())
    assert wf.id == uuid.UUID(WF_ID)
    assert wf.name == "WF"
    assert wf.status == Status.NOT_STARTED
    assert wf.schedule_status == ScheduleStatus.NA
    assert wf.is_shared is False
    assert wf.description is None
    assert wf.job_id is None
    assert wf.team_id is None
    assert wf.parent_loop_block_id is None


def test_workflow_from_dict_with_optionals():
    wf = Workflow.from_dict(
        _wf(
            description="desc",
            job_id=JOB_ID,
            team_id="dddddddd-dddd-dddd-dddd-dddddddddddd",
            created_by="user1",
            parent_loop_block_id=LOOP_ID,
        )
    )
    assert wf.description == "desc"
    assert isinstance(wf.job_id, uuid.UUID)
    assert isinstance(wf.team_id, uuid.UUID)
    assert wf.created_by == "user1"
    assert wf.parent_loop_block_id == uuid.UUID(LOOP_ID)


def test_workflow_timestamps_are_aware():
    wf = Workflow.from_dict(_wf())
    assert wf.created_at.tzinfo is not None
    assert wf.updated_at.tzinfo is not None


def test_workflow_from_dict_with_cunav_and_togra_fields():
    wf = Workflow.from_dict(
        _wf(
            organization_id="dddddddd-dddd-dddd-dddd-dddddddddddd",
            ticket_type="bug",
            priority="high",
            reporter_id=WF_ID,
            resolved_at=TS,
            external_reporter_first_name="Jane",
            external_reporter_last_name="Doe",
            external_reporter_email="jane@example.com",
            togra_workflow_id=WF_ID,
            togra_project_id=WF_ID,
            ticket_number=42,
            workflow_number=4,
            project_code="P1",
            ai_confidence=0.87,
            ai_should_route=True,
            duplicate_of_workflow_id=WF_ID,
        )
    )
    assert wf.ticket_type == "bug"
    assert wf.priority == "high"
    assert isinstance(wf.reporter_id, uuid.UUID)
    assert wf.resolved_at is not None
    assert wf.external_reporter_first_name == "Jane"
    assert wf.external_reporter_email == "jane@example.com"
    assert wf.ticket_number == 42
    assert wf.workflow_number == 4
    assert wf.project_code == "P1"
    assert wf.ai_confidence == 0.87
    assert wf.ai_should_route is True
    assert isinstance(wf.duplicate_of_workflow_id, uuid.UUID)
    assert isinstance(wf.organization_id, uuid.UUID)


def test_workflow_reworked_and_failed_status_round_trip():
    wf_r = Workflow.from_dict(_wf(status="Reworked"))
    assert wf_r.status == Status.REWORKED
    wf_f = Workflow.from_dict(_wf(status="Failed"))
    assert wf_f.status == Status.FAILED


# ── Task ──────────────────────────────────────────────────────────────────────


def _task(**kw: object) -> dict:
    d: dict = {
        "id": TASK_ID,
        "name": "T",
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


def test_task_from_dict_minimal():
    t = Task.from_dict(_task())
    assert t.id == uuid.UUID(TASK_ID)
    assert t.workflow_id == uuid.UUID(WF_ID)
    assert t.task_type == "standard"
    assert t.assigned_to is None
    assert t.rework_task_id is None
    assert t.start_time is None
    assert t.end_time is None
    assert t.decision_outcome is None
    assert t.priority == "none"
    assert t.due_time is None
    assert t.branch_name is None
    assert t.task_number is None
    assert t.port_namespace is None
    assert t.reworked_from_task_id is None


def test_task_from_dict_with_all_optionals():
    t = Task.from_dict(
        _task(
            description="desc",
            assigned_to="user-uuid",
            start_time=TS,
            end_time=TS,
            decision_outcome="approve",
            rework_task_id=WF_ID,
            loop_block_id=LOOP_ID,
            input_values={"x": 1},
            output_values={"y": 2},
            priority="high",
            due_time=TS,
            branch_name="feature/x",
            task_number=4,
            port_namespace="review",
            reworked_from_task_id=TASK_ID,
        )
    )
    assert t.description == "desc"
    assert t.assigned_to == "user-uuid"
    assert t.start_time is not None
    assert t.end_time is not None
    assert t.decision_outcome == "approve"
    assert isinstance(t.rework_task_id, uuid.UUID)
    assert isinstance(t.loop_block_id, uuid.UUID)
    assert t.input_values == {"x": 1}
    assert t.priority == "high"
    assert t.due_time is not None
    assert t.branch_name == "feature/x"
    assert t.task_number == 4
    assert t.port_namespace == "review"
    assert t.reworked_from_task_id == uuid.UUID(TASK_ID)


def test_task_type_checkpoint_round_trips():
    t = Task.from_dict(_task(task_type="checkpoint"))
    assert t.task_type == "checkpoint"


# ── TaskLink ──────────────────────────────────────────────────────────────────


def test_task_link_from_dict_minimal():
    link = TaskLink.from_dict({"from_task_id": LINK_FROM, "to_task_id": LINK_TO})
    assert link.from_task_id == uuid.UUID(LINK_FROM)
    assert link.to_task_id == uuid.UUID(LINK_TO)
    assert link.branch_label is None
    assert link.data_bindings is None


def test_task_link_with_branch_label():
    link = TaskLink.from_dict(
        {
            "from_task_id": LINK_FROM,
            "to_task_id": LINK_TO,
            "branch_label": "approved",
        }
    )
    assert link.branch_label == "approved"


# ── DataBinding ───────────────────────────────────────────────────────────────


def test_data_binding_from_dict_uses_from_to_keys():
    binding = DataBinding.from_dict({"from": "output1", "to": "input2"})
    assert binding.from_port == "output1"
    assert binding.to_port == "input2"


def test_data_binding_to_dict_round_trip():
    d = {"from": "output1", "to": "input2"}
    assert DataBinding.from_dict(d).to_dict() == d


def test_data_binding_to_dict_uses_from_not_from_port():
    binding = DataBinding(from_port="out", to_port="in")
    result = binding.to_dict()
    assert "from" in result
    assert "to" in result
    assert "from_port" not in result
    assert "to_port" not in result


# ── TaskWithContext ───────────────────────────────────────────────────────────


def test_task_with_context_from_dict():
    d = {**_task(), "workflow_name": "WF1", "job_id": JOB_ID, "job_name": "J1"}
    twc = TaskWithContext.from_dict(d)
    assert isinstance(twc.task, Task)
    assert twc.workflow_name == "WF1"
    assert isinstance(twc.job_id, uuid.UUID)
    assert twc.job_name == "J1"


def test_task_with_context_without_job():
    d = {**_task(), "workflow_name": "WF2"}
    twc = TaskWithContext.from_dict(d)
    assert twc.job_id is None
    assert twc.job_name is None


# ── WorkflowWithTasks ─────────────────────────────────────────────────────────


def test_workflow_with_tasks_from_dict():
    d = {**_wf(), "tasks": [_task()], "links": [{"from_task_id": LINK_FROM, "to_task_id": LINK_TO}]}
    wwt = WorkflowWithTasks.from_dict(d)
    assert isinstance(wwt.workflow, Workflow)
    assert len(wwt.tasks) == 1
    assert isinstance(wwt.tasks[0], Task)
    assert len(wwt.links) == 1
    assert isinstance(wwt.links[0], TaskLink)


def test_workflow_with_tasks_missing_keys_default_empty():
    wwt = WorkflowWithTasks.from_dict(_wf())
    assert wwt.tasks == []
    assert wwt.links == []


# ── Job ───────────────────────────────────────────────────────────────────────


def _job(**kw: object) -> dict:
    d: dict = {
        "id": JOB_ID,
        "name": "J",
        "status": "Not Started",
        "schedule_status": "N/A",
        "created_at": TS,
        "updated_at": TS,
        "archived": False,
    }
    d.update(kw)
    return d


def test_job_from_dict_minimal():
    j = Job.from_dict(_job())
    assert j.id == uuid.UUID(JOB_ID)
    assert j.name == "J"
    assert j.archived is False
    assert j.team_id is None


def test_job_with_team_id():
    j = Job.from_dict(_job(team_id="dddddddd-dddd-dddd-dddd-dddddddddddd"))
    assert isinstance(j.team_id, uuid.UUID)


# ── JobWithWorkflows ──────────────────────────────────────────────────────────


def test_job_with_workflows_from_dict():
    d = {**_job(), "workflows": [_wf()]}
    jww = JobWithWorkflows.from_dict(d)
    assert isinstance(jww.job, Job)
    assert len(jww.workflows) == 1
    assert isinstance(jww.workflows[0], Workflow)


def test_job_with_workflows_empty():
    jww = JobWithWorkflows.from_dict(_job())
    assert jww.workflows == []


# ── TaskPortSpec ──────────────────────────────────────────────────────────────


def _pspec(**kw: object) -> dict:
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


def test_port_spec_from_dict():
    ps = TaskPortSpec.from_dict(_pspec())
    assert ps.id == uuid.UUID(PORT_ID)
    assert ps.task_id == uuid.UUID(TASK_ID)
    assert ps.direction == "input"
    assert ps.required is True
    assert ps.description is None
    assert ps.default_value is None


def test_port_spec_with_optionals():
    ps = TaskPortSpec.from_dict(_pspec(description="some desc", default_value=42))
    assert ps.description == "some desc"
    assert ps.default_value == 42


# ── TaskPortValues ────────────────────────────────────────────────────────────


def test_port_values_from_dict_with_data():
    pv = TaskPortValues.from_dict({"specs": [_pspec()], "values": {"data_in": "hello"}})
    assert len(pv.specs) == 1
    assert pv.values == {"data_in": "hello"}


def test_port_values_empty_dict():
    pv = TaskPortValues.from_dict({})
    assert pv.specs == []
    assert pv.values is None
    assert pv.secret_set == []


def test_port_values_with_secret_set():
    pv = TaskPortValues.from_dict({"secret_set": ["api_key"]})
    assert pv.secret_set == ["api_key"]


# ── TaskScript ────────────────────────────────────────────────────────────────


def _script(**kw: object) -> dict:
    d: dict = {
        "id": SCRIPT_ID,
        "task_id": TASK_ID,
        "script_type": "webhook",
        "timeout_secs": 30,
        "retry_limit": 3,
        "created_at": TS,
        "updated_at": TS,
    }
    d.update(kw)
    return d


def test_task_script_from_dict_webhook():
    ts = TaskScript.from_dict(_script(endpoint="https://hook.example.com/cb"))
    assert ts.script_type == "webhook"
    assert ts.endpoint == "https://hook.example.com/cb"
    assert ts.script_body is None
    assert ts.execution_profile_id is None


def test_task_script_from_dict_python():
    ts = TaskScript.from_dict(
        _script(
            script_type="python",
            script_body="print('hi')",
            execution_profile_id=PROFILE_ID,
        )
    )
    assert ts.script_type == "python"
    assert ts.script_body == "print('hi')"
    assert isinstance(ts.execution_profile_id, uuid.UUID)


def test_task_script_from_dict_email():
    ts = TaskScript.from_dict(_script(script_type="email", connection_id=CONN_ID, endpoint=None))
    assert ts.script_type == "email"
    assert isinstance(ts.connection_id, uuid.UUID)


# ── TaskRun ───────────────────────────────────────────────────────────────────


def _run(**kw: object) -> dict:
    d: dict = {"id": RUN_ID, "task_id": TASK_ID, "created_at": TS}
    d.update(kw)
    return d


def test_task_run_from_dict_minimal():
    r = TaskRun.from_dict(_run())
    assert r.id == uuid.UUID(RUN_ID)
    assert r.outcome is None
    assert r.error_message is None
    assert r.runner_id is None


def test_task_run_from_dict_full():
    r = TaskRun.from_dict(
        _run(
            outcome="Failure",
            started_at=TS,
            completed_at=TS,
            runner_id="runner-1",
            error_message="timeout",
            input_json={"a": 1},
            output_json={"b": 2},
        )
    )
    assert r.outcome == "Failure"
    assert r.error_message == "timeout"
    assert r.runner_id == "runner-1"
    assert r.started_at is not None
    assert r.input_json == {"a": 1}


# ── TaskTeamRole ──────────────────────────────────────────────────────────────


def test_task_team_role_from_dict():
    ttr = TaskTeamRole.from_dict(
        {
            "task_id": TASK_ID,
            "team_role_id": ROLE_ID,
            "assigned_at": TS,
        }
    )
    assert ttr.task_id == uuid.UUID(TASK_ID)
    assert ttr.team_role_id == uuid.UUID(ROLE_ID)
    assert isinstance(ttr.assigned_at, datetime)


# ── Project ───────────────────────────────────────────────────────────────────


def test_project_from_dict_requires_project_code():
    p = Project.from_dict(
        {
            "id": WF_ID,
            "name": "Proj",
            "status": "Not Started",
            "created_by": "user1",
            "created_at": TS,
            "updated_at": TS,
            "project_code": "P1",
        }
    )
    assert p.project_code == "P1"
    assert p.archived is False
    assert p.organization_id is None


def test_project_from_dict_with_optionals():
    p = Project.from_dict(
        {
            "id": WF_ID,
            "name": "Proj",
            "status": "Not Started",
            "created_by": "user1",
            "created_at": TS,
            "updated_at": TS,
            "project_code": "p1",
            "archived": True,
            "organization_id": "dddddddd-dddd-dddd-dddd-dddddddddddd",
        }
    )
    assert p.archived is True
    assert isinstance(p.organization_id, uuid.UUID)


# ── Connection ────────────────────────────────────────────────────────────────


def _connection(**kw: object) -> dict:
    d: dict = {
        "id": CONN_ID,
        "name": "Conn",
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


def test_connection_from_dict_minimal():
    c = Connection.from_dict(_connection())
    assert c.id == uuid.UUID(CONN_ID)
    assert c.connection_type == "bearer_token"
    assert c.has_secret is False
    assert c.description is None
    assert c.organization_id is None


def test_connection_from_dict_with_secret_set():
    c = Connection.from_dict(_connection(has_secret=True, description="prod key"))
    assert c.has_secret is True
    assert c.description == "prod key"


def test_connection_test_result_from_dict():
    r = ConnectionTestResult.from_dict({"success": True, "message": "ok"})
    assert r.success is True
    assert r.message == "ok"


def test_resolved_connection_from_dict():
    rc = ResolvedConnection.from_dict(
        {"connection_type": "smtp", "config": {"host": "smtp.example.com"}, "secret": "s3cr3t"}
    )
    assert rc.connection_type == "smtp"
    assert rc.secret == "s3cr3t"


# ── WorkItem ──────────────────────────────────────────────────────────────────


def _work_item(**kw: object) -> dict:
    d: dict = {
        "id": WORK_ITEM_ID,
        "name": "WI",
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


def test_work_item_from_dict_minimal():
    w = WorkItem.from_dict(_work_item())
    assert w.id == uuid.UUID(WORK_ITEM_ID)
    assert w.task_type == "standard"
    assert w.port_namespace is None
    assert w.team_id is None


def test_work_item_from_dict_with_optionals():
    w = WorkItem.from_dict(
        _work_item(
            description="desc",
            effort=5,
            decision_input_port="route",
            assigned_to="user-uuid",
            team_id=TEAM_ID,
            port_namespace="review",
        )
    )
    assert w.description == "desc"
    assert w.effort == 5
    assert w.decision_input_port == "route"
    assert isinstance(w.team_id, uuid.UUID)
    assert w.port_namespace == "review"


def test_work_item_port_spec_from_dict():
    s = WorkItemPortSpec.from_dict(
        {
            "id": PORT_ID,
            "work_item_id": WORK_ITEM_ID,
            "direction": "input",
            "name": "token",
            "value_type": "secret",
            "required": True,
            "sort_order": 0,
            "created_at": TS,
            "updated_at": TS,
        }
    )
    assert s.value_type == "secret"
    assert s.required is True


def test_work_item_script_from_dict():
    s = WorkItemScript.from_dict(
        {
            "id": SCRIPT_ID,
            "work_item_id": WORK_ITEM_ID,
            "script_type": "mcp_tool",
            "timeout_secs": 30,
            "retry_limit": 3,
            "created_at": TS,
            "updated_at": TS,
            "connection_id": CONN_ID,
        }
    )
    assert s.script_type == "mcp_tool"
    assert isinstance(s.connection_id, uuid.UUID)


def test_work_item_check_and_check_script_from_dict():
    c = WorkItemCheck.from_dict(
        {
            "id": CHECK_ID,
            "work_item_id": WORK_ITEM_ID,
            "name": "Review",
            "check_type": "manual",
            "required": True,
            "sort_order": 0,
            "created_at": TS,
            "updated_at": TS,
        }
    )
    assert c.check_type == "manual"
    cs = WorkItemCheckScript.from_dict(
        {
            "id": SCRIPT_ID,
            "check_id": CHECK_ID,
            "script_type": "shell",
            "timeout_secs": 30,
            "retry_limit": 0,
            "locked_on_clone": True,
            "created_at": TS,
            "updated_at": TS,
        }
    )
    assert cs.locked_on_clone is True


def test_work_item_team_role_from_dict():
    r = WorkItemTeamRole.from_dict(
        {
            "work_item_id": WORK_ITEM_ID,
            "team_role_id": ROLE_ID,
            "assigned_at": TS,
        }
    )
    assert r.work_item_id == uuid.UUID(WORK_ITEM_ID)


def test_work_item_branch_from_dict():
    b = WorkItemBranch.from_dict(
        {
            "id": PORT_ID,
            "work_item_id": WORK_ITEM_ID,
            "label": "approve",
            "task_name": "Approved",
            "sort_order": 0,
            "created_at": TS,
            "updated_at": TS,
        }
    )
    assert b.label == "approve"


def test_instantiate_work_item_response_from_dict_no_branches():
    r = InstantiateWorkItemResponse.from_dict({"primary_task": _task(), "branch_tasks": []})
    assert isinstance(r.primary_task, Task)
    assert r.branch_tasks == []


def test_instantiate_work_item_response_from_dict_with_branches():
    r = InstantiateWorkItemResponse.from_dict(
        {
            "primary_task": _task(),
            "branch_tasks": [{"label": "approve", "task": _task()}],
        }
    )
    assert len(r.branch_tasks) == 1
    assert isinstance(r.branch_tasks[0], BranchTaskResult)
    assert r.branch_tasks[0].label == "approve"


# ── CheckpointCheck ───────────────────────────────────────────────────────────


def test_checkpoint_check_from_dict_minimal():
    c = CheckpointCheck.from_dict(
        {
            "id": CHECK_ID,
            "task_id": TASK_ID,
            "name": "QA sign-off",
            "check_type": "manual",
            "required": True,
            "sort_order": 0,
            "status": "pending",
            "created_at": TS,
            "updated_at": TS,
        }
    )
    assert c.status == "pending"
    assert c.verified_by is None


def test_checkpoint_check_from_dict_verified():
    c = CheckpointCheck.from_dict(
        {
            "id": CHECK_ID,
            "task_id": TASK_ID,
            "name": "QA sign-off",
            "check_type": "manual",
            "required": True,
            "sort_order": 0,
            "status": "passed",
            "created_at": TS,
            "updated_at": TS,
            "verified_by": "user1",
            "verified_at": TS,
            "note": "looks good",
        }
    )
    assert c.status == "passed"
    assert c.verified_by == "user1"
    assert c.note == "looks good"


def test_checkpoint_check_script_from_dict():
    s = CheckpointCheckScript.from_dict(
        {
            "id": SCRIPT_ID,
            "check_id": CHECK_ID,
            "script_type": "webhook",
            "timeout_secs": 30,
            "retry_limit": 3,
            "locked_on_clone": False,
            "created_at": TS,
            "updated_at": TS,
            "endpoint": "https://hook.example.com",
        }
    )
    assert s.endpoint == "https://hook.example.com"


def test_checkpoint_check_run_from_dict():
    r = CheckpointCheckRun.from_dict(
        {
            "id": RUN_ID,
            "check_id": CHECK_ID,
            "created_at": TS,
            "outcome": "Success",
            "output_json": {"passed": True},
        }
    )
    assert r.outcome == "Success"
    assert r.output_json == {"passed": True}


def test_passthrough_checkpoints_from_dict():
    p = PassthroughCheckpoints.from_dict({"task_ids": [TASK_ID, WF_ID]})
    assert p.task_ids == [uuid.UUID(TASK_ID), uuid.UUID(WF_ID)]


def test_passthrough_checkpoints_from_dict_empty():
    p = PassthroughCheckpoints.from_dict({})
    assert p.task_ids == []


# ── ScheduledScript ───────────────────────────────────────────────────────────


def _scheduled_script(**kw: object) -> dict:
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


def test_scheduled_script_from_dict_minimal():
    s = ScheduledScript.from_dict(_scheduled_script())
    assert s.is_active is True
    assert s.last_run_status is None
    assert s.connection_id is None


def test_scheduled_script_from_dict_with_email_type():
    s = ScheduledScript.from_dict(
        _scheduled_script(
            script_type="email",
            connection_id=CONN_ID,
            last_run_status="Success",
            last_run_at=TS,
        )
    )
    assert s.script_type == "email"
    assert isinstance(s.connection_id, uuid.UUID)
    assert s.last_run_status == "Success"


def test_scheduled_script_run_from_dict():
    r = ScheduledScriptRun.from_dict(
        {
            "id": RUN_ID,
            "schedule_id": SCHEDULE_ID,
            "triggered_by": "schedule",
            "created_at": TS,
            "status": "Success",
        }
    )
    assert r.triggered_by == "schedule"
    assert r.status == "Success"


def test_scheduled_script_dispatch_from_dict_without_connection():
    d = ScheduledScriptDispatch.from_dict(
        {
            "id": SCHEDULE_ID,
            "script_type": "webhook",
            "timeout_secs": 30,
            "state": {},
        }
    )
    assert d.connection is None


def test_scheduled_script_dispatch_from_dict_with_connection():
    d = ScheduledScriptDispatch.from_dict(
        {
            "id": SCHEDULE_ID,
            "script_type": "email",
            "timeout_secs": 30,
            "state": {},
            "connection": {"connection_type": "smtp", "config": {}, "secret": "s3cr3t"},
        }
    )
    assert d.connection is not None
    assert d.connection.secret == "s3cr3t"


# ── AI chat sessions ──────────────────────────────────────────────────────────


def test_chat_session_from_dict():
    s = ChatSession.from_dict(
        {
            "id": SESSION_ID,
            "username": "alice",
            "title": "New chat",
            "created_at": TS,
            "updated_at": TS,
        }
    )
    assert s.username == "alice"
    assert s.title == "New chat"


def test_chat_message_from_dict():
    m = ChatMessage.from_dict(
        {
            "id": RUN_ID,
            "session_id": SESSION_ID,
            "role": "user",
            "content": "hello",
            "created_at": TS,
        }
    )
    assert m.role == "user"
    assert m.content == "hello"


# ── ExecutionProfile ──────────────────────────────────────────────────────────


def test_execution_profile_from_dict():
    ep = ExecutionProfile.from_dict(
        {
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
    )
    assert ep.id == uuid.UUID(PROFILE_ID)
    assert ep.image == "python:3.12-slim"
    assert ep.description is None
    assert ep.image_pull_policy == "IfNotPresent"
    assert ep.enable_buildkit_sidecar is False
    assert ep.runner_pool == "default"


def test_execution_profile_with_buildkit_and_runner_pool():
    ep = ExecutionProfile.from_dict(
        {
            "id": PROFILE_ID,
            "name": "P",
            "image": "img",
            "cpu_request": "100m",
            "cpu_limit": "1",
            "memory_request": "128Mi",
            "memory_limit": "512Mi",
            "created_by": "u",
            "created_at": TS,
            "updated_at": TS,
            "image_pull_policy": "Always",
            "enable_buildkit_sidecar": True,
            "runner_pool": "lagan-ci",
        }
    )
    assert ep.image_pull_policy == "Always"
    assert ep.enable_buildkit_sidecar is True
    assert ep.runner_pool == "lagan-ci"


def test_execution_profile_with_description():
    ep = ExecutionProfile.from_dict(
        {
            "id": PROFILE_ID,
            "name": "P",
            "image": "img",
            "cpu_request": "100m",
            "cpu_limit": "1",
            "memory_request": "128Mi",
            "memory_limit": "512Mi",
            "created_by": "u",
            "created_at": TS,
            "updated_at": TS,
            "description": "desc",
        }
    )
    assert ep.description == "desc"


# ── LoopBlock ─────────────────────────────────────────────────────────────────


def _lblock(**kw: object) -> dict:
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


def test_loop_block_from_dict():
    lb = LoopBlock.from_dict(_lblock())
    assert lb.id == uuid.UUID(LOOP_ID)
    assert lb.loop_type == "count"
    assert lb.loop_config == {"count": 5}
    assert lb.inner_workflow_id == uuid.UUID(INNER_WF_ID)


# ── CreateLoopBlockResponse ───────────────────────────────────────────────────


def test_create_loop_block_response_from_dict():
    d = {
        "task": _task(task_type="loop_block"),
        "loop_block": _lblock(),
    }
    r = CreateLoopBlockResponse.from_dict(d)
    assert isinstance(r.task, Task)
    assert r.task.task_type == "loop_block"
    assert isinstance(r.loop_block, LoopBlock)
