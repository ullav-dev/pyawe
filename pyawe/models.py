"""Dataclass models mirroring the AWE server's API schemas."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# ── helpers ──────────────────────────────────────────────────────────────────


def _dt(s: str | None) -> datetime | None:
    if s is None:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _uuid(s: str | None) -> uuid.UUID | None:
    return uuid.UUID(s) if s is not None else None


# ── enumerations ─────────────────────────────────────────────────────────────


class Status(str, Enum):
    """Lifecycle status shared by workflows, tasks, and jobs.

    ``CANCELLED``, ``REWORKED``, and ``FAILED`` are task-only and
    system-managed: ``CANCELLED`` is set automatically by the propagator when
    a task is on a rejected decision branch; ``REWORKED`` is set only by the
    manual rework trigger (``POST /tasks/{id}/rework``); ``FAILED`` is set
    only when a checkpoint's required check is marked failed. None of these
    should be set via ``update_task``.
    """

    NOT_STARTED = "Not Started"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    COMPLETE = "Complete"
    CANCELLED = "Cancelled"
    REWORKED = "Reworked"
    FAILED = "Failed"


class ScheduleStatus(str, Enum):
    """Schedule health indicator shared by workflows, tasks, and jobs."""

    NA = "N/A"
    ON_TIME = "On Time"
    AT_RISK = "At Risk"
    LATE = "Late"


class TaskType(str, Enum):
    """Task execution model."""

    STANDARD = "standard"
    DECISION = "decision"
    AUTOMATED = "automated"
    LOOP_BLOCK = "loop_block"
    CHECKPOINT = "checkpoint"


class PortDirection(str, Enum):
    """Direction of a task port."""

    INPUT = "input"
    OUTPUT = "output"


class PortValueType(str, Enum):
    """Data type carried by a task or work item port.

    ``SECRET`` is valid only on work item port specs: it declares the slot,
    but the value itself is set per task instance via ``TaskSecretsClient``
    after instantiation.
    """

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    FILE = "file"
    DAM_ASSET = "dam_asset"
    SECRET = "secret"


class ScriptType(str, Enum):
    """Execution mechanism for an automated task."""

    WEBHOOK = "webhook"
    SHELL = "shell"
    PYTHON = "python"
    MCP_TOOL = "mcp_tool"
    EMAIL = "email"


class LoopType(str, Enum):
    """Iteration strategy for a loop block."""

    COUNT = "count"
    WHILE = "while"
    FOR_EACH = "for_each"


# ── auth models ───────────────────────────────────────────────────────────────


@dataclass
class LoginInfo:
    """Session information returned by a successful :meth:`AweClient.login` call."""

    token: str
    user_id: str
    email: str
    username: str
    roles: list[str]
    permissions: list[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LoginInfo:
        user = d["user"]
        return cls(
            token=d["token"],
            user_id=str(user["id"]),
            email=user["email"],
            username=user["username"],
            roles=d.get("roles", []),
            permissions=d.get("permissions", []),
        )


# ── workflow models ───────────────────────────────────────────────────────────


@dataclass
class Workflow:
    """A workflow definition or instance."""

    id: uuid.UUID
    name: str
    is_template: bool
    created_at: datetime
    updated_at: datetime
    status: Status
    schedule_status: ScheduleStatus
    is_shared: bool
    created_by: str | None = None
    description: str | None = None
    job_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    """Denormalized from ``team_id``; read-only."""
    parent_loop_block_id: uuid.UUID | None = None
    sort_order: int | None = None
    """Display order within the parent job (backlog or sprint)."""
    story_points: int | None = None
    """Story point estimate for this story-workflow."""
    # ── Cunav ticket extensions ─────────────────────────────────────────────
    ticket_type: str | None = None
    priority: str | None = None
    reporter_id: uuid.UUID | None = None
    resolved_at: datetime | None = None
    external_reporter_first_name: str | None = None
    """Set when the reporter has no UUM user row. Cleared by an empty string,
    NOT ``null`` — see :meth:`WorkflowsClient.update`."""
    external_reporter_last_name: str | None = None
    external_reporter_email: str | None = None
    # ── Togra cross-reference ───────────────────────────────────────────────
    togra_workflow_id: uuid.UUID | None = None
    togra_project_id: uuid.UUID | None = None
    # ── Human-readable references ───────────────────────────────────────────
    ticket_number: int | None = None
    """Human-readable, globally-sequenced cunav ticket number. Read-only."""
    workflow_number: int | None = None
    """Per-project sequence number (e.g. the ``4`` in ``P1-W0004``). Read-only."""
    project_code: str | None = None
    """The owning project's code, if the workflow's job is linked to one. Read-only."""
    # ── AI triage ────────────────────────────────────────────────────────────
    ai_processed_at: datetime | None = None
    ai_confidence: float | None = None
    ai_should_route: bool | None = None
    ai_outcome_feedback: str | None = None
    """``"helpful"`` or ``"unhelpful"``."""
    ai_outcome_feedback_by: uuid.UUID | None = None
    ai_outcome_feedback_at: datetime | None = None
    ai_outcome_feedback_reason: str | None = None
    ai_outcome_feedback_note_id: uuid.UUID | None = None
    # ── Duplicate ticket linking ────────────────────────────────────────────
    duplicate_of_workflow_id: uuid.UUID | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Workflow:
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            is_template=d["is_template"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            status=Status(d["status"]),
            schedule_status=ScheduleStatus(d["schedule_status"]),
            is_shared=d["is_shared"],
            created_by=d.get("created_by"),
            description=d.get("description"),
            job_id=_uuid(d.get("job_id")),
            team_id=_uuid(d.get("team_id")),
            organization_id=_uuid(d.get("organization_id")),
            parent_loop_block_id=_uuid(d.get("parent_loop_block_id")),
            sort_order=d.get("sort_order"),
            story_points=d.get("story_points"),
            ticket_type=d.get("ticket_type"),
            priority=d.get("priority"),
            reporter_id=_uuid(d.get("reporter_id")),
            resolved_at=_dt(d.get("resolved_at")),
            external_reporter_first_name=d.get("external_reporter_first_name"),
            external_reporter_last_name=d.get("external_reporter_last_name"),
            external_reporter_email=d.get("external_reporter_email"),
            togra_workflow_id=_uuid(d.get("togra_workflow_id")),
            togra_project_id=_uuid(d.get("togra_project_id")),
            ticket_number=d.get("ticket_number"),
            workflow_number=d.get("workflow_number"),
            project_code=d.get("project_code"),
            ai_processed_at=_dt(d.get("ai_processed_at")),
            ai_confidence=d.get("ai_confidence"),
            ai_should_route=d.get("ai_should_route"),
            ai_outcome_feedback=d.get("ai_outcome_feedback"),
            ai_outcome_feedback_by=_uuid(d.get("ai_outcome_feedback_by")),
            ai_outcome_feedback_at=_dt(d.get("ai_outcome_feedback_at")),
            ai_outcome_feedback_reason=d.get("ai_outcome_feedback_reason"),
            ai_outcome_feedback_note_id=_uuid(d.get("ai_outcome_feedback_note_id")),
            duplicate_of_workflow_id=_uuid(d.get("duplicate_of_workflow_id")),
        )


@dataclass
class TaskLink:
    """A directed edge between two tasks."""

    from_task_id: uuid.UUID
    to_task_id: uuid.UUID
    branch_label: str | None = None
    """Set only when the source task is a decision task."""
    data_bindings: Any | None = None
    """List of ``{from: output_name, to: input_name}`` mappings propagated on completion."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskLink:
        return cls(
            from_task_id=uuid.UUID(d["from_task_id"]),
            to_task_id=uuid.UUID(d["to_task_id"]),
            branch_label=d.get("branch_label"),
            data_bindings=d.get("data_bindings"),
        )


@dataclass
class Task:
    """A task within a workflow."""

    id: uuid.UUID
    name: str
    is_template: bool
    created_at: datetime
    updated_at: datetime
    status: Status
    schedule_status: ScheduleStatus
    workflow_id: uuid.UUID
    is_start: bool
    is_end: bool
    task_type: str
    """One of ``"standard"``, ``"decision"``, ``"automated"``, ``"loop_block"``."""
    created_by: str | None = None
    description: str | None = None
    rework_task_id: uuid.UUID | None = None
    loop_block_id: uuid.UUID | None = None
    """Set when ``task_type == "loop_block"``."""
    assigned_to: str | None = None
    """User UUID string; no foreign-key constraint (users live in a separate service)."""
    start_time: datetime | None = None
    end_time: datetime | None = None
    decision_outcome: str | None = None
    decision_input_port: str | None = None
    """Input port name that drives auto-decide for decision tasks."""
    input_values: Any | None = None
    output_values: Any | None = None
    is_locked: bool = False
    """When ``True``, structural edits are blocked for non-privileged users."""
    canvas_x: float | None = None
    canvas_y: float | None = None
    effort: int | None = None
    """Unitless effort estimate (e.g. story points). ``None`` means not yet estimated."""
    priority: str = "none"
    """``"none"`` (default), ``"low"``, ``"medium"``, ``"high"``, or ``"critical"``."""
    due_time: datetime | None = None
    branch_name: str | None = None
    """Git branch this task is working against."""
    task_number: int | None = None
    """Sequence number within the owning project's task numbering. Read-only."""
    port_namespace: str | None = None
    """User-defined prefix (``^[a-z][a-z0-9_]*$``) used instead of ``t{task_number}``
    when a checkpoint mirrors this task's output ports."""
    reworked_from_task_id: uuid.UUID | None = None
    """Set only on a task spawned by the manual rework trigger; read-only provenance."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Task:
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            is_template=d["is_template"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            status=Status(d["status"]),
            schedule_status=ScheduleStatus(d["schedule_status"]),
            workflow_id=uuid.UUID(d["workflow_id"]),
            is_start=d["is_start"],
            is_end=d["is_end"],
            task_type=d["task_type"],
            created_by=d.get("created_by"),
            description=d.get("description"),
            rework_task_id=_uuid(d.get("rework_task_id")),
            loop_block_id=_uuid(d.get("loop_block_id")),
            assigned_to=d.get("assigned_to"),
            start_time=_dt(d.get("start_time")),
            end_time=_dt(d.get("end_time")),
            decision_outcome=d.get("decision_outcome"),
            decision_input_port=d.get("decision_input_port"),
            input_values=d.get("input_values"),
            output_values=d.get("output_values"),
            is_locked=d.get("is_locked", False),
            canvas_x=d.get("canvas_x"),
            canvas_y=d.get("canvas_y"),
            effort=d.get("effort"),
            priority=d.get("priority", "none"),
            due_time=_dt(d.get("due_time")),
            branch_name=d.get("branch_name"),
            task_number=d.get("task_number"),
            port_namespace=d.get("port_namespace"),
            reworked_from_task_id=_uuid(d.get("reworked_from_task_id")),
        )


@dataclass
class TaskWithContext:
    """A task enriched with its workflow and job names, returned by ``list_mine``."""

    task: Task
    workflow_name: str
    job_id: uuid.UUID | None = None
    job_name: str | None = None
    project_code: str | None = None
    """The owning project's code, if the job is linked to one. Read-only."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskWithContext:
        return cls(
            task=Task.from_dict(d),
            workflow_name=d["workflow_name"],
            job_id=_uuid(d.get("job_id")),
            job_name=d.get("job_name"),
            project_code=d.get("project_code"),
        )


@dataclass
class WorkflowWithTasks:
    """Workflow with its associated tasks and inter-task links."""

    workflow: Workflow
    tasks: list[Task] = field(default_factory=list)
    links: list[TaskLink] = field(default_factory=list)
    project_code: str | None = None
    """The owning project's code, if the workflow's job is linked to one. Read-only."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkflowWithTasks:
        return cls(
            workflow=Workflow.from_dict(d),
            tasks=[Task.from_dict(t) for t in d.get("tasks", [])],
            links=[TaskLink.from_dict(lk) for lk in d.get("links", [])],
            project_code=d.get("project_code"),
        )


# ── job models ────────────────────────────────────────────────────────────────


@dataclass
class Job:
    """A job that groups related workflow instances."""

    id: uuid.UUID
    name: str
    status: Status
    schedule_status: ScheduleStatus
    created_at: datetime
    updated_at: datetime
    archived: bool
    team_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    """Denormalized from ``team_id``; read-only."""
    project_id: uuid.UUID | None = None
    job_type: str | None = None
    """``"sprint"``, ``"kanban"``, or ``"backlog"``; ``None`` for legacy jobs."""
    start_date: str | None = None
    """ISO 8601 date string; set when ``job_type == "sprint"``."""
    end_date: str | None = None
    """ISO 8601 date string; set when ``job_type == "sprint"``."""
    ai_enabled: bool = False
    """Only meaningful for ``job_type == "kanban"`` queues: whether new tickets
    are dispatched to cunav's AI triage webhook."""
    ai_togra_project_id: uuid.UUID | None = None
    ai_togra_job_id: uuid.UUID | None = None
    ai_togra_template_id: uuid.UUID | None = None
    ai_route_confidence_threshold: float | None = None
    ai_rules: Any | None = None
    """Per-outcome-type enable/threshold config, e.g.
    ``[{"type": "flag_duplicate", "enabled": true, "confidence_threshold": 0.6}]``."""
    email_connection_id: uuid.UUID | None = None
    inbound_email_connection_id: uuid.UUID | None = None
    project_code: str | None = None
    """The linked project's code, if any. Read-only."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Job:
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            status=Status(d["status"]),
            schedule_status=ScheduleStatus(d["schedule_status"]),
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            archived=d["archived"],
            team_id=_uuid(d.get("team_id")),
            organization_id=_uuid(d.get("organization_id")),
            project_id=_uuid(d.get("project_id")),
            job_type=d.get("job_type"),
            start_date=d.get("start_date"),
            end_date=d.get("end_date"),
            ai_enabled=d.get("ai_enabled", False),
            ai_togra_project_id=_uuid(d.get("ai_togra_project_id")),
            ai_togra_job_id=_uuid(d.get("ai_togra_job_id")),
            ai_togra_template_id=_uuid(d.get("ai_togra_template_id")),
            ai_route_confidence_threshold=d.get("ai_route_confidence_threshold"),
            ai_rules=d.get("ai_rules"),
            email_connection_id=_uuid(d.get("email_connection_id")),
            inbound_email_connection_id=_uuid(d.get("inbound_email_connection_id")),
            project_code=d.get("project_code"),
        )


@dataclass
class JobWithWorkflows:
    """Job with its associated workflows."""

    job: Job
    workflows: list[Workflow] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> JobWithWorkflows:
        return cls(
            job=Job.from_dict(d),
            workflows=[Workflow.from_dict(w) for w in d.get("workflows", [])],
        )


# ── task port models ──────────────────────────────────────────────────────────


@dataclass
class TaskPortSpec:
    """Port specification (input or output) defined on a task."""

    id: uuid.UUID
    task_id: uuid.UUID
    direction: str
    """``"input"`` or ``"output"``."""
    name: str
    value_type: str
    """One of ``"string"``, ``"number"``, ``"boolean"``, ``"json"``, ``"file"``, ``"dam_asset"``."""
    required: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    default_value: Any | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskPortSpec:
        return cls(
            id=uuid.UUID(d["id"]),
            task_id=uuid.UUID(d["task_id"]),
            direction=d["direction"],
            name=d["name"],
            value_type=d["value_type"],
            required=d["required"],
            sort_order=d["sort_order"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            description=d.get("description"),
            default_value=d.get("default_value"),
        )


@dataclass
class TaskPortValues:
    """Port specs paired with their current runtime values."""

    specs: list[TaskPortSpec] = field(default_factory=list)
    values: Any | None = None
    """Dict of ``{name: value}`` or ``None`` when no values have been set."""
    secret_set: list[str] = field(default_factory=list)
    """Names of secret input ports that currently have an encrypted value stored."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskPortValues:
        return cls(
            specs=[TaskPortSpec.from_dict(s) for s in d.get("specs", [])],
            values=d.get("values"),
            secret_set=d.get("secret_set", []),
        )


@dataclass
class DataBinding:
    """A single data binding on a task link edge."""

    from_port: str
    """Name of the output port on the upstream task."""
    to_port: str
    """Name of the input port on the downstream task."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DataBinding:
        return cls(from_port=d["from"], to_port=d["to"])

    def to_dict(self) -> dict[str, str]:
        return {"from": self.from_port, "to": self.to_port}


# ── task script / run models ──────────────────────────────────────────────────


@dataclass
class TaskScript:
    """Automated execution script attached to a task."""

    id: uuid.UUID
    task_id: uuid.UUID
    script_type: str
    """One of ``"webhook"``, ``"shell"``, ``"python"``, ``"mcp_tool"``, ``"email"``."""
    timeout_secs: int
    retry_limit: int
    created_at: datetime
    updated_at: datetime
    endpoint: str | None = None
    script_body: str | None = None
    execution_profile_id: uuid.UUID | None = None
    connection_id: uuid.UUID | None = None
    """Connection profile to resolve auth from at run time. Required
    (must reference an ``smtp`` connection) when ``script_type == "email"``."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskScript:
        return cls(
            id=uuid.UUID(d["id"]),
            task_id=uuid.UUID(d["task_id"]),
            script_type=d["script_type"],
            timeout_secs=d["timeout_secs"],
            retry_limit=d["retry_limit"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            endpoint=d.get("endpoint"),
            script_body=d.get("script_body"),
            execution_profile_id=_uuid(d.get("execution_profile_id")),
            connection_id=_uuid(d.get("connection_id")),
        )


@dataclass
class TaskRun:
    """Record of a single automated task execution attempt."""

    id: uuid.UUID
    task_id: uuid.UUID
    created_at: datetime
    runner_id: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    outcome: str | None = None
    """``"Success"``, ``"Failure"``, or ``"Timeout"``."""
    input_json: Any | None = None
    output_json: Any | None = None
    error_message: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskRun:
        return cls(
            id=uuid.UUID(d["id"]),
            task_id=uuid.UUID(d["task_id"]),
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            runner_id=d.get("runner_id"),
            started_at=_dt(d.get("started_at")),
            completed_at=_dt(d.get("completed_at")),
            outcome=d.get("outcome"),
            input_json=d.get("input_json"),
            output_json=d.get("output_json"),
            error_message=d.get("error_message"),
        )


# ── task team-role model ──────────────────────────────────────────────────────


@dataclass
class TaskTeamRole:
    """Assignment of a team role to a task."""

    task_id: uuid.UUID
    team_role_id: uuid.UUID
    assigned_at: datetime

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskTeamRole:
        return cls(
            task_id=uuid.UUID(d["task_id"]),
            team_role_id=uuid.UUID(d["team_role_id"]),
            assigned_at=_dt(d["assigned_at"]),  # type: ignore[arg-type]
        )


# ── execution profile model ───────────────────────────────────────────────────


@dataclass
class ExecutionProfile:
    """Approved Kubernetes execution environment for automated tasks."""

    id: uuid.UUID
    name: str
    image: str
    """Full OCI image reference, e.g. ``python:3.12-slim``."""
    cpu_request: str
    cpu_limit: str
    memory_request: str
    memory_limit: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    image_pull_policy: str = "IfNotPresent"
    enable_buildkit_sidecar: bool = False
    """Run a rootless ``buildkitd`` as a native Kubernetes sidecar alongside
    this profile's task container."""
    runner_pool: str = "default"
    """Which ``awe-runner`` pool dispatches this profile's tasks."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ExecutionProfile:
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            image=d["image"],
            cpu_request=d["cpu_request"],
            cpu_limit=d["cpu_limit"],
            memory_request=d["memory_request"],
            memory_limit=d["memory_limit"],
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            description=d.get("description"),
            image_pull_policy=d.get("image_pull_policy", "IfNotPresent"),
            enable_buildkit_sidecar=d.get("enable_buildkit_sidecar", False),
            runner_pool=d.get("runner_pool", "default"),
        )


# ── loop block model ──────────────────────────────────────────────────────────


@dataclass
class LoopBlock:
    """A loop block that wraps an inner workflow repeated across iterations."""

    id: uuid.UUID
    task_id: uuid.UUID
    """The task in the outer workflow that represents this loop block."""
    outer_workflow_id: uuid.UUID
    inner_workflow_id: uuid.UUID
    """The workflow executed on each iteration."""
    loop_type: str
    """``"count"``, ``"while"``, or ``"for_each"``."""
    loop_config: Any
    """Type-dependent config: ``{"count": N}``, ``{"condition": "continue"}``, or
    ``{"collection": [...]}``. """
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LoopBlock:
        return cls(
            id=uuid.UUID(d["id"]),
            task_id=uuid.UUID(d["task_id"]),
            outer_workflow_id=uuid.UUID(d["outer_workflow_id"]),
            inner_workflow_id=uuid.UUID(d["inner_workflow_id"]),
            loop_type=d["loop_type"],
            loop_config=d["loop_config"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
        )


@dataclass
class CreateLoopBlockResponse:
    """Response from ``POST /loop-blocks``: the new outer task and its loop block."""

    task: Task
    loop_block: LoopBlock

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CreateLoopBlockResponse:
        return cls(
            task=Task.from_dict(d["task"]),
            loop_block=LoopBlock.from_dict(d["loop_block"]),
        )


# ── project models ────────────────────────────────────────────────────────────


@dataclass
class Project:
    """A project that groups related jobs."""

    id: uuid.UUID
    name: str
    status: Status
    created_by: str
    created_at: datetime
    updated_at: datetime
    project_code: str
    """Short unique code (e.g. ``"P1"``) used as the prefix for this project's
    human-readable workflow/task references (e.g. ``"P1-0001"``, ``"P1-W0001"``)."""
    description: str | None = None
    team_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    """Denormalized from ``team_id``; read-only."""
    project_manager_id: str | None = None
    archived: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Project:
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            status=Status(d["status"]),
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            project_code=d["project_code"],
            description=d.get("description"),
            team_id=_uuid(d.get("team_id")),
            organization_id=_uuid(d.get("organization_id")),
            project_manager_id=d.get("project_manager_id"),
            archived=d.get("archived", False),
        )


@dataclass
class ProjectWithJobs:
    """Project with its associated jobs."""

    project: Project
    jobs: list[Job] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ProjectWithJobs:
        return cls(
            project=Project.from_dict(d),
            jobs=[Job.from_dict(j) for j in d.get("jobs", [])],
        )


@dataclass
class WorkflowAllocation:
    """First-task allocation summary for a workflow within a job."""

    workflow_id: uuid.UUID
    start_task_id: uuid.UUID | None = None
    """The ``is_start`` task, if one exists."""
    assigned_to: str | None = None
    """Direct user assignee on the start task."""
    team_role_ids: list[uuid.UUID] = field(default_factory=list)
    """Team role IDs assigned to the start task."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkflowAllocation:
        return cls(
            workflow_id=uuid.UUID(d["workflow_id"]),
            start_task_id=_uuid(d.get("start_task_id")),
            assigned_to=d.get("assigned_to"),
            team_role_ids=[uuid.UUID(r) for r in d.get("team_role_ids", [])],
        )


# ── task state history models ─────────────────────────────────────────────────


@dataclass
class TaskStateHistoryEntry:
    """A single recorded status transition for a job-linked task.

    All name fields are snapshotted at transition time so this record is
    self-contained for external reporting.
    """

    id: uuid.UUID
    transitioned_at: datetime
    task_name: str
    workflow_name: str
    job_id: uuid.UUID
    job_name: str
    from_status: str
    to_status: str
    actor_type: str
    """``"user"``, ``"propagator"``, ``"automated"``, or ``"system"``."""
    task_id: uuid.UUID | None = None
    workflow_id: uuid.UUID | None = None
    actor_id: str | None = None
    actor_username: str | None = None
    propagation_depth: int | None = None
    client_app: str | None = None
    client_version: str | None = None
    metadata: Any | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TaskStateHistoryEntry:
        return cls(
            id=uuid.UUID(d["id"]),
            transitioned_at=_dt(d["transitioned_at"]),  # type: ignore[arg-type]
            task_name=d["task_name"],
            workflow_name=d["workflow_name"],
            job_id=uuid.UUID(d["job_id"]),
            job_name=d["job_name"],
            from_status=d["from_status"],
            to_status=d["to_status"],
            actor_type=d["actor_type"],
            task_id=_uuid(d.get("task_id")),
            workflow_id=_uuid(d.get("workflow_id")),
            actor_id=d.get("actor_id"),
            actor_username=d.get("actor_username"),
            propagation_depth=d.get("propagation_depth"),
            client_app=d.get("client_app"),
            client_version=d.get("client_version"),
            metadata=d.get("metadata"),
        )


# ── connection models ────────────────────────────────────────────────────────


@dataclass
class Connection:
    """A reusable credential ("connection profile"), configured once and
    referenced by id from a ``webhook``/``mcp_tool`` script, a scheduled
    script, or the AI email routing on a job.
    """

    id: uuid.UUID
    name: str
    connection_type: str
    """One of ``"bearer_token"``, ``"oauth2_client_credentials"``,
    ``"api_key_header"``, ``"basic_auth"``, ``"smtp"``, or ``"imap"``."""
    team_id: uuid.UUID
    """Owning team — a connection may only be used by workflows owned by the same team."""
    config: Any
    """Non-secret configuration; shape depends on ``connection_type``."""
    has_secret: bool
    """Whether a secret value has been set via :meth:`ConnectionsClient.patch_secret`."""
    created_by: str
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    organization_id: uuid.UUID | None = None
    """Denormalized from ``team_id``; read-only."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Connection:
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            connection_type=d["connection_type"],
            team_id=uuid.UUID(d["team_id"]),
            config=d.get("config"),
            has_secret=d["has_secret"],
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            description=d.get("description"),
            organization_id=_uuid(d.get("organization_id")),
        )


@dataclass
class ConnectionTestResult:
    """Result of an active connection credential test."""

    success: bool
    message: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ConnectionTestResult:
        return cls(success=d["success"], message=d["message"])


@dataclass
class ResolvedConnection:
    """Fully resolved connection, decrypted (service role only)."""

    connection_type: str
    config: Any
    secret: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ResolvedConnection:
        return cls(
            connection_type=d["connection_type"],
            config=d.get("config"),
            secret=d["secret"],
        )


# ── work item models ─────────────────────────────────────────────────────────


@dataclass
class WorkItem:
    """A standalone, reusable task template not tied to any workflow — placed
    into a workflow as a new task via :meth:`WorkItemsClient.instantiate`.
    """

    id: uuid.UUID
    name: str
    task_type: str
    """``"standard"``, ``"decision"``, or ``"automated"``."""
    is_start: bool
    is_end: bool
    is_locked: bool
    is_shared: bool
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    effort: int | None = None
    decision_input_port: str | None = None
    assigned_to: str | None = None
    team_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    """Denormalized from ``team_id``; read-only."""
    created_by: str | None = None
    port_namespace: str | None = None
    """Checkpoint port namespace seeded onto every task instantiated from this work item."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkItem:
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            task_type=d["task_type"],
            is_start=d["is_start"],
            is_end=d["is_end"],
            is_locked=d["is_locked"],
            is_shared=d["is_shared"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            description=d.get("description"),
            effort=d.get("effort"),
            decision_input_port=d.get("decision_input_port"),
            assigned_to=d.get("assigned_to"),
            team_id=_uuid(d.get("team_id")),
            organization_id=_uuid(d.get("organization_id")),
            created_by=d.get("created_by"),
            port_namespace=d.get("port_namespace"),
        )


@dataclass
class WorkItemPortSpec:
    """Port specification (input or output) defined on a work item."""

    id: uuid.UUID
    work_item_id: uuid.UUID
    direction: str
    """``"input"`` or ``"output"``."""
    name: str
    value_type: str
    """One of ``"string"``, ``"number"``, ``"boolean"``, ``"json"``, ``"file"``,
    ``"dam_asset"``, or ``"secret"``."""
    required: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    default_value: Any | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkItemPortSpec:
        return cls(
            id=uuid.UUID(d["id"]),
            work_item_id=uuid.UUID(d["work_item_id"]),
            direction=d["direction"],
            name=d["name"],
            value_type=d["value_type"],
            required=d["required"],
            sort_order=d["sort_order"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            description=d.get("description"),
            default_value=d.get("default_value"),
        )


@dataclass
class WorkItemScript:
    """Automated execution script attached to a work item."""

    id: uuid.UUID
    work_item_id: uuid.UUID
    script_type: str
    """One of ``"webhook"``, ``"shell"``, ``"python"``, ``"mcp_tool"``."""
    timeout_secs: int
    retry_limit: int
    created_at: datetime
    updated_at: datetime
    endpoint: str | None = None
    script_body: str | None = None
    execution_profile_id: uuid.UUID | None = None
    connection_id: uuid.UUID | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkItemScript:
        return cls(
            id=uuid.UUID(d["id"]),
            work_item_id=uuid.UUID(d["work_item_id"]),
            script_type=d["script_type"],
            timeout_secs=d["timeout_secs"],
            retry_limit=d["retry_limit"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            endpoint=d.get("endpoint"),
            script_body=d.get("script_body"),
            execution_profile_id=_uuid(d.get("execution_profile_id")),
            connection_id=_uuid(d.get("connection_id")),
        )


@dataclass
class WorkItemCheck:
    """Checkpoint check template defined on a work item."""

    id: uuid.UUID
    work_item_id: uuid.UUID
    name: str
    check_type: str
    """``"manual"`` or ``"script"``."""
    required: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    related_port_names: Any | None = None
    assigned_to: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkItemCheck:
        return cls(
            id=uuid.UUID(d["id"]),
            work_item_id=uuid.UUID(d["work_item_id"]),
            name=d["name"],
            check_type=d["check_type"],
            required=d["required"],
            sort_order=d["sort_order"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            description=d.get("description"),
            related_port_names=d.get("related_port_names"),
            assigned_to=d.get("assigned_to"),
        )


@dataclass
class WorkItemCheckScript:
    """Automated execution script attached to a work item check."""

    id: uuid.UUID
    check_id: uuid.UUID
    script_type: str
    """One of ``"webhook"``, ``"shell"``, ``"python"``, ``"mcp_tool"``."""
    timeout_secs: int
    retry_limit: int
    locked_on_clone: bool
    created_at: datetime
    updated_at: datetime
    endpoint: str | None = None
    script_body: str | None = None
    execution_profile_id: uuid.UUID | None = None
    connection_id: uuid.UUID | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkItemCheckScript:
        return cls(
            id=uuid.UUID(d["id"]),
            check_id=uuid.UUID(d["check_id"]),
            script_type=d["script_type"],
            timeout_secs=d["timeout_secs"],
            retry_limit=d["retry_limit"],
            locked_on_clone=d["locked_on_clone"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            endpoint=d.get("endpoint"),
            script_body=d.get("script_body"),
            execution_profile_id=_uuid(d.get("execution_profile_id")),
            connection_id=_uuid(d.get("connection_id")),
        )


@dataclass
class WorkItemTeamRole:
    """Assignment of a team role to a work item."""

    work_item_id: uuid.UUID
    team_role_id: uuid.UUID
    assigned_at: datetime

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkItemTeamRole:
        return cls(
            work_item_id=uuid.UUID(d["work_item_id"]),
            team_role_id=uuid.UUID(d["team_role_id"]),
            assigned_at=_dt(d["assigned_at"]),  # type: ignore[arg-type]
        )


@dataclass
class WorkItemBranch:
    """A named outgoing branch for a decision-type work item."""

    id: uuid.UUID
    work_item_id: uuid.UUID
    label: str
    task_name: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> WorkItemBranch:
        return cls(
            id=uuid.UUID(d["id"]),
            work_item_id=uuid.UUID(d["work_item_id"]),
            label=d["label"],
            task_name=d["task_name"],
            sort_order=d["sort_order"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
        )


@dataclass
class BranchTaskResult:
    """One branch task created by :meth:`WorkItemsClient.instantiate`."""

    label: str
    task: Task

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> BranchTaskResult:
        return cls(label=d["label"], task=Task.from_dict(d["task"]))


@dataclass
class InstantiateWorkItemResponse:
    """Response from ``POST /work-items/{id}/instantiate``."""

    primary_task: Task
    branch_tasks: list[BranchTaskResult] = field(default_factory=list)
    """Non-empty only for decision work items with branches."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> InstantiateWorkItemResponse:
        return cls(
            primary_task=Task.from_dict(d["primary_task"]),
            branch_tasks=[BranchTaskResult.from_dict(b) for b in d.get("branch_tasks", [])],
        )


# ── checkpoint check models ──────────────────────────────────────────────────


@dataclass
class CheckpointCheck:
    """A single check gating a checkpoint task."""

    id: uuid.UUID
    task_id: uuid.UUID
    name: str
    check_type: str
    """``"manual"``, ``"script"``, or ``"passthrough"``."""
    required: bool
    sort_order: int
    status: str
    """``"pending"``, ``"passed"``, or ``"failed"``."""
    created_at: datetime
    updated_at: datetime
    description: str | None = None
    related_port_names: Any | None = None
    """Cosmetic only — names of input ports this check happens to read."""
    assigned_to: str | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
    note: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CheckpointCheck:
        return cls(
            id=uuid.UUID(d["id"]),
            task_id=uuid.UUID(d["task_id"]),
            name=d["name"],
            check_type=d["check_type"],
            required=d["required"],
            sort_order=d["sort_order"],
            status=d["status"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            description=d.get("description"),
            related_port_names=d.get("related_port_names"),
            assigned_to=d.get("assigned_to"),
            verified_by=d.get("verified_by"),
            verified_at=_dt(d.get("verified_at")),
            note=d.get("note"),
        )


@dataclass
class CheckpointCheckScript:
    """Automated execution script attached to a checkpoint check."""

    id: uuid.UUID
    check_id: uuid.UUID
    script_type: str
    """One of ``"webhook"``, ``"shell"``, ``"python"``, ``"mcp_tool"``."""
    timeout_secs: int
    retry_limit: int
    locked_on_clone: bool
    created_at: datetime
    updated_at: datetime
    endpoint: str | None = None
    script_body: str | None = None
    execution_profile_id: uuid.UUID | None = None
    connection_id: uuid.UUID | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CheckpointCheckScript:
        return cls(
            id=uuid.UUID(d["id"]),
            check_id=uuid.UUID(d["check_id"]),
            script_type=d["script_type"],
            timeout_secs=d["timeout_secs"],
            retry_limit=d["retry_limit"],
            locked_on_clone=d["locked_on_clone"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            endpoint=d.get("endpoint"),
            script_body=d.get("script_body"),
            execution_profile_id=_uuid(d.get("execution_profile_id")),
            connection_id=_uuid(d.get("connection_id")),
        )


@dataclass
class CheckpointCheckRun:
    """Record of a single checkpoint check script execution attempt."""

    id: uuid.UUID
    check_id: uuid.UUID
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    outcome: str | None = None
    """``"Success"``, ``"Failure"``, or ``"Timeout"``."""
    output_json: Any | None = None
    """Contains ``{"passed": bool, ...}`` on a ``"Success"`` outcome."""
    error_message: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CheckpointCheckRun:
        return cls(
            id=uuid.UUID(d["id"]),
            check_id=uuid.UUID(d["check_id"]),
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            started_at=_dt(d.get("started_at")),
            completed_at=_dt(d.get("completed_at")),
            outcome=d.get("outcome"),
            output_json=d.get("output_json"),
            error_message=d.get("error_message"),
        )


@dataclass
class PassthroughCheckpoints:
    """Task IDs in a workflow that have a passthrough checkpoint check."""

    task_ids: list[uuid.UUID] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> PassthroughCheckpoints:
        return cls(task_ids=[uuid.UUID(t) for t in d.get("task_ids", [])])


# ── scheduled script models ──────────────────────────────────────────────────


@dataclass
class ScheduledScript:
    """A script that runs on a wall-clock cron schedule, independent of any
    workflow/task instance.
    """

    id: uuid.UUID
    team_id: uuid.UUID
    name: str
    is_active: bool
    cron_expression: str
    """Standard 5-field cron expression, evaluated in UTC."""
    script_type: str
    """``"webhook"``, ``"shell"``, ``"python"``, ``"mcp_tool"``, or ``"email"``."""
    timeout_secs: int
    state: Any
    """Arbitrary JSON the script persists across runs."""
    next_run_at: datetime
    created_by: str
    created_at: datetime
    updated_at: datetime
    organization_id: uuid.UUID | None = None
    """Denormalized from ``team_id``; read-only."""
    description: str | None = None
    endpoint: str | None = None
    script_body: str | None = None
    execution_profile_id: uuid.UUID | None = None
    connection_id: uuid.UUID | None = None
    running_since: datetime | None = None
    last_run_at: datetime | None = None
    last_run_status: str | None = None
    """``"Success"``, ``"Failure"``, or ``"Timeout"``."""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ScheduledScript:
        return cls(
            id=uuid.UUID(d["id"]),
            team_id=uuid.UUID(d["team_id"]),
            name=d["name"],
            is_active=d["is_active"],
            cron_expression=d["cron_expression"],
            script_type=d["script_type"],
            timeout_secs=d["timeout_secs"],
            state=d.get("state"),
            next_run_at=_dt(d["next_run_at"]),  # type: ignore[arg-type]
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            organization_id=_uuid(d.get("organization_id")),
            description=d.get("description"),
            endpoint=d.get("endpoint"),
            script_body=d.get("script_body"),
            execution_profile_id=_uuid(d.get("execution_profile_id")),
            connection_id=_uuid(d.get("connection_id")),
            running_since=_dt(d.get("running_since")),
            last_run_at=_dt(d.get("last_run_at")),
            last_run_status=d.get("last_run_status"),
        )


@dataclass
class ScheduledScriptRun:
    """One run of a scheduled script."""

    id: uuid.UUID
    schedule_id: uuid.UUID
    triggered_by: str
    """``"schedule"`` (fired by cron) or ``"manual"`` (fired via
    :meth:`ScheduledScriptsClient.trigger`)."""
    created_at: datetime
    runner_id: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: str | None = None
    message: str | None = None
    error_message: str | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ScheduledScriptRun:
        return cls(
            id=uuid.UUID(d["id"]),
            schedule_id=uuid.UUID(d["schedule_id"]),
            triggered_by=d["triggered_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            runner_id=d.get("runner_id"),
            started_at=_dt(d.get("started_at")),
            completed_at=_dt(d.get("completed_at")),
            status=d.get("status"),
            message=d.get("message"),
            error_message=d.get("error_message"),
        )


@dataclass
class ScheduledScriptDispatch:
    """Everything ``awe_runner`` needs to execute a scheduled script (service role only)."""

    id: uuid.UUID
    script_type: str
    timeout_secs: int
    state: Any
    endpoint: str | None = None
    script_body: str | None = None
    execution_profile_id: uuid.UUID | None = None
    connection: ResolvedConnection | None = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ScheduledScriptDispatch:
        connection = d.get("connection")
        return cls(
            id=uuid.UUID(d["id"]),
            script_type=d["script_type"],
            timeout_secs=d["timeout_secs"],
            state=d.get("state"),
            endpoint=d.get("endpoint"),
            script_body=d.get("script_body"),
            execution_profile_id=_uuid(d.get("execution_profile_id")),
            connection=ResolvedConnection.from_dict(connection) if connection else None,
        )


# ── AI chat session models ───────────────────────────────────────────────────


@dataclass
class ChatSession:
    """An AI chat session belonging to the authenticated user."""

    id: uuid.UUID
    username: str
    title: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ChatSession:
        return cls(
            id=uuid.UUID(d["id"]),
            username=d["username"],
            title=d["title"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
        )


@dataclass
class ChatMessage:
    """A single message within an AI chat session."""

    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ChatMessage:
        return cls(
            id=uuid.UUID(d["id"]),
            session_id=uuid.UUID(d["session_id"]),
            role=d["role"],
            content=d["content"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
        )
