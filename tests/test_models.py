"""Tests for pyawe dataclass models and helper functions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime

import pytest

from pyawe.models import (
    CreateLoopBlockResponse,
    DataBinding,
    ExecutionProfile,
    Job,
    JobWithWorkflows,
    LoginInfo,
    LoopBlock,
    LoopType,
    Note,
    NoteFolder,
    PortDirection,
    PortValueType,
    ScriptType,
    ScheduleStatus,
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
    _dt,
    _uuid,
)

WF_ID = "11111111-1111-1111-1111-111111111111"
TASK_ID = "22222222-2222-2222-2222-222222222222"
JOB_ID = "33333333-3333-3333-3333-333333333333"
NOTE_ID = "44444444-4444-4444-4444-444444444444"
FOLDER_ID = "55555555-5555-5555-5555-555555555555"
PROFILE_ID = "66666666-6666-6666-6666-666666666666"
LINK_FROM = "77777777-7777-7777-7777-777777777777"
LINK_TO = "88888888-8888-8888-8888-888888888888"
PORT_ID = "99999999-9999-9999-9999-999999999999"
SCRIPT_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
RUN_ID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
ROLE_ID = "cccccccc-cccc-cccc-cccc-cccccccccccc"
LOOP_ID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
INNER_WF_ID = "ffffffff-ffff-ffff-ffff-ffffffffffff"
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


def test_script_type_values():
    assert ScriptType.WEBHOOK == "webhook"
    assert ScriptType.SHELL == "shell"
    assert ScriptType.PYTHON == "python"
    assert ScriptType.MCP_TOOL == "mcp_tool"


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
        "id": WF_ID, "name": "WF", "is_template": False,
        "created_at": TS, "updated_at": TS,
        "status": "Not Started", "schedule_status": "N/A", "is_shared": False,
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
    wf = Workflow.from_dict(_wf(
        description="desc",
        job_id=JOB_ID,
        team_id="dddddddd-dddd-dddd-dddd-dddddddddddd",
        created_by="user1",
        parent_loop_block_id=LOOP_ID,
    ))
    assert wf.description == "desc"
    assert isinstance(wf.job_id, uuid.UUID)
    assert isinstance(wf.team_id, uuid.UUID)
    assert wf.created_by == "user1"
    assert wf.parent_loop_block_id == uuid.UUID(LOOP_ID)


def test_workflow_timestamps_are_aware():
    wf = Workflow.from_dict(_wf())
    assert wf.created_at.tzinfo is not None
    assert wf.updated_at.tzinfo is not None


# ── Task ──────────────────────────────────────────────────────────────────────


def _task(**kw: object) -> dict:
    d: dict = {
        "id": TASK_ID, "name": "T", "is_template": False,
        "created_at": TS, "updated_at": TS,
        "status": "Not Started", "schedule_status": "N/A",
        "workflow_id": WF_ID, "is_start": False, "is_end": False,
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


def test_task_from_dict_with_all_optionals():
    t = Task.from_dict(_task(
        description="desc",
        assigned_to="user-uuid",
        start_time=TS,
        end_time=TS,
        decision_outcome="approve",
        rework_task_id=WF_ID,
        loop_block_id=LOOP_ID,
        input_values={"x": 1},
        output_values={"y": 2},
    ))
    assert t.description == "desc"
    assert t.assigned_to == "user-uuid"
    assert t.start_time is not None
    assert t.end_time is not None
    assert t.decision_outcome == "approve"
    assert isinstance(t.rework_task_id, uuid.UUID)
    assert isinstance(t.loop_block_id, uuid.UUID)
    assert t.input_values == {"x": 1}


# ── TaskLink ──────────────────────────────────────────────────────────────────


def test_task_link_from_dict_minimal():
    link = TaskLink.from_dict({"from_task_id": LINK_FROM, "to_task_id": LINK_TO})
    assert link.from_task_id == uuid.UUID(LINK_FROM)
    assert link.to_task_id == uuid.UUID(LINK_TO)
    assert link.branch_label is None
    assert link.data_bindings is None


def test_task_link_with_branch_label():
    link = TaskLink.from_dict({
        "from_task_id": LINK_FROM,
        "to_task_id": LINK_TO,
        "branch_label": "approved",
    })
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
        "id": JOB_ID, "name": "J",
        "status": "Not Started", "schedule_status": "N/A",
        "created_at": TS, "updated_at": TS, "archived": False,
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
        "id": PORT_ID, "task_id": TASK_ID,
        "direction": "input", "name": "data_in",
        "value_type": "string", "required": True,
        "sort_order": 0, "created_at": TS, "updated_at": TS,
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


# ── TaskScript ────────────────────────────────────────────────────────────────


def _script(**kw: object) -> dict:
    d: dict = {
        "id": SCRIPT_ID, "task_id": TASK_ID,
        "script_type": "webhook",
        "timeout_secs": 30, "retry_limit": 3,
        "created_at": TS, "updated_at": TS,
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
    ts = TaskScript.from_dict(_script(
        script_type="python",
        script_body="print('hi')",
        execution_profile_id=PROFILE_ID,
    ))
    assert ts.script_type == "python"
    assert ts.script_body == "print('hi')"
    assert isinstance(ts.execution_profile_id, uuid.UUID)


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
    r = TaskRun.from_dict(_run(
        outcome="Failure",
        started_at=TS,
        completed_at=TS,
        runner_id="runner-1",
        error_message="timeout",
        input_json={"a": 1},
        output_json={"b": 2},
    ))
    assert r.outcome == "Failure"
    assert r.error_message == "timeout"
    assert r.runner_id == "runner-1"
    assert r.started_at is not None
    assert r.input_json == {"a": 1}


# ── TaskTeamRole ──────────────────────────────────────────────────────────────


def test_task_team_role_from_dict():
    ttr = TaskTeamRole.from_dict({
        "task_id": TASK_ID, "team_role_id": ROLE_ID, "assigned_at": TS,
    })
    assert ttr.task_id == uuid.UUID(TASK_ID)
    assert ttr.team_role_id == uuid.UUID(ROLE_ID)
    assert isinstance(ttr.assigned_at, datetime)


# ── Note ──────────────────────────────────────────────────────────────────────


def _note(**kw: object) -> dict:
    d: dict = {
        "id": NOTE_ID, "entity_type": "task", "entity_id": TASK_ID,
        "title": "Note", "is_shared": False,
        "created_by": "user1", "created_at": TS, "updated_at": TS,
    }
    d.update(kw)
    return d


def test_note_from_dict_minimal():
    n = Note.from_dict(_note())
    assert n.id == uuid.UUID(NOTE_ID)
    assert n.entity_type == "task"
    assert n.body is None
    assert n.parent_id is None
    assert n.folder_id is None


def test_note_from_dict_with_optionals():
    n = Note.from_dict(_note(body="body text", parent_id=NOTE_ID, folder_id=FOLDER_ID))
    assert n.body == "body text"
    assert n.parent_id == uuid.UUID(NOTE_ID)
    assert n.folder_id == uuid.UUID(FOLDER_ID)


# ── NoteFolder ────────────────────────────────────────────────────────────────

FOLDER_ID = "55555555-5555-5555-5555-555555555555"


def test_note_folder_from_dict():
    nf = NoteFolder.from_dict({
        "id": FOLDER_ID, "name": "My Folder",
        "created_by": "user1", "created_at": TS,
    })
    assert nf.id == uuid.UUID(FOLDER_ID)
    assert nf.name == "My Folder"
    assert nf.created_by == "user1"


# ── ExecutionProfile ──────────────────────────────────────────────────────────


def test_execution_profile_from_dict():
    ep = ExecutionProfile.from_dict({
        "id": PROFILE_ID, "name": "Python 3.12",
        "image": "python:3.12-slim",
        "cpu_request": "100m", "cpu_limit": "1",
        "memory_request": "128Mi", "memory_limit": "512Mi",
        "created_by": "user1", "created_at": TS, "updated_at": TS,
    })
    assert ep.id == uuid.UUID(PROFILE_ID)
    assert ep.image == "python:3.12-slim"
    assert ep.description is None


def test_execution_profile_with_description():
    ep = ExecutionProfile.from_dict({
        "id": PROFILE_ID, "name": "P", "image": "img",
        "cpu_request": "100m", "cpu_limit": "1",
        "memory_request": "128Mi", "memory_limit": "512Mi",
        "created_by": "u", "created_at": TS, "updated_at": TS,
        "description": "desc",
    })
    assert ep.description == "desc"


# ── LoopBlock ─────────────────────────────────────────────────────────────────


def _lblock(**kw: object) -> dict:
    d: dict = {
        "id": LOOP_ID, "task_id": TASK_ID,
        "outer_workflow_id": WF_ID, "inner_workflow_id": INNER_WF_ID,
        "loop_type": "count", "loop_config": {"count": 5},
        "created_at": TS, "updated_at": TS,
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
