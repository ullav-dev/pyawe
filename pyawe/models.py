"""Dataclass models mirroring the AWE server's API schemas."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ── helpers ──────────────────────────────────────────────────────────────────


def _dt(s: Optional[str]) -> Optional[datetime]:
    if s is None:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _uuid(s: Optional[str]) -> Optional[uuid.UUID]:
    return uuid.UUID(s) if s is not None else None


# ── enumerations ─────────────────────────────────────────────────────────────


class Status(str, Enum):
    """Lifecycle status shared by workflows, tasks, and jobs.

    ``CANCELLED`` is task-only and set automatically by the propagator when a
    task is on a rejected decision branch; do not set it via ``update_task``.
    """

    NOT_STARTED = "Not Started"
    READY = "Ready"
    IN_PROGRESS = "In Progress"
    ON_HOLD = "On Hold"
    COMPLETE = "Complete"
    CANCELLED = "Cancelled"


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


class PortDirection(str, Enum):
    """Direction of a task port."""

    INPUT = "input"
    OUTPUT = "output"


class PortValueType(str, Enum):
    """Data type carried by a task port."""

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    FILE = "file"
    DAM_ASSET = "dam_asset"


class ScriptType(str, Enum):
    """Execution mechanism for an automated task."""

    WEBHOOK = "webhook"
    SHELL = "shell"
    PYTHON = "python"
    MCP_TOOL = "mcp_tool"


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
    roles: List[str]
    permissions: List[str]

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LoginInfo":
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
    created_by: Optional[str] = None
    description: Optional[str] = None
    job_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    parent_loop_block_id: Optional[uuid.UUID] = None
    sort_order: Optional[int] = None
    """Display order within the parent job (backlog or sprint)."""
    story_points: Optional[int] = None
    """Story point estimate for this story-workflow."""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Workflow":
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
            parent_loop_block_id=_uuid(d.get("parent_loop_block_id")),
            sort_order=d.get("sort_order"),
            story_points=d.get("story_points"),
        )


@dataclass
class TaskLink:
    """A directed edge between two tasks."""

    from_task_id: uuid.UUID
    to_task_id: uuid.UUID
    branch_label: Optional[str] = None
    """Set only when the source task is a decision task."""
    data_bindings: Optional[Any] = None
    """List of ``{from: output_name, to: input_name}`` mappings propagated on completion."""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TaskLink":
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
    created_by: Optional[str] = None
    description: Optional[str] = None
    rework_task_id: Optional[uuid.UUID] = None
    loop_block_id: Optional[uuid.UUID] = None
    """Set when ``task_type == "loop_block"``."""
    assigned_to: Optional[str] = None
    """User UUID string; no foreign-key constraint (users live in a separate service)."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    decision_outcome: Optional[str] = None
    decision_input_port: Optional[str] = None
    """Input port name that drives auto-decide for decision tasks."""
    input_values: Optional[Any] = None
    output_values: Optional[Any] = None
    is_locked: bool = False
    """When ``True``, structural edits are blocked for non-privileged users."""
    canvas_x: Optional[float] = None
    canvas_y: Optional[float] = None
    effort: Optional[int] = None
    """Unitless effort estimate (e.g. story points). ``None`` means not yet estimated."""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Task":
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
        )


@dataclass
class TaskWithContext:
    """A task enriched with its workflow and job names, returned by ``list_mine``."""

    task: Task
    workflow_name: str
    job_id: Optional[uuid.UUID] = None
    job_name: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TaskWithContext":
        return cls(
            task=Task.from_dict(d),
            workflow_name=d["workflow_name"],
            job_id=_uuid(d.get("job_id")),
            job_name=d.get("job_name"),
        )


@dataclass
class WorkflowWithTasks:
    """Workflow with its associated tasks and inter-task links."""

    workflow: Workflow
    tasks: List[Task] = field(default_factory=list)
    links: List[TaskLink] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "WorkflowWithTasks":
        return cls(
            workflow=Workflow.from_dict(d),
            tasks=[Task.from_dict(t) for t in d.get("tasks", [])],
            links=[TaskLink.from_dict(lk) for lk in d.get("links", [])],
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
    team_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    job_type: Optional[str] = None
    """``"sprint"``, ``"kanban"``, or ``"backlog"``; ``None`` for legacy jobs."""
    start_date: Optional[str] = None
    """ISO 8601 date string; set when ``job_type == "sprint"``."""
    end_date: Optional[str] = None
    """ISO 8601 date string; set when ``job_type == "sprint"``."""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Job":
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            status=Status(d["status"]),
            schedule_status=ScheduleStatus(d["schedule_status"]),
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            archived=d["archived"],
            team_id=_uuid(d.get("team_id")),
            project_id=_uuid(d.get("project_id")),
            job_type=d.get("job_type"),
            start_date=d.get("start_date"),
            end_date=d.get("end_date"),
        )


@dataclass
class JobWithWorkflows:
    """Job with its associated workflows."""

    job: Job
    workflows: List[Workflow] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "JobWithWorkflows":
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
    description: Optional[str] = None
    default_value: Optional[Any] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TaskPortSpec":
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

    specs: List[TaskPortSpec] = field(default_factory=list)
    values: Optional[Any] = None
    """Dict of ``{name: value}`` or ``None`` when no values have been set."""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TaskPortValues":
        return cls(
            specs=[TaskPortSpec.from_dict(s) for s in d.get("specs", [])],
            values=d.get("values"),
        )


@dataclass
class DataBinding:
    """A single data binding on a task link edge."""

    from_port: str
    """Name of the output port on the upstream task."""
    to_port: str
    """Name of the input port on the downstream task."""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DataBinding":
        return cls(from_port=d["from"], to_port=d["to"])

    def to_dict(self) -> Dict[str, str]:
        return {"from": self.from_port, "to": self.to_port}


# ── task script / run models ──────────────────────────────────────────────────


@dataclass
class TaskScript:
    """Automated execution script attached to a task."""

    id: uuid.UUID
    task_id: uuid.UUID
    script_type: str
    """One of ``"webhook"``, ``"shell"``, ``"python"``, ``"mcp_tool"``."""
    timeout_secs: int
    retry_limit: int
    created_at: datetime
    updated_at: datetime
    endpoint: Optional[str] = None
    script_body: Optional[str] = None
    execution_profile_id: Optional[uuid.UUID] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TaskScript":
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
        )


@dataclass
class TaskRun:
    """Record of a single automated task execution attempt."""

    id: uuid.UUID
    task_id: uuid.UUID
    created_at: datetime
    runner_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    outcome: Optional[str] = None
    """``"Success"``, ``"Failure"``, or ``"Timeout"``."""
    input_json: Optional[Any] = None
    output_json: Optional[Any] = None
    error_message: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TaskRun":
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
    def from_dict(cls, d: Dict[str, Any]) -> "TaskTeamRole":
        return cls(
            task_id=uuid.UUID(d["task_id"]),
            team_role_id=uuid.UUID(d["team_role_id"]),
            assigned_at=_dt(d["assigned_at"]),  # type: ignore[arg-type]
        )


# ── note models ───────────────────────────────────────────────────────────────


@dataclass
class Note:
    """A note attached to a task, workflow, or job."""

    id: uuid.UUID
    entity_type: str
    """``"task"``, ``"workflow"``, or ``"job"``."""
    entity_id: uuid.UUID
    title: str
    is_shared: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    body: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    """Set on replies; ``None`` for top-level notes."""
    folder_id: Optional[uuid.UUID] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Note":
        return cls(
            id=uuid.UUID(d["id"]),
            entity_type=d["entity_type"],
            entity_id=uuid.UUID(d["entity_id"]),
            title=d["title"],
            is_shared=d["is_shared"],
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            body=d.get("body"),
            parent_id=_uuid(d.get("parent_id")),
            folder_id=_uuid(d.get("folder_id")),
        )


@dataclass
class NoteFolder:
    """A folder used to organise notes."""

    id: uuid.UUID
    name: str
    created_by: str
    created_at: datetime

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NoteFolder":
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
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
    description: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ExecutionProfile":
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
    def from_dict(cls, d: Dict[str, Any]) -> "LoopBlock":
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
    def from_dict(cls, d: Dict[str, Any]) -> "CreateLoopBlockResponse":
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
    description: Optional[str] = None
    team_id: Optional[uuid.UUID] = None
    project_manager_id: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Project":
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            status=Status(d["status"]),
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            description=d.get("description"),
            team_id=_uuid(d.get("team_id")),
            project_manager_id=d.get("project_manager_id"),
        )


@dataclass
class ProjectWithJobs:
    """Project with its associated jobs."""

    project: Project
    jobs: List[Job] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProjectWithJobs":
        return cls(
            project=Project.from_dict(d),
            jobs=[Job.from_dict(j) for j in d.get("jobs", [])],
        )


# ── idea board models ─────────────────────────────────────────────────────────


@dataclass
class IdeaBoard:
    """An ideas board belonging to a project."""

    id: uuid.UUID
    name: str
    project_id: uuid.UUID
    created_by: str
    created_at: datetime

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "IdeaBoard":
        return cls(
            id=uuid.UUID(d["id"]),
            name=d["name"],
            project_id=uuid.UUID(d["project_id"]),
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
        )


@dataclass
class StickyNote:
    """A note positioned on an ideas board."""

    id: uuid.UUID
    """The underlying note ID."""
    title: str
    color: str
    x: float
    y: float
    width: float
    height: float
    created_by: str
    created_at: datetime
    updated_at: datetime
    body: Optional[str] = None
    workflow_id: Optional[uuid.UUID] = None
    """Soft reference to a backlog story (workflow)."""

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StickyNote":
        return cls(
            id=uuid.UUID(d["id"]),
            title=d["title"],
            color=d["color"],
            x=d["x"],
            y=d["y"],
            width=d["width"],
            height=d["height"],
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            updated_at=_dt(d["updated_at"]),  # type: ignore[arg-type]
            body=d.get("body"),
            workflow_id=_uuid(d.get("workflow_id")),
        )


@dataclass
class StickyOrigin:
    """Board and sticky returned by the by-workflow lookup."""

    board_id: uuid.UUID
    board_name: str
    sticky: StickyNote

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StickyOrigin":
        return cls(
            board_id=uuid.UUID(d["board_id"]),
            board_name=d["board_name"],
            sticky=StickyNote.from_dict(d["sticky"]),
        )


@dataclass
class NoteLink:
    """A directed link between two stickies on an ideas board."""

    id: uuid.UUID
    from_note_id: uuid.UUID
    to_note_id: uuid.UUID
    created_by: str
    created_at: datetime
    label: Optional[str] = None
    from_port: Optional[str] = None
    to_port: Optional[str] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "NoteLink":
        return cls(
            id=uuid.UUID(d["id"]),
            from_note_id=uuid.UUID(d["from_note_id"]),
            to_note_id=uuid.UUID(d["to_note_id"]),
            created_by=d["created_by"],
            created_at=_dt(d["created_at"]),  # type: ignore[arg-type]
            label=d.get("label"),
            from_port=d.get("from_port"),
            to_port=d.get("to_port"),
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
    task_id: Optional[uuid.UUID] = None
    workflow_id: Optional[uuid.UUID] = None
    actor_id: Optional[str] = None
    actor_username: Optional[str] = None
    propagation_depth: Optional[int] = None
    client_app: Optional[str] = None
    client_version: Optional[str] = None
    metadata: Optional[Any] = None

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TaskStateHistoryEntry":
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
