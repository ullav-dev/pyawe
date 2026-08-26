"""AweClient and resource sub-clients for the AWE API."""

from __future__ import annotations

import builtins
import uuid
from datetime import datetime
from typing import Any

from ._http import _compact, _HttpSession, _str_id
from .models import (
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
    PassthroughCheckpoints,
    Project,
    ProjectWithJobs,
    ResolvedConnection,
    ScheduledScript,
    ScheduledScriptDispatch,
    ScheduledScriptRun,
    ScheduleStatus,
    Status,
    Task,
    TaskLink,
    TaskPortSpec,
    TaskPortValues,
    TaskRun,
    TaskScript,
    TaskStateHistoryEntry,
    TaskTeamRole,
    TaskType,
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

# Sentinel used to distinguish "not provided" from ``None`` for the tri-state
# ``assigned_to`` field on task updates.
_UNSET: Any = object()


# ── workflows ─────────────────────────────────────────────────────────────────


class WorkflowsClient:
    """Methods for the ``/workflows`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, team_id: uuid.UUID | str | None = None) -> builtins.list[Workflow]:
        """Return all visible workflows, optionally filtered by team.

        Args:
            team_id: When supplied, returns only workflows for this team.

        Returns:
            List of :class:`~pyawe.models.Workflow` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: dict[str, Any] = {}
        if team_id is not None:
            params["team_id"] = _str_id(team_id)
        return [Workflow.from_dict(w) for w in self._http.get("/workflows", params=params)]

    def create(
        self,
        name: str,
        *,
        is_template: bool | None = None,
        description: str | None = None,
        status: Status | str | None = None,
        schedule_status: ScheduleStatus | str | None = None,
        job_id: uuid.UUID | str | None = None,
        team_id: uuid.UUID | str | None = None,
        is_shared: bool | None = None,
        sort_order: int | None = None,
        story_points: int | None = None,
        ticket_type: str | None = None,
        priority: str | None = None,
        reporter_id: uuid.UUID | str | None = None,
        external_reporter_first_name: str | None = None,
        external_reporter_last_name: str | None = None,
        external_reporter_email: str | None = None,
    ) -> Workflow:
        """Create a new workflow.

        Args:
            name: Human-readable workflow name.
            is_template: Mark as a reusable template.
            description: Optional description.
            status: Initial status (default ``"Not Started"``).
            schedule_status: Initial schedule status (default ``"N/A"``).
            job_id: Associate with an existing job.
            team_id: Assign to a team.
            is_shared: Visibility flag for team members (default ``False``).
            sort_order: Display order within the parent job (backlog or sprint).
            story_points: Story point estimate for this story-workflow.
            ticket_type: Cunav ticket type.
            priority: Cunav ticket priority.
            reporter_id: UUID of the reporting user.
            external_reporter_first_name: First name of a reporter with no
                UUM user row.
            external_reporter_last_name: Last name of a reporter with no
                UUM user row.
            external_reporter_email: Email of a reporter with no UUM user row.

        Returns:
            The newly created :class:`~pyawe.models.Workflow`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "is_template": is_template,
                "description": description,
                "status": status,
                "schedule_status": schedule_status,
                "job_id": _str_id(job_id),
                "team_id": _str_id(team_id),
                "is_shared": is_shared,
                "sort_order": sort_order,
                "story_points": story_points,
                "ticket_type": ticket_type,
                "priority": priority,
                "reporter_id": _str_id(reporter_id),
                "external_reporter_first_name": external_reporter_first_name,
                "external_reporter_last_name": external_reporter_last_name,
                "external_reporter_email": external_reporter_email,
            }
        )
        return Workflow.from_dict(self._http.post("/workflows", json=body))

    def get(self, workflow_id: uuid.UUID | str) -> WorkflowWithTasks:
        """Fetch a workflow with its tasks and links.

        Args:
            workflow_id: UUID of the workflow.

        Returns:
            :class:`~pyawe.models.WorkflowWithTasks`.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return WorkflowWithTasks.from_dict(self._http.get(f"/workflows/{_str_id(workflow_id)}"))

    def update(
        self,
        workflow_id: uuid.UUID | str,
        *,
        name: str | None = None,
        is_template: bool | None = None,
        description: str | None = None,
        status: Status | str | None = None,
        schedule_status: ScheduleStatus | str | None = None,
        job_id: uuid.UUID | str | None = None,
        is_shared: bool | None = None,
        sort_order: int | None = None,
        story_points: int | None = None,
        ticket_type: str | None = None,
        priority: str | None = None,
        resolved_at: datetime | None = None,
        external_reporter_first_name: str | None = None,
        external_reporter_last_name: str | None = None,
        external_reporter_email: str | None = None,
        togra_workflow_id: uuid.UUID | str | None = None,
        togra_project_id: uuid.UUID | str | None = None,
        ai_processed_at: datetime | None = None,
        ai_confidence: float | None = None,
        ai_should_route: bool | None = None,
        ai_outcome_feedback: str | None = None,
        ai_outcome_feedback_reason: str | None = None,
        ai_outcome_feedback_note_id: uuid.UUID | str | None = None,
    ) -> Workflow:
        """Update a workflow; only supplied fields are changed.

        All fields here are applied via COALESCE — omitting a field (or
        passing ``None``) leaves the stored value unchanged. To clear a
        previously-set external reporter field, pass an empty string, not
        ``None`` — per the server's documented behavior these three fields
        are the one exception to the omit-vs-clear convention.

        Args:
            workflow_id: UUID of the workflow to update.
            name: New name.
            is_template: Template flag.
            description: New description.
            status: New status.
            schedule_status: New schedule status.
            job_id: Reassign to a different job.
            is_shared: Visibility flag for team members.
            sort_order: Display order within the parent job.
            story_points: Story point estimate.
            ticket_type: Cunav ticket type.
            priority: Cunav ticket priority.
            resolved_at: Resolution timestamp.
            external_reporter_first_name: Pass ``""`` to clear.
            external_reporter_last_name: Pass ``""`` to clear.
            external_reporter_email: Pass ``""`` to clear.
            togra_workflow_id: Togra cross-reference workflow UUID.
            togra_project_id: Togra cross-reference project UUID.
            ai_processed_at: Timestamp the AI triage webhook finished processing.
            ai_confidence: Model's self-reported routing confidence (0.0-1.0).
            ai_should_route: Whether the model recommended auto-routing.
            ai_outcome_feedback: ``"helpful"`` or ``"unhelpful"``.
            ai_outcome_feedback_reason: Free-text explanation of the feedback.
            ai_outcome_feedback_note_id: The "AI Analysis" note this feedback judges.

        Returns:
            The updated :class:`~pyawe.models.Workflow`.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "is_template": is_template,
                "description": description,
                "status": status,
                "schedule_status": schedule_status,
                "job_id": _str_id(job_id),
                "is_shared": is_shared,
                "sort_order": sort_order,
                "story_points": story_points,
                "ticket_type": ticket_type,
                "priority": priority,
                "resolved_at": resolved_at.isoformat() if resolved_at else None,
                "external_reporter_first_name": external_reporter_first_name,
                "external_reporter_last_name": external_reporter_last_name,
                "external_reporter_email": external_reporter_email,
                "togra_workflow_id": _str_id(togra_workflow_id),
                "togra_project_id": _str_id(togra_project_id),
                "ai_processed_at": ai_processed_at.isoformat() if ai_processed_at else None,
                "ai_confidence": ai_confidence,
                "ai_should_route": ai_should_route,
                "ai_outcome_feedback": ai_outcome_feedback,
                "ai_outcome_feedback_reason": ai_outcome_feedback_reason,
                "ai_outcome_feedback_note_id": _str_id(ai_outcome_feedback_note_id),
            }
        )
        return Workflow.from_dict(self._http.put(f"/workflows/{_str_id(workflow_id)}", json=body))

    def delete(self, workflow_id: uuid.UUID | str) -> None:
        """Delete a workflow.

        Args:
            workflow_id: UUID of the workflow to delete.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/workflows/{_str_id(workflow_id)}")

    def set_team(self, workflow_id: uuid.UUID | str, team_id: uuid.UUID | str) -> Workflow:
        """Assign a workflow to a team.

        Args:
            workflow_id: UUID of the workflow.
            team_id: UUID of the team.

        Returns:
            The updated :class:`~pyawe.models.Workflow`.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return Workflow.from_dict(
            self._http.put(
                f"/workflows/{_str_id(workflow_id)}/team",
                json={"team_id": _str_id(team_id)},
            )
        )

    def clear_team(self, workflow_id: uuid.UUID | str) -> Workflow:
        """Remove the team assignment from a workflow.

        Args:
            workflow_id: UUID of the workflow.

        Returns:
            The updated :class:`~pyawe.models.Workflow`.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return Workflow.from_dict(self._http.delete(f"/workflows/{_str_id(workflow_id)}/team"))

    def merge(
        self,
        workflow_id: uuid.UUID | str,
        other_id: uuid.UUID | str,
    ) -> Workflow:
        """Merge *other_id* into *workflow_id*.

        The end task of *workflow_id* is linked to the start task of *other_id*;
        all tasks are moved into *workflow_id* and *other_id* is deleted.

        Args:
            workflow_id: UUID of the primary (absorbing) workflow.
            other_id: UUID of the workflow to merge in.

        Returns:
            The merged :class:`~pyawe.models.Workflow`.

        Raises:
            AweValidationError: If either workflow is missing a start/end task,
                or the two IDs are the same.
            AweNotFoundError: If either workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return Workflow.from_dict(
            self._http.post(f"/workflows/{_str_id(workflow_id)}/merge/{_str_id(other_id)}")
        )

    def set_duplicate_of(
        self,
        workflow_id: uuid.UUID | str,
        duplicate_of_workflow_id: uuid.UUID | str,
    ) -> Workflow:
        """Mark a workflow (ticket) as a duplicate of another.

        Args:
            workflow_id: UUID of the duplicate workflow.
            duplicate_of_workflow_id: UUID of the workflow it duplicates.

        Returns:
            The updated :class:`~pyawe.models.Workflow`.

        Raises:
            AweNotFoundError: If either workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return Workflow.from_dict(
            self._http.put(
                f"/workflows/{_str_id(workflow_id)}/duplicate-of",
                json={"duplicate_of_workflow_id": _str_id(duplicate_of_workflow_id)},
            )
        )

    def clear_duplicate_of(self, workflow_id: uuid.UUID | str) -> Workflow:
        """Remove the duplicate-of link from a workflow.

        Args:
            workflow_id: UUID of the workflow.

        Returns:
            The updated :class:`~pyawe.models.Workflow`.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return Workflow.from_dict(
            self._http.delete(f"/workflows/{_str_id(workflow_id)}/duplicate-of")
        )

    def list_duplicates(self, workflow_id: uuid.UUID | str) -> builtins.list[Workflow]:
        """Return all workflows marked as duplicates of *workflow_id*.

        Args:
            workflow_id: UUID of the target workflow.

        Returns:
            List of :class:`~pyawe.models.Workflow` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            Workflow.from_dict(w)
            for w in self._http.get(f"/workflows/{_str_id(workflow_id)}/duplicates")
        ]

    def duplicate(self, workflow_id: uuid.UUID | str) -> WorkflowWithTasks:
        """Create a full deep copy of a workflow.

        Copies tasks, links, port specs, scripts, team-role assignments, and
        the caller's own notes.

        Args:
            workflow_id: UUID of the workflow to duplicate.

        Returns:
            The new :class:`~pyawe.models.WorkflowWithTasks`.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return WorkflowWithTasks.from_dict(
            self._http.post(f"/workflows/{_str_id(workflow_id)}/duplicate")
        )

    def save_as_template(
        self,
        workflow_id: uuid.UUID | str,
        *,
        name: str | None = None,
        is_shared: bool | None = None,
    ) -> WorkflowWithTasks:
        """Save a job workflow as a reusable template.

        Requires team owner, leader, or admin role. Port specs, automation
        scripts, role assignments, links, and loop blocks are all retained.

        Args:
            workflow_id: UUID of the source job workflow.
            name: Template name (defaults to the source workflow name).
            is_shared: Visibility flag (defaults to the source workflow's setting).

        Returns:
            The new template :class:`~pyawe.models.WorkflowWithTasks`.

        Raises:
            AweValidationError: If the workflow is already a template.
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated or not privileged.
        """
        body = _compact({"name": name, "is_shared": is_shared})
        return WorkflowWithTasks.from_dict(
            self._http.post(f"/workflows/{_str_id(workflow_id)}/save-as-template", json=body)
        )


# ── tasks ─────────────────────────────────────────────────────────────────────


class TasksClient:
    """Methods for the ``/tasks`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, workflow_id: uuid.UUID | str | None = None) -> builtins.list[Task]:
        """List tasks, optionally filtered by workflow.

        Args:
            workflow_id: When supplied, returns only tasks within this workflow.

        Returns:
            List of :class:`~pyawe.models.Task` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: dict[str, Any] = {}
        if workflow_id is not None:
            params["workflow_id"] = _str_id(workflow_id)
        return [Task.from_dict(t) for t in self._http.get("/tasks", params=params)]

    def list_mine(
        self,
        role_ids: builtins.list[uuid.UUID | str] | None = None,
    ) -> builtins.list[TaskWithContext]:
        """Return tasks assigned to the authenticated user or their team roles.

        Args:
            role_ids: Team role UUIDs to include alongside direct assignments.

        Returns:
            List of :class:`~pyawe.models.TaskWithContext` objects, each enriched
            with workflow and job names.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: dict[str, Any] = {}
        if role_ids:
            params["role_ids"] = ",".join(_str_id(r) for r in role_ids)  # type: ignore[misc]
        return [TaskWithContext.from_dict(t) for t in self._http.get("/tasks/mine", params=params)]

    def create(
        self,
        name: str,
        workflow_id: uuid.UUID | str,
        *,
        is_template: bool | None = None,
        description: str | None = None,
        status: Status | str | None = None,
        schedule_status: ScheduleStatus | str | None = None,
        rework_task_id: uuid.UUID | str | None = None,
        is_start: bool | None = None,
        is_end: bool | None = None,
        task_type: TaskType | str | None = None,
        effort: int | None = None,
        priority: str | None = None,
        due_time: datetime | None = None,
    ) -> Task:
        """Create a task within a workflow.

        Args:
            name: Task name.
            workflow_id: UUID of the containing workflow.
            is_template: Mark as a template task.
            description: Optional description.
            status: Initial status (default ``"Not Started"``).
            schedule_status: Initial schedule status (default ``"N/A"``).
            rework_task_id: UUID of the task this one reworks, if any.
            is_start: Designate as the workflow start task.
            is_end: Designate as the workflow end task.
            task_type: ``"standard"`` (default), ``"decision"``,
                ``"automated"``, ``"loop_block"``, or ``"checkpoint"``.
            effort: Unitless effort estimate (e.g. story points).
            priority: ``"none"`` (default), ``"low"``, ``"medium"``,
                ``"high"``, or ``"critical"``.
            due_time: Optional point in time the task is due.

        Returns:
            The newly created :class:`~pyawe.models.Task`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "workflow_id": _str_id(workflow_id),
                "is_template": is_template,
                "description": description,
                "status": status,
                "schedule_status": schedule_status,
                "rework_task_id": _str_id(rework_task_id),
                "is_start": is_start,
                "is_end": is_end,
                "task_type": task_type,
                "effort": effort,
                "priority": priority,
                "due_time": due_time.isoformat() if due_time else None,
            }
        )
        return Task.from_dict(self._http.post("/tasks", json=body))

    def get(self, task_id: uuid.UUID | str) -> Task:
        """Fetch a single task.

        Args:
            task_id: UUID of the task.

        Returns:
            :class:`~pyawe.models.Task`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return Task.from_dict(self._http.get(f"/tasks/{_str_id(task_id)}"))

    def update(
        self,
        task_id: uuid.UUID | str,
        *,
        name: str | None = None,
        is_template: bool | None = None,
        description: str | None = None,
        status: Status | str | None = None,
        schedule_status: ScheduleStatus | str | None = None,
        rework_task_id: uuid.UUID | str | None = None,
        is_start: bool | None = None,
        is_end: bool | None = None,
        task_type: TaskType | str | None = None,
        assigned_to: Any = _UNSET,
        decision_input_port: Any = _UNSET,
        is_locked: bool | None = None,
        canvas_x: float | None = None,
        canvas_y: float | None = None,
        effort: Any = _UNSET,
        priority: str | None = None,
        due_time: Any = _UNSET,
        branch_name: Any = _UNSET,
        port_namespace: Any = _UNSET,
    ) -> Task:
        """Update a task; only supplied fields are changed.

        ``assigned_to``, ``decision_input_port``, ``effort``, ``due_time``,
        ``branch_name``, and ``port_namespace`` are tri-state fields:

        - **Omitted** (default): field is left unchanged.
        - **``None``**: clears the current value.
        - **A value**: sets the field.

        Args:
            task_id: UUID of the task to update.
            name: New name.
            is_template: Template flag.
            description: New description.
            status: New status. Completed/cancelled tasks cannot be
                transitioned. Setting to ``"In Progress"`` stamps ``start_time``;
                setting to ``"Complete"`` stamps ``end_time``.
            schedule_status: New schedule status.
            rework_task_id: Rework back-link.
            is_start: Start task flag.
            is_end: End task flag.
            task_type: Task type string.
            assigned_to: User ID string, ``None`` to clear, or omit to leave unchanged.
            decision_input_port: Input port name for auto-decide, ``None`` to clear,
                or omit to leave unchanged.
            is_locked: Lock or unlock structural edits (requires owner/leader/admin).
            canvas_x: Canvas X position from the workflow editor.
            canvas_y: Canvas Y position from the workflow editor.
            effort: Unitless effort estimate, ``None`` to clear, or omit to leave unchanged.
            priority: ``"none"``, ``"low"``, ``"medium"``, ``"high"``, or ``"critical"``.
            due_time: Due time, ``None`` to clear, or omit to leave unchanged.
            branch_name: Git branch name, ``None`` to clear, or omit to leave unchanged.
            port_namespace: Checkpoint port namespace override
                (``^[a-z][a-z0-9_]*$``), ``None`` to clear (falls back to
                ``t{task_number}``), or omit to leave unchanged.

        Returns:
            The updated :class:`~pyawe.models.Task`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweValidationError: If the status transition is invalid.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "is_template": is_template,
                "description": description,
                "status": status,
                "schedule_status": schedule_status,
                "rework_task_id": _str_id(rework_task_id),
                "is_start": is_start,
                "is_end": is_end,
                "task_type": task_type,
                "is_locked": is_locked,
                "canvas_x": canvas_x,
                "canvas_y": canvas_y,
                "priority": priority,
            }
        )
        if assigned_to is not _UNSET:
            body["assigned_to"] = assigned_to  # None → clear; str → set
        if decision_input_port is not _UNSET:
            body["decision_input_port"] = decision_input_port  # None → clear; str → set
        if effort is not _UNSET:
            body["effort"] = effort  # None → clear; int → set
        if due_time is not _UNSET:
            body["due_time"] = due_time.isoformat() if due_time is not None else None
        if branch_name is not _UNSET:
            body["branch_name"] = branch_name  # None → clear; str → set
        if port_namespace is not _UNSET:
            body["port_namespace"] = port_namespace  # None → clear; str → set
        return Task.from_dict(self._http.put(f"/tasks/{_str_id(task_id)}", json=body))

    def delete(self, task_id: uuid.UUID | str) -> None:
        """Delete a task.

        Args:
            task_id: UUID of the task to delete.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/tasks/{_str_id(task_id)}")

    def decide(self, task_id: uuid.UUID | str, branch_label: str) -> Task:
        """Resolve a decision task by choosing an outgoing branch.

        Sets the task status to ``"Complete"``, records ``decision_outcome``,
        activates the chosen successor, and cancels tasks on rejected branches.

        Args:
            task_id: UUID of a decision task.
            branch_label: Label of the branch to follow. Must match an outgoing
                link's ``branch_label``.

        Returns:
            The decided :class:`~pyawe.models.Task`.

        Raises:
            AweValidationError: If the task is not a decision task, is already
                complete, or the branch label is not found.
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return Task.from_dict(
            self._http.post(
                f"/tasks/{_str_id(task_id)}/decide",
                json={"branch_label": branch_label},
            )
        )

    def clear_rework(self, task_id: uuid.UUID | str) -> Task:
        """Remove the rework back-link from a task.

        Args:
            task_id: UUID of the task.

        Returns:
            The updated :class:`~pyawe.models.Task`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return Task.from_dict(self._http.delete(f"/tasks/{_str_id(task_id)}/rework"))

    def request_rework(self, task_id: uuid.UUID | str) -> Task:
        """Manually trigger a rework of *task_id*.

        Spawns a fresh clone of the subgraph between the task's configured
        ``rework_task_id`` and the task itself, rewires the clone chain in
        place of the original, and marks the original task ``"Reworked"``.
        The original target/intermediate tasks are never touched.

        Args:
            task_id: UUID of the task that judged rework was needed (the
                "source" task; must already have ``rework_task_id`` set).

        Returns:
            The reworked (now ``"Reworked"``-status) :class:`~pyawe.models.Task`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweValidationError: If the task has no ``rework_task_id`` configured.
            AweAuthError: If not authenticated.
        """
        return Task.from_dict(self._http.post(f"/tasks/{_str_id(task_id)}/rework"))


# ── task links ────────────────────────────────────────────────────────────────


class TaskLinksClient:
    """Methods for task link management (``/task-links`` and ``/tasks/{id}/…``)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def create(
        self,
        from_task_id: uuid.UUID | str,
        to_task_id: uuid.UUID | str,
        *,
        branch_label: str | None = None,
    ) -> TaskLink:
        """Create a directed link between two tasks.

        Args:
            from_task_id: UUID of the upstream task.
            to_task_id: UUID of the downstream task.
            branch_label: Required when the upstream task is a decision task.

        Returns:
            The created :class:`~pyawe.models.TaskLink`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body: dict[str, Any] = {
            "from_task_id": _str_id(from_task_id),
            "to_task_id": _str_id(to_task_id),
        }
        if branch_label is not None:
            body["branch_label"] = branch_label
        return TaskLink.from_dict(self._http.post("/task-links", json=body))

    def delete(
        self,
        from_task_id: uuid.UUID | str,
        to_task_id: uuid.UUID | str,
    ) -> None:
        """Delete the link between two tasks.

        Args:
            from_task_id: UUID of the upstream task.
            to_task_id: UUID of the downstream task.

        Raises:
            AweNotFoundError: If the link does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/task-links/{_str_id(from_task_id)}/{_str_id(to_task_id)}")

    def get_next(self, task_id: uuid.UUID | str) -> list[Task]:
        """Return the immediate successor tasks of *task_id*.

        Args:
            task_id: UUID of the task.

        Returns:
            List of :class:`~pyawe.models.Task` objects.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return [Task.from_dict(t) for t in self._http.get(f"/tasks/{_str_id(task_id)}/next")]

    def get_previous(self, task_id: uuid.UUID | str) -> list[Task]:
        """Return the immediate predecessor tasks of *task_id*.

        Args:
            task_id: UUID of the task.

        Returns:
            List of :class:`~pyawe.models.Task` objects.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return [Task.from_dict(t) for t in self._http.get(f"/tasks/{_str_id(task_id)}/previous")]

    def get_outgoing(self, task_id: uuid.UUID | str) -> list[TaskLink]:
        """Return all outgoing links from *task_id*.

        Args:
            task_id: UUID of the task.

        Returns:
            List of :class:`~pyawe.models.TaskLink` objects.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return [TaskLink.from_dict(lk) for lk in self._http.get(f"/tasks/{_str_id(task_id)}/links")]

    def update_bindings(
        self,
        from_task_id: uuid.UUID | str,
        to_task_id: uuid.UUID | str,
        bindings: list[DataBinding],
    ) -> TaskLink:
        """Replace the data bindings on a task link edge.

        Bindings are applied by the propagator when the upstream task completes,
        copying output values to the downstream task's inputs.

        Args:
            from_task_id: UUID of the upstream task.
            to_task_id: UUID of the downstream task.
            bindings: New list of :class:`~pyawe.models.DataBinding` objects.

        Returns:
            The updated :class:`~pyawe.models.TaskLink`.

        Raises:
            AweNotFoundError: If the link does not exist.
            AweAuthError: If not authenticated.
        """
        return TaskLink.from_dict(
            self._http.put(
                f"/task-links/{_str_id(from_task_id)}/{_str_id(to_task_id)}/bindings",
                json={"bindings": [b.to_dict() for b in bindings]},
            )
        )


# ── task ports ────────────────────────────────────────────────────────────────


class TaskPortsClient:
    """Methods for task port spec and value management (``/tasks/{id}/ports``, etc.)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def get_workflow_ports(self, workflow_id: uuid.UUID | str) -> list[TaskPortSpec]:
        """Return all port specs for every task in a workflow.

        Args:
            workflow_id: UUID of the workflow.

        Returns:
            List of :class:`~pyawe.models.TaskPortSpec` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            TaskPortSpec.from_dict(s)
            for s in self._http.get(f"/workflows/{_str_id(workflow_id)}/ports")
        ]

    def list_specs(self, task_id: uuid.UUID | str) -> list[TaskPortSpec]:
        """Return all port specs (inputs and outputs) for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            List of :class:`~pyawe.models.TaskPortSpec` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            TaskPortSpec.from_dict(s) for s in self._http.get(f"/tasks/{_str_id(task_id)}/ports")
        ]

    def create_spec(
        self,
        task_id: uuid.UUID | str,
        direction: str,
        name: str,
        value_type: str,
        *,
        required: bool | None = None,
        description: str | None = None,
        default_value: Any | None = None,
        sort_order: int | None = None,
    ) -> TaskPortSpec:
        """Add a port spec to a task.

        Args:
            task_id: UUID of the task.
            direction: ``"input"`` or ``"output"``.
            name: Port name (unique within direction on the task).
            value_type: ``"string"``, ``"number"``, ``"boolean"``, ``"json"``,
                ``"file"``, or ``"dam_asset"``.
            required: Whether this input is required (default ``False``;
                ignored for outputs).
            description: Human-readable description.
            default_value: JSON default applied at instantiation for optional inputs.
            sort_order: Display order.

        Returns:
            The created :class:`~pyawe.models.TaskPortSpec`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "direction": direction,
                "name": name,
                "value_type": value_type,
                "required": required,
                "description": description,
                "default_value": default_value,
                "sort_order": sort_order,
            }
        )
        return TaskPortSpec.from_dict(
            self._http.post(f"/tasks/{_str_id(task_id)}/ports", json=body)
        )

    def update_spec(
        self,
        task_id: uuid.UUID | str,
        port_id: uuid.UUID | str,
        *,
        name: str | None = None,
        value_type: str | None = None,
        required: bool | None = None,
        description: str | None = None,
        default_value: Any | None = None,
        sort_order: int | None = None,
    ) -> TaskPortSpec:
        """Update a port spec; only supplied fields are changed.

        Args:
            task_id: UUID of the task.
            port_id: UUID of the port spec.
            name: New port name.
            value_type: New value type.
            required: Required flag.
            description: New description.
            default_value: New default value.
            sort_order: New sort order.

        Returns:
            The updated :class:`~pyawe.models.TaskPortSpec`.

        Raises:
            AweNotFoundError: If the port spec does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "value_type": value_type,
                "required": required,
                "description": description,
                "default_value": default_value,
                "sort_order": sort_order,
            }
        )
        return TaskPortSpec.from_dict(
            self._http.put(f"/tasks/{_str_id(task_id)}/ports/{_str_id(port_id)}", json=body)
        )

    def delete_spec(
        self,
        task_id: uuid.UUID | str,
        port_id: uuid.UUID | str,
    ) -> None:
        """Delete a port spec.

        Args:
            task_id: UUID of the task.
            port_id: UUID of the port spec.

        Raises:
            AweNotFoundError: If the port spec does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/tasks/{_str_id(task_id)}/ports/{_str_id(port_id)}")

    def get_inputs(self, task_id: uuid.UUID | str) -> TaskPortValues:
        """Return input port specs and current values for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            :class:`~pyawe.models.TaskPortValues` with ``direction == "input"`` specs.

        Raises:
            AweAuthError: If not authenticated.
        """
        return TaskPortValues.from_dict(self._http.get(f"/tasks/{_str_id(task_id)}/inputs"))

    def patch_inputs(self, task_id: uuid.UUID | str, values: dict[str, Any]) -> TaskPortValues:
        """Partially update the input values of a task.

        Only the keys present in *values* are written; others are left unchanged.

        Args:
            task_id: UUID of the task.
            values: Mapping of ``{port_name: value}`` pairs to set.

        Returns:
            Updated :class:`~pyawe.models.TaskPortValues`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return TaskPortValues.from_dict(
            self._http.patch(f"/tasks/{_str_id(task_id)}/inputs", json={"values": values})
        )

    def get_outputs(self, task_id: uuid.UUID | str) -> TaskPortValues:
        """Return output port specs and current values for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            :class:`~pyawe.models.TaskPortValues` with ``direction == "output"`` specs.

        Raises:
            AweAuthError: If not authenticated.
        """
        return TaskPortValues.from_dict(self._http.get(f"/tasks/{_str_id(task_id)}/outputs"))

    def patch_outputs(self, task_id: uuid.UUID | str, values: dict[str, Any]) -> Task:
        """Partially update the output values of a task (runner use).

        Only the keys present in *values* are written; others are left unchanged.
        Typically called by the automated runner after a task completes.

        Args:
            task_id: UUID of the task.
            values: Mapping of ``{port_name: value}`` pairs to set.

        Returns:
            Updated :class:`~pyawe.models.Task`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return Task.from_dict(
            self._http.patch(f"/tasks/{_str_id(task_id)}/outputs", json={"values": values})
        )


# ── task scripts ──────────────────────────────────────────────────────────────


class TaskScriptsClient:
    """Methods for automated task script management (``/tasks/{id}/script``)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def get(self, task_id: uuid.UUID | str) -> TaskScript:
        """Fetch the script attached to a task.

        Args:
            task_id: UUID of the task.

        Returns:
            :class:`~pyawe.models.TaskScript`.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        return TaskScript.from_dict(self._http.get(f"/tasks/{_str_id(task_id)}/script"))

    def upsert(
        self,
        task_id: uuid.UUID | str,
        *,
        script_type: str | None = None,
        endpoint: str | None = None,
        script_body: str | None = None,
        timeout_secs: int | None = None,
        retry_limit: int | None = None,
        execution_profile_id: uuid.UUID | str | None = None,
        connection_id: uuid.UUID | str | None = None,
    ) -> TaskScript:
        """Create or fully replace the script on a task.

        Args:
            task_id: UUID of the task.
            script_type: ``"webhook"`` (default), ``"shell"``, ``"python"``,
                ``"mcp_tool"``, or ``"email"``.
            endpoint: Webhook URL; required when ``script_type == "webhook"``.
            script_body: Script source; required for ``"shell"``, ``"python"``,
                and ``"mcp_tool"`` types. Must be absent for ``"email"``.
            timeout_secs: Execution timeout in seconds.
            retry_limit: Maximum number of retry attempts.
            execution_profile_id: Execution profile for Kubernetes dispatch
                (``"shell"`` and ``"python"`` only).
            connection_id: Connection profile to resolve auth from at run
                time. Required (must reference an ``smtp`` connection) when
                ``script_type == "email"``.

        Returns:
            The upserted :class:`~pyawe.models.TaskScript`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "script_type": script_type,
                "endpoint": endpoint,
                "script_body": script_body,
                "timeout_secs": timeout_secs,
                "retry_limit": retry_limit,
                "execution_profile_id": _str_id(execution_profile_id),
                "connection_id": _str_id(connection_id),
            }
        )
        return TaskScript.from_dict(self._http.put(f"/tasks/{_str_id(task_id)}/script", json=body))

    def delete(self, task_id: uuid.UUID | str) -> None:
        """Remove the script from a task.

        Args:
            task_id: UUID of the task.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/tasks/{_str_id(task_id)}/script")


# ── task secrets ─────────────────────────────────────────────────────────────


class TaskSecretsClient:
    """Methods for task secret value management (``/tasks/{id}/secrets``)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def patch(self, task_id: uuid.UUID | str, values: dict[str, str | None]) -> None:
        """Set or delete secret values on a task.

        Each key in *values* is a port name. A string value stores the secret;
        ``None`` deletes it.

        Args:
            task_id: UUID of the task.
            values: Mapping of ``{port_name: secret_value_or_none}``.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.patch(f"/tasks/{_str_id(task_id)}/secrets", json={"values": values})

    def get(self, task_id: uuid.UUID | str) -> dict[str, str]:
        """Return decrypted secret values for a task (service role only).

        Args:
            task_id: UUID of the task.

        Returns:
            Dict of ``{port_name: plaintext_value}``.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
            AweError: 403 if the caller does not hold the service role.
        """
        data = self._http.get(f"/tasks/{_str_id(task_id)}/secrets")
        result: dict[str, str] = data.get("values", {})
        return result


# ── task runs ─────────────────────────────────────────────────────────────────


class TaskRunsClient:
    """Methods for automated task execution history (``/tasks/{id}/runs``)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, task_id: uuid.UUID | str) -> builtins.list[TaskRun]:
        """Return all execution run records for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            List of :class:`~pyawe.models.TaskRun` objects, newest first.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [TaskRun.from_dict(r) for r in self._http.get(f"/tasks/{_str_id(task_id)}/runs")]

    def create(
        self,
        task_id: uuid.UUID | str,
        outcome: str,
        started_at: datetime,
        completed_at: datetime,
        *,
        run_id: uuid.UUID | str | None = None,
        runner_id: str | None = None,
        input_json: Any | None = None,
        output_json: Any | None = None,
        error_message: str | None = None,
        branch_name: str | None = None,
    ) -> TaskRun:
        """Record a completed execution run.

        This endpoint is called by the runner after executing an automated task.

        Args:
            task_id: UUID of the task.
            outcome: ``"Success"``, ``"Failure"``, or ``"Timeout"``.
            started_at: When execution began.
            completed_at: When execution ended (or timed out).
            run_id: Optional client-supplied UUID for idempotent recording.
            runner_id: Identifier of the runner that executed the task.
            input_json: Snapshot of the dispatch payload.
            output_json: Structured output produced by the task.
            error_message: Error details when ``outcome != "Success"``.
            branch_name: Git branch extracted from the run's output (``mcp_tool``
                scripts declaring ``branch_output_field``). When present on a
                successful run, the task's ``branch_name`` is updated to this value.

        Returns:
            The recorded :class:`~pyawe.models.TaskRun`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        body: dict[str, Any] = {
            "outcome": outcome,
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
        }
        if run_id is not None:
            body["run_id"] = _str_id(run_id)
        if runner_id is not None:
            body["runner_id"] = runner_id
        if input_json is not None:
            body["input_json"] = input_json
        if output_json is not None:
            body["output_json"] = output_json
        if error_message is not None:
            body["error_message"] = error_message
        if branch_name is not None:
            body["branch_name"] = branch_name
        return TaskRun.from_dict(self._http.post(f"/tasks/{_str_id(task_id)}/runs", json=body))

    def get(
        self,
        task_id: uuid.UUID | str,
        run_id: uuid.UUID | str,
    ) -> TaskRun:
        """Fetch a single execution run record.

        Args:
            task_id: UUID of the task.
            run_id: UUID of the run.

        Returns:
            :class:`~pyawe.models.TaskRun`.

        Raises:
            AweNotFoundError: If the run does not exist.
            AweAuthError: If not authenticated.
        """
        return TaskRun.from_dict(
            self._http.get(f"/tasks/{_str_id(task_id)}/runs/{_str_id(run_id)}")
        )


# ── task team roles ───────────────────────────────────────────────────────────


class TaskTeamRolesClient:
    """Methods for task team-role assignment (``/tasks/{id}/team-roles``)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, task_id: uuid.UUID | str) -> builtins.list[TaskTeamRole]:
        """Return all team-role assignments for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            List of :class:`~pyawe.models.TaskTeamRole` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            TaskTeamRole.from_dict(r)
            for r in self._http.get(f"/tasks/{_str_id(task_id)}/team-roles")
        ]

    def assign(
        self,
        task_id: uuid.UUID | str,
        team_role_id: uuid.UUID | str,
    ) -> TaskTeamRole:
        """Assign a team role to a task.

        Args:
            task_id: UUID of the task.
            team_role_id: UUID of the team role.

        Returns:
            The created :class:`~pyawe.models.TaskTeamRole`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        return TaskTeamRole.from_dict(
            self._http.post(
                f"/tasks/{_str_id(task_id)}/team-roles",
                json={"team_role_id": _str_id(team_role_id)},
            )
        )

    def remove(
        self,
        task_id: uuid.UUID | str,
        team_role_id: uuid.UUID | str,
    ) -> None:
        """Remove a team-role assignment from a task.

        Args:
            task_id: UUID of the task.
            team_role_id: UUID of the team role assignment to remove.

        Raises:
            AweNotFoundError: If the assignment does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/tasks/{_str_id(task_id)}/team-roles/{_str_id(team_role_id)}")


# ── jobs ──────────────────────────────────────────────────────────────────────


class JobsClient:
    """Methods for the ``/jobs`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, team_id: uuid.UUID | str | None = None) -> builtins.list[Job]:
        """Return all jobs, optionally filtered by team.

        Args:
            team_id: When supplied, returns only jobs for this team.

        Returns:
            List of :class:`~pyawe.models.Job` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: dict[str, Any] = {}
        if team_id is not None:
            params["team_id"] = _str_id(team_id)
        return [Job.from_dict(j) for j in self._http.get("/jobs", params=params)]

    def create(
        self,
        name: str,
        *,
        status: Status | str | None = None,
        schedule_status: ScheduleStatus | str | None = None,
        team_id: uuid.UUID | str | None = None,
        project_id: uuid.UUID | str | None = None,
        job_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> Job:
        """Create a new job.

        Args:
            name: Job name.
            status: Initial status (default ``"Not Started"``).
            schedule_status: Initial schedule status (default ``"N/A"``).
            team_id: Assign to a team.
            project_id: Associate with a project.
            job_type: ``"sprint"``, ``"kanban"``, or ``"backlog"``.
            start_date: Sprint start date (ISO 8601, e.g. ``"2026-01-01"``).
            end_date: Sprint end date (ISO 8601).

        Returns:
            The newly created :class:`~pyawe.models.Job`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "status": status,
                "schedule_status": schedule_status,
                "team_id": _str_id(team_id),
                "project_id": _str_id(project_id),
                "job_type": job_type,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
        return Job.from_dict(self._http.post("/jobs", json=body))

    def get(self, job_id: uuid.UUID | str) -> JobWithWorkflows:
        """Fetch a job with its associated workflows.

        Args:
            job_id: UUID of the job.

        Returns:
            :class:`~pyawe.models.JobWithWorkflows`.

        Raises:
            AweNotFoundError: If the job does not exist.
            AweAuthError: If not authenticated.
        """
        return JobWithWorkflows.from_dict(self._http.get(f"/jobs/{_str_id(job_id)}"))

    def update(
        self,
        job_id: uuid.UUID | str,
        *,
        name: str | None = None,
        status: Status | str | None = None,
        schedule_status: ScheduleStatus | str | None = None,
        archived: bool | None = None,
        project_id: uuid.UUID | str | None = None,
        job_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        ai_enabled: bool | None = None,
        ai_togra_project_id: uuid.UUID | str | None = None,
        ai_togra_job_id: uuid.UUID | str | None = None,
        ai_togra_template_id: uuid.UUID | str | None = None,
        ai_route_confidence_threshold: float | None = None,
        ai_rules: Any | None = None,
        email_connection_id: uuid.UUID | str | None = None,
        inbound_email_connection_id: uuid.UUID | str | None = None,
    ) -> Job:
        """Update a job; only supplied fields are changed.

        Args:
            job_id: UUID of the job to update.
            name: New name.
            status: New status.
            schedule_status: New schedule status.
            archived: Archive flag.
            project_id: Reassign to a different project.
            job_type: ``"sprint"``, ``"kanban"``, or ``"backlog"``.
            start_date: Sprint start date (ISO 8601).
            end_date: Sprint end date (ISO 8601).
            ai_enabled: Whether new tickets in this queue are dispatched to
                cunav's AI triage webhook (``job_type == "kanban"`` queues only).
            ai_togra_project_id: Togra project routed to when AI confidence clears
                the threshold.
            ai_togra_job_id: Togra job routed to.
            ai_togra_template_id: Togra template routed to.
            ai_route_confidence_threshold: Confidence threshold for auto-routing.
            ai_rules: Per-outcome-type enable/threshold config.
            email_connection_id: ``smtp`` connection used for outbound automated email.
            inbound_email_connection_id: ``imap`` connection treated as this queue's
                support mailbox.

        Returns:
            The updated :class:`~pyawe.models.Job`.

        Raises:
            AweNotFoundError: If the job does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "status": status,
                "schedule_status": schedule_status,
                "archived": archived,
                "project_id": _str_id(project_id),
                "job_type": job_type,
                "start_date": start_date,
                "end_date": end_date,
                "ai_enabled": ai_enabled,
                "ai_togra_project_id": _str_id(ai_togra_project_id),
                "ai_togra_job_id": _str_id(ai_togra_job_id),
                "ai_togra_template_id": _str_id(ai_togra_template_id),
                "ai_route_confidence_threshold": ai_route_confidence_threshold,
                "ai_rules": ai_rules,
                "email_connection_id": _str_id(email_connection_id),
                "inbound_email_connection_id": _str_id(inbound_email_connection_id),
            }
        )
        return Job.from_dict(self._http.put(f"/jobs/{_str_id(job_id)}", json=body))

    def get_workflow_allocations(
        self, job_id: uuid.UUID | str
    ) -> builtins.list[WorkflowAllocation]:
        """Return first-task allocation summaries for every workflow in a job.

        Args:
            job_id: UUID of the job.

        Returns:
            List of :class:`~pyawe.models.WorkflowAllocation` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            WorkflowAllocation.from_dict(a)
            for a in self._http.get(f"/jobs/{_str_id(job_id)}/workflow-allocations")
        ]

    def delete(self, job_id: uuid.UUID | str) -> None:
        """Delete a job.

        Args:
            job_id: UUID of the job to delete.

        Raises:
            AweNotFoundError: If the job does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/jobs/{_str_id(job_id)}")

    def clone_workflow(
        self,
        job_id: uuid.UUID | str,
        workflow_id: uuid.UUID | str,
        *,
        name: str | None = None,
    ) -> Workflow:
        """Clone a workflow template into a job.

        Args:
            job_id: UUID of the target job.
            workflow_id: UUID of the workflow template to clone.
            name: Overrides the cloned workflow's name; omit or pass an
                empty/whitespace-only string to keep the template's name.

        Returns:
            The new :class:`~pyawe.models.Workflow` inside the job. Use
            :meth:`WorkflowsClient.get` if you also need its cloned tasks/links.

        Raises:
            AweNotFoundError: If the job or workflow does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact({"name": name})
        return Workflow.from_dict(
            self._http.post(
                f"/jobs/{_str_id(job_id)}/workflows/from-template/{_str_id(workflow_id)}",
                json=body,
            )
        )

    def set_team(self, job_id: uuid.UUID | str, team_id: uuid.UUID | str) -> Job:
        """Assign a job to a team.

        Args:
            job_id: UUID of the job.
            team_id: UUID of the team.

        Returns:
            The updated :class:`~pyawe.models.Job`.

        Raises:
            AweNotFoundError: If the job does not exist.
            AweAuthError: If not authenticated.
        """
        return Job.from_dict(
            self._http.put(
                f"/jobs/{_str_id(job_id)}/team",
                json={"team_id": _str_id(team_id)},
            )
        )

    def clear_team(self, job_id: uuid.UUID | str) -> Job:
        """Remove the team assignment from a job.

        Args:
            job_id: UUID of the job.

        Returns:
            The updated :class:`~pyawe.models.Job`.

        Raises:
            AweNotFoundError: If the job does not exist.
            AweAuthError: If not authenticated.
        """
        return Job.from_dict(self._http.delete(f"/jobs/{_str_id(job_id)}/team"))


# ── execution profiles ────────────────────────────────────────────────────────


class ExecutionProfilesClient:
    """Methods for the ``/execution-profiles`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self) -> builtins.list[ExecutionProfile]:
        """Return all execution profiles.

        Returns:
            List of :class:`~pyawe.models.ExecutionProfile` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [ExecutionProfile.from_dict(p) for p in self._http.get("/execution-profiles")]

    def create(
        self,
        name: str,
        image: str,
        *,
        description: str | None = None,
        cpu_request: str | None = None,
        cpu_limit: str | None = None,
        memory_request: str | None = None,
        memory_limit: str | None = None,
        image_pull_policy: str | None = None,
        enable_buildkit_sidecar: bool | None = None,
        runner_pool: str | None = None,
    ) -> ExecutionProfile:
        """Create a new execution profile.

        The *image* must match the server's ``AWE_ALLOWED_IMAGES`` patterns.

        Args:
            name: Unique human-readable name shown in the UI.
            image: Full OCI image reference, e.g. ``"python:3.12-slim"``.
            description: Optional description.
            cpu_request: Kubernetes CPU request, e.g. ``"100m"``.
            cpu_limit: Kubernetes CPU limit, e.g. ``"1"``.
            memory_request: Kubernetes memory request, e.g. ``"128Mi"``.
            memory_limit: Kubernetes memory limit, e.g. ``"512Mi"``.
            image_pull_policy: Kubernetes ``imagePullPolicy`` (default ``"IfNotPresent"``).
            enable_buildkit_sidecar: Opt in to a rootless ``buildkitd`` native
                sidecar (default ``False``).
            runner_pool: Which ``awe-runner`` pool dispatches this profile's
                tasks (default ``"default"``).

        Returns:
            The newly created :class:`~pyawe.models.ExecutionProfile`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "image": image,
                "description": description,
                "cpu_request": cpu_request,
                "cpu_limit": cpu_limit,
                "memory_request": memory_request,
                "memory_limit": memory_limit,
                "image_pull_policy": image_pull_policy,
                "enable_buildkit_sidecar": enable_buildkit_sidecar,
                "runner_pool": runner_pool,
            }
        )
        return ExecutionProfile.from_dict(self._http.post("/execution-profiles", json=body))

    def get(self, profile_id: uuid.UUID | str) -> ExecutionProfile:
        """Fetch an execution profile.

        Args:
            profile_id: UUID of the execution profile.

        Returns:
            :class:`~pyawe.models.ExecutionProfile`.

        Raises:
            AweNotFoundError: If the profile does not exist.
            AweAuthError: If not authenticated.
        """
        return ExecutionProfile.from_dict(
            self._http.get(f"/execution-profiles/{_str_id(profile_id)}")
        )

    def update(
        self,
        profile_id: uuid.UUID | str,
        *,
        name: str | None = None,
        image: str | None = None,
        description: str | None = None,
        cpu_request: str | None = None,
        cpu_limit: str | None = None,
        memory_request: str | None = None,
        memory_limit: str | None = None,
        image_pull_policy: str | None = None,
        enable_buildkit_sidecar: bool | None = None,
        runner_pool: str | None = None,
    ) -> ExecutionProfile:
        """Update an execution profile; only supplied fields are changed.

        Args:
            profile_id: UUID of the profile to update.
            name: New name.
            image: New OCI image reference.
            description: New description.
            cpu_request: New CPU request.
            cpu_limit: New CPU limit.
            memory_request: New memory request.
            memory_limit: New memory limit.
            image_pull_policy: New Kubernetes ``imagePullPolicy``.
            enable_buildkit_sidecar: Opt in to a rootless ``buildkitd`` native sidecar.
            runner_pool: New ``awe-runner`` pool.

        Returns:
            The updated :class:`~pyawe.models.ExecutionProfile`.

        Raises:
            AweNotFoundError: If the profile does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "image": image,
                "description": description,
                "cpu_request": cpu_request,
                "cpu_limit": cpu_limit,
                "memory_request": memory_request,
                "memory_limit": memory_limit,
                "image_pull_policy": image_pull_policy,
                "enable_buildkit_sidecar": enable_buildkit_sidecar,
                "runner_pool": runner_pool,
            }
        )
        return ExecutionProfile.from_dict(
            self._http.put(f"/execution-profiles/{_str_id(profile_id)}", json=body)
        )

    def delete(self, profile_id: uuid.UUID | str) -> None:
        """Delete an execution profile.

        Args:
            profile_id: UUID of the profile to delete.

        Raises:
            AweNotFoundError: If the profile does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/execution-profiles/{_str_id(profile_id)}")


# ── loop blocks ───────────────────────────────────────────────────────────────


class LoopBlocksClient:
    """Methods for the ``/loop-blocks`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def create(
        self,
        name: str,
        workflow_id: uuid.UUID | str,
        loop_type: str,
        loop_config: Any,
    ) -> CreateLoopBlockResponse:
        """Create a loop block task inside a workflow.

        Creates both the outer task (of type ``"loop_block"``) and an empty
        inner workflow that will be executed on each iteration.

        Args:
            name: Name shown on the loop block node and used as the inner
                workflow name.
            workflow_id: UUID of the outer workflow.
            loop_type: ``"count"``, ``"while"``, or ``"for_each"``.
            loop_config: Type-dependent configuration dict:

                - ``"count"``: ``{"count": N}``
                - ``"while"``: ``{"condition": "continue"}``
                - ``"for_each"``: ``{"collection": [...]}``

        Returns:
            :class:`~pyawe.models.CreateLoopBlockResponse` containing the new
            outer task and loop block record.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        return CreateLoopBlockResponse.from_dict(
            self._http.post(
                "/loop-blocks",
                json={
                    "name": name,
                    "workflow_id": _str_id(workflow_id),
                    "loop_type": loop_type,
                    "loop_config": loop_config,
                },
            )
        )

    def get(self, loop_block_id: uuid.UUID | str) -> LoopBlock:
        """Fetch a loop block.

        Args:
            loop_block_id: UUID of the loop block.

        Returns:
            :class:`~pyawe.models.LoopBlock`.

        Raises:
            AweNotFoundError: If the loop block does not exist.
            AweAuthError: If not authenticated.
        """
        return LoopBlock.from_dict(self._http.get(f"/loop-blocks/{_str_id(loop_block_id)}"))

    def update(
        self,
        loop_block_id: uuid.UUID | str,
        *,
        name: str | None = None,
        loop_type: str | None = None,
        loop_config: Any | None = None,
    ) -> LoopBlock:
        """Update a loop block; only supplied fields are changed.

        Renaming the loop block also renames the inner workflow.

        Args:
            loop_block_id: UUID of the loop block.
            name: New name.
            loop_type: New loop type.
            loop_config: New loop configuration.

        Returns:
            The updated :class:`~pyawe.models.LoopBlock`.

        Raises:
            AweNotFoundError: If the loop block does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact({"name": name, "loop_type": loop_type, "loop_config": loop_config})
        return LoopBlock.from_dict(
            self._http.put(f"/loop-blocks/{_str_id(loop_block_id)}", json=body)
        )

    def delete(self, loop_block_id: uuid.UUID | str) -> None:
        """Delete a loop block.

        Args:
            loop_block_id: UUID of the loop block.

        Raises:
            AweNotFoundError: If the loop block does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/loop-blocks/{_str_id(loop_block_id)}")


# ── projects ──────────────────────────────────────────────────────────────────


class ProjectsClient:
    """Methods for the ``/projects`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, team_id: uuid.UUID | str | None = None) -> builtins.list[Project]:
        """Return all visible projects, optionally filtered by team.

        Args:
            team_id: When supplied, returns only projects for this team.

        Returns:
            List of :class:`~pyawe.models.Project` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: dict[str, Any] = {}
        if team_id is not None:
            params["team_id"] = _str_id(team_id)
        return [Project.from_dict(p) for p in self._http.get("/projects", params=params)]

    def create(
        self,
        name: str,
        project_code: str,
        *,
        description: str | None = None,
        status: Status | str | None = None,
        team_id: uuid.UUID | str | None = None,
        project_manager_id: str | None = None,
    ) -> Project:
        """Create a new project.

        Args:
            name: Project name.
            project_code: Short unique code (1-8 letters/digits, must start
                with a letter), normalized to uppercase. Used as the prefix
                for this project's task/workflow references (e.g. ``"P1"``).
            description: Optional description.
            status: Initial status (default ``"Not Started"``).
            team_id: Assign to a team.
            project_manager_id: User ID of the project manager (defaults to creator).

        Returns:
            The newly created :class:`~pyawe.models.Project`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response, or if ``project_code`` is
                already taken.
        """
        body = _compact(
            {
                "name": name,
                "project_code": project_code,
                "description": description,
                "status": status,
                "team_id": _str_id(team_id),
                "project_manager_id": project_manager_id,
            }
        )
        return Project.from_dict(self._http.post("/projects", json=body))

    def get(self, project_id: uuid.UUID | str) -> ProjectWithJobs:
        """Fetch a project with its associated jobs.

        Args:
            project_id: UUID of the project.

        Returns:
            :class:`~pyawe.models.ProjectWithJobs`.

        Raises:
            AweNotFoundError: If the project does not exist.
            AweAuthError: If not authenticated.
        """
        return ProjectWithJobs.from_dict(self._http.get(f"/projects/{_str_id(project_id)}"))

    def update(
        self,
        project_id: uuid.UUID | str,
        *,
        name: str | None = None,
        description: str | None = None,
        status: Status | str | None = None,
        project_manager_id: str | None = None,
        project_code: str | None = None,
        archived: bool | None = None,
    ) -> Project:
        """Update a project; only supplied fields are changed.

        Args:
            project_id: UUID of the project to update.
            name: New name.
            description: New description.
            status: New status.
            project_manager_id: New project manager user ID.
            project_code: New project code.
            archived: Archive flag.

        Returns:
            The updated :class:`~pyawe.models.Project`.

        Raises:
            AweNotFoundError: If the project does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "description": description,
                "status": status,
                "project_manager_id": project_manager_id,
                "project_code": project_code,
                "archived": archived,
            }
        )
        return Project.from_dict(self._http.put(f"/projects/{_str_id(project_id)}", json=body))

    def delete(self, project_id: uuid.UUID | str) -> None:
        """Delete a project.

        Args:
            project_id: UUID of the project to delete.

        Raises:
            AweNotFoundError: If the project does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/projects/{_str_id(project_id)}")


# ── task state history ────────────────────────────────────────────────────────


class TaskHistoryClient:
    """Methods for task state transition history."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def get_task_history(
        self,
        task_id: uuid.UUID | str,
        *,
        actor_type: str | None = None,
        actor_id: str | None = None,
        from_status: str | None = None,
        to_status: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> builtins.list[TaskStateHistoryEntry]:
        """Return status transition history for a single task.

        Args:
            task_id: UUID of the task.
            actor_type: Filter by ``"user"``, ``"propagator"``, ``"automated"``, or ``"system"``.
            actor_id: Filter by actor user UUID.
            from_status: Only transitions from this status.
            to_status: Only transitions to this status.
            since: Only transitions on or after this timestamp.
            until: Only transitions before this timestamp.
            limit: Page size (default 100, max 1000).
            offset: Zero-based page offset.

        Returns:
            List of :class:`~pyawe.models.TaskStateHistoryEntry` objects, newest first.

        Raises:
            AweAuthError: If not authenticated.
        """
        params = _compact(
            {
                "actor_type": actor_type,
                "actor_id": actor_id,
                "from_status": from_status,
                "to_status": to_status,
                "since": since.isoformat() if since else None,
                "until": until.isoformat() if until else None,
                "limit": limit,
                "offset": offset,
            }
        )
        return [
            TaskStateHistoryEntry.from_dict(e)
            for e in self._http.get(f"/tasks/{_str_id(task_id)}/history", params=params)
        ]

    def get_job_task_history(
        self,
        job_id: uuid.UUID | str,
        *,
        task_id: uuid.UUID | str | None = None,
        actor_type: str | None = None,
        actor_id: str | None = None,
        from_status: str | None = None,
        to_status: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> builtins.list[TaskStateHistoryEntry]:
        """Return status transition history for all tasks in a job.

        Args:
            job_id: UUID of the job.
            task_id: Optionally filter to a specific task within the job.
            actor_type: Filter by actor type.
            actor_id: Filter by actor user UUID.
            from_status: Only transitions from this status.
            to_status: Only transitions to this status.
            since: Only transitions on or after this timestamp.
            until: Only transitions before this timestamp.
            limit: Page size (default 100, max 1000).
            offset: Zero-based page offset.

        Returns:
            List of :class:`~pyawe.models.TaskStateHistoryEntry` objects, newest first.

        Raises:
            AweAuthError: If not authenticated.
        """
        params = _compact(
            {
                "task_id": _str_id(task_id),
                "actor_type": actor_type,
                "actor_id": actor_id,
                "from_status": from_status,
                "to_status": to_status,
                "since": since.isoformat() if since else None,
                "until": until.isoformat() if until else None,
                "limit": limit,
                "offset": offset,
            }
        )
        return [
            TaskStateHistoryEntry.from_dict(e)
            for e in self._http.get(f"/jobs/{_str_id(job_id)}/task-history", params=params)
        ]

    def list(
        self,
        *,
        actor_type: str | None = None,
        actor_id: str | None = None,
        from_status: str | None = None,
        to_status: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> builtins.list[TaskStateHistoryEntry]:
        """Return the global task state transition feed (admin/ops use).

        Args:
            actor_type: Filter by actor type.
            actor_id: Filter by actor user UUID.
            from_status: Only transitions from this status.
            to_status: Only transitions to this status.
            since: Only transitions on or after this timestamp.
            until: Only transitions before this timestamp.
            limit: Page size (default 100, max 1000).
            offset: Zero-based page offset.

        Returns:
            List of :class:`~pyawe.models.TaskStateHistoryEntry` objects, newest first.

        Raises:
            AweAuthError: If not authenticated.
        """
        params = _compact(
            {
                "actor_type": actor_type,
                "actor_id": actor_id,
                "from_status": from_status,
                "to_status": to_status,
                "since": since.isoformat() if since else None,
                "until": until.isoformat() if until else None,
                "limit": limit,
                "offset": offset,
            }
        )
        return [
            TaskStateHistoryEntry.from_dict(e)
            for e in self._http.get("/task-history", params=params)
        ]


# ── connections ───────────────────────────────────────────────────────────────


class ConnectionsClient:
    """Methods for the ``/connections`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, team_id: uuid.UUID | str | None = None) -> builtins.list[Connection]:
        """Return all visible connections, optionally filtered by team.

        Args:
            team_id: When supplied, returns only connections for this team.

        Returns:
            List of :class:`~pyawe.models.Connection` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: dict[str, Any] = {}
        if team_id is not None:
            params["team_id"] = _str_id(team_id)
        return [Connection.from_dict(c) for c in self._http.get("/connections", params=params)]

    def create(
        self,
        name: str,
        connection_type: str,
        team_id: uuid.UUID | str,
        *,
        description: str | None = None,
        config: Any | None = None,
    ) -> Connection:
        """Create a new connection profile.

        Args:
            name: Human-readable name.
            connection_type: ``"bearer_token"``, ``"oauth2_client_credentials"``,
                ``"api_key_header"``, ``"basic_auth"``, ``"smtp"``, or ``"imap"``.
            team_id: Owning team.
            description: Optional description.
            config: Non-secret configuration (shape depends on *connection_type*).

        Returns:
            The newly created :class:`~pyawe.models.Connection`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "connection_type": connection_type,
                "team_id": _str_id(team_id),
                "description": description,
                "config": config,
            }
        )
        return Connection.from_dict(self._http.post("/connections", json=body))

    def get(self, connection_id: uuid.UUID | str) -> Connection:
        """Fetch a connection.

        Args:
            connection_id: UUID of the connection.

        Returns:
            :class:`~pyawe.models.Connection`.

        Raises:
            AweNotFoundError: If the connection does not exist.
            AweAuthError: If not authenticated.
        """
        return Connection.from_dict(self._http.get(f"/connections/{_str_id(connection_id)}"))

    def update(
        self,
        connection_id: uuid.UUID | str,
        *,
        name: str | None = None,
        description: str | None = None,
        config: Any | None = None,
    ) -> Connection:
        """Update a connection; only supplied fields are changed.

        Args:
            connection_id: UUID of the connection to update.
            name: New name.
            description: New description.
            config: New non-secret configuration.

        Returns:
            The updated :class:`~pyawe.models.Connection`.

        Raises:
            AweNotFoundError: If the connection does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact({"name": name, "description": description, "config": config})
        return Connection.from_dict(
            self._http.put(f"/connections/{_str_id(connection_id)}", json=body)
        )

    def delete(self, connection_id: uuid.UUID | str) -> None:
        """Delete a connection.

        Args:
            connection_id: UUID of the connection to delete.

        Raises:
            AweNotFoundError: If the connection does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/connections/{_str_id(connection_id)}")

    def patch_secret(self, connection_id: uuid.UUID | str, value: str | None) -> None:
        """Set or clear a connection's secret value.

        Args:
            connection_id: UUID of the connection.
            value: The secret value to store, or ``None`` to clear it.

        Raises:
            AweNotFoundError: If the connection does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.patch(f"/connections/{_str_id(connection_id)}/secret", json={"value": value})

    def test(self, connection_id: uuid.UUID | str) -> ConnectionTestResult:
        """Actively test that a saved connection's credentials work right now.

        Limited to ``"smtp"`` and ``"imap"`` connections. A failed test is a
        normal outcome (``success=False`` with a human-readable message), not
        an exception.

        Args:
            connection_id: UUID of the connection.

        Returns:
            :class:`~pyawe.models.ConnectionTestResult`.

        Raises:
            AweNotFoundError: If the connection does not exist.
            AweValidationError: If the connection type doesn't support testing,
                or has no secret set.
            AweAuthError: If not authenticated.
        """
        return ConnectionTestResult.from_dict(
            self._http.post(f"/connections/{_str_id(connection_id)}/test")
        )

    def test_config(self, connection_type: str, config: Any, secret: str) -> ConnectionTestResult:
        """Test ``"smtp"``/``"imap"`` credentials without a saved connection.

        Args:
            connection_type: ``"smtp"`` or ``"imap"``.
            config: Non-secret configuration to test.
            secret: The secret value to test.

        Returns:
            :class:`~pyawe.models.ConnectionTestResult`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        return ConnectionTestResult.from_dict(
            self._http.post(
                "/connections/test",
                json={
                    "connection_type": connection_type,
                    "config": config,
                    "secret": secret,
                },
            )
        )

    def list_mcp_tools(
        self, connection_id: uuid.UUID | str, mcp_server_url: str
    ) -> builtins.list[dict[str, Any]]:
        """List the tools available on an external MCP server via this connection.

        Args:
            connection_id: UUID of the connection to authenticate with.
            mcp_server_url: The MCP server's Streamable HTTP endpoint.

        Returns:
            List of raw tool summary dicts (name/description/schema).

        Raises:
            AweNotFoundError: If the connection does not exist.
            AweValidationError: If the connection has no secret set, or the
                MCP server call failed.
            AweAuthError: If not authenticated.
        """
        data = self._http.post(
            f"/connections/{_str_id(connection_id)}/mcp-tools",
            json={"mcp_server_url": mcp_server_url},
        )
        result: list[dict[str, Any]] = data.get("tools", [])
        return result

    def get_task_connection(self, task_id: uuid.UUID | str) -> ResolvedConnection:
        """Resolve the connection referenced by a task's ``mcp_tool`` script (service role only).

        Args:
            task_id: UUID of the task.

        Returns:
            :class:`~pyawe.models.ResolvedConnection` with the decrypted secret.

        Raises:
            AweNotFoundError: If the task doesn't exist, or has no connection configured.
            AweAuthError: If not authenticated.
            AweError: 403 if the caller does not hold the service role.
        """
        return ResolvedConnection.from_dict(self._http.get(f"/tasks/{_str_id(task_id)}/connection"))


# ── work items ────────────────────────────────────────────────────────────────


class WorkItemsClient:
    """Methods for the ``/work-items`` resource: standalone, reusable task templates."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self) -> builtins.list[WorkItem]:
        """Return all work items visible to the authenticated user.

        Returns:
            List of :class:`~pyawe.models.WorkItem` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [WorkItem.from_dict(w) for w in self._http.get("/work-items")]

    def create(
        self,
        name: str,
        *,
        description: str | None = None,
        task_type: str | None = None,
        effort: int | None = None,
        is_start: bool | None = None,
        is_end: bool | None = None,
        decision_input_port: str | None = None,
        is_locked: bool | None = None,
        assigned_to: str | None = None,
        team_id: uuid.UUID | str | None = None,
        is_shared: bool | None = None,
        port_namespace: str | None = None,
    ) -> WorkItem:
        """Create a new work item.

        Args:
            name: Work item name.
            description: Optional description.
            task_type: ``"standard"`` (default), ``"decision"``, or ``"automated"``.
            effort: Unitless effort estimate.
            is_start: Designate as a start-task template.
            is_end: Designate as an end-task template.
            decision_input_port: Input port name for auto-decide (decision work items).
            is_locked: Lock structural edits.
            assigned_to: Default assignee user ID.
            team_id: Owning team; omit for a private work item.
            is_shared: Visibility flag for team members (default ``False``).
            port_namespace: Checkpoint port namespace seeded onto every
                instantiated task (``^[a-z][a-z0-9_]*$``).

        Returns:
            The newly created :class:`~pyawe.models.WorkItem`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "description": description,
                "task_type": task_type,
                "effort": effort,
                "is_start": is_start,
                "is_end": is_end,
                "decision_input_port": decision_input_port,
                "is_locked": is_locked,
                "assigned_to": assigned_to,
                "team_id": _str_id(team_id),
                "is_shared": is_shared,
                "port_namespace": port_namespace,
            }
        )
        return WorkItem.from_dict(self._http.post("/work-items", json=body))

    def get(self, work_item_id: uuid.UUID | str) -> WorkItem:
        """Fetch a single work item.

        Args:
            work_item_id: UUID of the work item.

        Returns:
            :class:`~pyawe.models.WorkItem`.

        Raises:
            AweNotFoundError: If the work item does not exist.
            AweAuthError: If not authenticated.
        """
        return WorkItem.from_dict(self._http.get(f"/work-items/{_str_id(work_item_id)}"))

    def update(
        self,
        work_item_id: uuid.UUID | str,
        *,
        name: str | None = None,
        description: str | None = None,
        task_type: str | None = None,
        effort: Any = _UNSET,
        is_start: bool | None = None,
        is_end: bool | None = None,
        decision_input_port: Any = _UNSET,
        is_locked: bool | None = None,
        assigned_to: Any = _UNSET,
        team_id: Any = _UNSET,
        is_shared: bool | None = None,
        port_namespace: Any = _UNSET,
    ) -> WorkItem:
        """Update a work item; only supplied fields are changed.

        ``effort``, ``decision_input_port``, ``assigned_to``, ``team_id``, and
        ``port_namespace`` are tri-state fields: omit to leave unchanged,
        pass ``None`` to clear, or pass a value to set.

        Args:
            work_item_id: UUID of the work item to update.
            name: New name.
            description: New description.
            task_type: New task type.
            effort: Effort estimate, ``None`` to clear, or omit to leave unchanged.
            is_start: Start-task flag.
            is_end: End-task flag.
            decision_input_port: Input port name, ``None`` to clear, or omit
                to leave unchanged.
            is_locked: Lock flag.
            assigned_to: Default assignee, ``None`` to clear, or omit to leave unchanged.
            team_id: Owning team, ``None`` to make private, or omit to leave unchanged.
            is_shared: Visibility flag.
            port_namespace: Checkpoint port namespace, ``None`` to clear, or
                omit to leave unchanged.

        Returns:
            The updated :class:`~pyawe.models.WorkItem`.

        Raises:
            AweNotFoundError: If the work item does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "description": description,
                "task_type": task_type,
                "is_start": is_start,
                "is_end": is_end,
                "is_locked": is_locked,
                "is_shared": is_shared,
            }
        )
        if effort is not _UNSET:
            body["effort"] = effort
        if decision_input_port is not _UNSET:
            body["decision_input_port"] = decision_input_port
        if assigned_to is not _UNSET:
            body["assigned_to"] = assigned_to
        if team_id is not _UNSET:
            body["team_id"] = _str_id(team_id) if team_id is not None else None
        if port_namespace is not _UNSET:
            body["port_namespace"] = port_namespace
        return WorkItem.from_dict(self._http.put(f"/work-items/{_str_id(work_item_id)}", json=body))

    def delete(self, work_item_id: uuid.UUID | str) -> None:
        """Delete a work item.

        Args:
            work_item_id: UUID of the work item to delete.

        Raises:
            AweNotFoundError: If the work item does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/work-items/{_str_id(work_item_id)}")

    # ── ports ────────────────────────────────────────────────────────────────

    def list_ports(self, work_item_id: uuid.UUID | str) -> builtins.list[WorkItemPortSpec]:
        """Return all port specs for a work item.

        Args:
            work_item_id: UUID of the work item.

        Returns:
            List of :class:`~pyawe.models.WorkItemPortSpec` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            WorkItemPortSpec.from_dict(s)
            for s in self._http.get(f"/work-items/{_str_id(work_item_id)}/ports")
        ]

    def create_port(
        self,
        work_item_id: uuid.UUID | str,
        direction: str,
        name: str,
        value_type: str,
        *,
        required: bool | None = None,
        description: str | None = None,
        default_value: Any | None = None,
        sort_order: int | None = None,
    ) -> WorkItemPortSpec:
        """Add a port spec to a work item.

        Args:
            work_item_id: UUID of the work item.
            direction: ``"input"`` or ``"output"``.
            name: Port name.
            value_type: ``"string"``, ``"number"``, ``"boolean"``, ``"json"``,
                ``"file"``, ``"dam_asset"``, or ``"secret"``.
            required: Whether this input is required (default ``False``).
            description: Human-readable description.
            default_value: JSON default value.
            sort_order: Display order.

        Returns:
            The created :class:`~pyawe.models.WorkItemPortSpec`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "direction": direction,
                "name": name,
                "value_type": value_type,
                "required": required,
                "description": description,
                "default_value": default_value,
                "sort_order": sort_order,
            }
        )
        return WorkItemPortSpec.from_dict(
            self._http.post(f"/work-items/{_str_id(work_item_id)}/ports", json=body)
        )

    def update_port(
        self,
        work_item_id: uuid.UUID | str,
        port_id: uuid.UUID | str,
        *,
        name: str | None = None,
        value_type: str | None = None,
        required: bool | None = None,
        description: str | None = None,
        default_value: Any | None = None,
        sort_order: int | None = None,
    ) -> WorkItemPortSpec:
        """Update a work item port spec; only supplied fields are changed.

        Args:
            work_item_id: UUID of the work item.
            port_id: UUID of the port spec.
            name: New port name.
            value_type: New value type.
            required: Required flag.
            description: New description.
            default_value: New default value.
            sort_order: New sort order.

        Returns:
            The updated :class:`~pyawe.models.WorkItemPortSpec`.

        Raises:
            AweNotFoundError: If the port spec does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "value_type": value_type,
                "required": required,
                "description": description,
                "default_value": default_value,
                "sort_order": sort_order,
            }
        )
        return WorkItemPortSpec.from_dict(
            self._http.put(
                f"/work-items/{_str_id(work_item_id)}/ports/{_str_id(port_id)}", json=body
            )
        )

    def delete_port(self, work_item_id: uuid.UUID | str, port_id: uuid.UUID | str) -> None:
        """Delete a work item port spec.

        Args:
            work_item_id: UUID of the work item.
            port_id: UUID of the port spec.

        Raises:
            AweNotFoundError: If the port spec does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/work-items/{_str_id(work_item_id)}/ports/{_str_id(port_id)}")

    # ── script ───────────────────────────────────────────────────────────────

    def get_script(self, work_item_id: uuid.UUID | str) -> WorkItemScript:
        """Fetch the script attached to a work item.

        Args:
            work_item_id: UUID of the work item.

        Returns:
            :class:`~pyawe.models.WorkItemScript`.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        return WorkItemScript.from_dict(
            self._http.get(f"/work-items/{_str_id(work_item_id)}/script")
        )

    def upsert_script(
        self,
        work_item_id: uuid.UUID | str,
        *,
        script_type: str | None = None,
        endpoint: str | None = None,
        script_body: str | None = None,
        timeout_secs: int | None = None,
        retry_limit: int | None = None,
        execution_profile_id: uuid.UUID | str | None = None,
        connection_id: uuid.UUID | str | None = None,
    ) -> WorkItemScript:
        """Create or fully replace the script on a work item.

        Args:
            work_item_id: UUID of the work item.
            script_type: ``"webhook"`` (default), ``"shell"``, ``"python"``, or ``"mcp_tool"``.
            endpoint: Webhook URL.
            script_body: Script source.
            timeout_secs: Execution timeout in seconds.
            retry_limit: Maximum number of retry attempts.
            execution_profile_id: Execution profile for Kubernetes dispatch.
            connection_id: Connection profile to resolve auth from at run
                time; valid for ``"webhook"``/``"mcp_tool"`` only.

        Returns:
            The upserted :class:`~pyawe.models.WorkItemScript`.

        Raises:
            AweNotFoundError: If the work item does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "script_type": script_type,
                "endpoint": endpoint,
                "script_body": script_body,
                "timeout_secs": timeout_secs,
                "retry_limit": retry_limit,
                "execution_profile_id": _str_id(execution_profile_id),
                "connection_id": _str_id(connection_id),
            }
        )
        return WorkItemScript.from_dict(
            self._http.put(f"/work-items/{_str_id(work_item_id)}/script", json=body)
        )

    def delete_script(self, work_item_id: uuid.UUID | str) -> None:
        """Remove the script from a work item.

        Args:
            work_item_id: UUID of the work item.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/work-items/{_str_id(work_item_id)}/script")

    # ── checks ───────────────────────────────────────────────────────────────

    def list_checks(self, work_item_id: uuid.UUID | str) -> builtins.list[WorkItemCheck]:
        """Return all checkpoint check templates for a work item.

        Args:
            work_item_id: UUID of the work item.

        Returns:
            List of :class:`~pyawe.models.WorkItemCheck` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            WorkItemCheck.from_dict(c)
            for c in self._http.get(f"/work-items/{_str_id(work_item_id)}/checks")
        ]

    def create_check(
        self,
        work_item_id: uuid.UUID | str,
        name: str,
        check_type: str,
        *,
        description: str | None = None,
        required: bool | None = None,
        sort_order: int | None = None,
        related_port_names: Any | None = None,
        assigned_to: str | None = None,
    ) -> WorkItemCheck:
        """Add a checkpoint check template to a work item.

        Args:
            work_item_id: UUID of the work item.
            name: Check name.
            check_type: ``"manual"`` or ``"script"``.
            description: Optional description.
            required: Default ``True``.
            sort_order: Display order.
            related_port_names: Cosmetic list of related port names.
            assigned_to: Default assignee user ID for manual checks.

        Returns:
            The created :class:`~pyawe.models.WorkItemCheck`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "check_type": check_type,
                "description": description,
                "required": required,
                "sort_order": sort_order,
                "related_port_names": related_port_names,
                "assigned_to": assigned_to,
            }
        )
        return WorkItemCheck.from_dict(
            self._http.post(f"/work-items/{_str_id(work_item_id)}/checks", json=body)
        )

    def update_check(
        self,
        work_item_id: uuid.UUID | str,
        check_id: uuid.UUID | str,
        *,
        name: str | None = None,
        description: str | None = None,
        required: bool | None = None,
        sort_order: int | None = None,
        related_port_names: Any | None = None,
        assigned_to: str | None = None,
    ) -> WorkItemCheck:
        """Update a work item check template; only supplied fields are changed.

        Args:
            work_item_id: UUID of the work item.
            check_id: UUID of the check.
            name: New name.
            description: New description.
            required: Required flag.
            sort_order: New sort order.
            related_port_names: New related port names.
            assigned_to: New default assignee.

        Returns:
            The updated :class:`~pyawe.models.WorkItemCheck`.

        Raises:
            AweNotFoundError: If the check does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "description": description,
                "required": required,
                "sort_order": sort_order,
                "related_port_names": related_port_names,
                "assigned_to": assigned_to,
            }
        )
        return WorkItemCheck.from_dict(
            self._http.put(
                f"/work-items/{_str_id(work_item_id)}/checks/{_str_id(check_id)}", json=body
            )
        )

    def delete_check(self, work_item_id: uuid.UUID | str, check_id: uuid.UUID | str) -> None:
        """Delete a work item check template.

        Args:
            work_item_id: UUID of the work item.
            check_id: UUID of the check.

        Raises:
            AweNotFoundError: If the check does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/work-items/{_str_id(work_item_id)}/checks/{_str_id(check_id)}")

    def get_check_script(
        self, work_item_id: uuid.UUID | str, check_id: uuid.UUID | str
    ) -> WorkItemCheckScript:
        """Fetch the script attached to a work item check template.

        Args:
            work_item_id: UUID of the work item.
            check_id: UUID of the check.

        Returns:
            :class:`~pyawe.models.WorkItemCheckScript`.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        return WorkItemCheckScript.from_dict(
            self._http.get(f"/work-items/{_str_id(work_item_id)}/checks/{_str_id(check_id)}/script")
        )

    def upsert_check_script(
        self,
        work_item_id: uuid.UUID | str,
        check_id: uuid.UUID | str,
        *,
        script_type: str | None = None,
        endpoint: str | None = None,
        script_body: str | None = None,
        timeout_secs: int | None = None,
        retry_limit: int | None = None,
        execution_profile_id: uuid.UUID | str | None = None,
        connection_id: uuid.UUID | str | None = None,
        locked_on_clone: bool | None = None,
    ) -> WorkItemCheckScript:
        """Create or fully replace the script on a work item check template.

        Args:
            work_item_id: UUID of the work item.
            check_id: UUID of the check.
            script_type: ``"webhook"`` (default), ``"shell"``, ``"python"``, or ``"mcp_tool"``.
            endpoint: Webhook URL.
            script_body: Script source.
            timeout_secs: Execution timeout in seconds.
            retry_limit: Maximum number of retry attempts.
            execution_profile_id: Execution profile for Kubernetes dispatch.
            connection_id: Connection profile to resolve auth from at run time.
            locked_on_clone: Prevent edits/removal of clones made onto a real task.

        Returns:
            The upserted :class:`~pyawe.models.WorkItemCheckScript`.

        Raises:
            AweNotFoundError: If the check does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "script_type": script_type,
                "endpoint": endpoint,
                "script_body": script_body,
                "timeout_secs": timeout_secs,
                "retry_limit": retry_limit,
                "execution_profile_id": _str_id(execution_profile_id),
                "connection_id": _str_id(connection_id),
                "locked_on_clone": locked_on_clone,
            }
        )
        return WorkItemCheckScript.from_dict(
            self._http.put(
                f"/work-items/{_str_id(work_item_id)}/checks/{_str_id(check_id)}/script",
                json=body,
            )
        )

    def delete_check_script(self, work_item_id: uuid.UUID | str, check_id: uuid.UUID | str) -> None:
        """Remove the script from a work item check template.

        Args:
            work_item_id: UUID of the work item.
            check_id: UUID of the check.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/work-items/{_str_id(work_item_id)}/checks/{_str_id(check_id)}/script")

    # ── team roles ───────────────────────────────────────────────────────────

    def list_team_roles(self, work_item_id: uuid.UUID | str) -> builtins.list[WorkItemTeamRole]:
        """Return all team-role assignments for a work item.

        Args:
            work_item_id: UUID of the work item.

        Returns:
            List of :class:`~pyawe.models.WorkItemTeamRole` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            WorkItemTeamRole.from_dict(r)
            for r in self._http.get(f"/work-items/{_str_id(work_item_id)}/team-roles")
        ]

    def assign_team_role(
        self, work_item_id: uuid.UUID | str, team_role_id: uuid.UUID | str
    ) -> WorkItemTeamRole:
        """Assign a team role to a work item.

        Args:
            work_item_id: UUID of the work item.
            team_role_id: UUID of the team role.

        Returns:
            The created :class:`~pyawe.models.WorkItemTeamRole`.

        Raises:
            AweNotFoundError: If the work item does not exist.
            AweAuthError: If not authenticated.
        """
        return WorkItemTeamRole.from_dict(
            self._http.post(
                f"/work-items/{_str_id(work_item_id)}/team-roles",
                json={"team_role_id": _str_id(team_role_id)},
            )
        )

    def remove_team_role(
        self, work_item_id: uuid.UUID | str, team_role_id: uuid.UUID | str
    ) -> None:
        """Remove a team-role assignment from a work item.

        Args:
            work_item_id: UUID of the work item.
            team_role_id: UUID of the team role assignment to remove.

        Raises:
            AweNotFoundError: If the assignment does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/work-items/{_str_id(work_item_id)}/team-roles/{_str_id(team_role_id)}")

    # ── instantiate / branches ───────────────────────────────────────────────

    def instantiate(
        self,
        work_item_id: uuid.UUID | str,
        workflow_id: uuid.UUID | str,
        *,
        canvas_x: float | None = None,
        canvas_y: float | None = None,
    ) -> InstantiateWorkItemResponse:
        """Place a copy of a work item as a new task inside a workflow.

        Args:
            work_item_id: UUID of the work item to instantiate.
            workflow_id: UUID of the target workflow.
            canvas_x: Optional canvas position for the primary task.
            canvas_y: Optional canvas position for the primary task.

        Returns:
            :class:`~pyawe.models.InstantiateWorkItemResponse` with the
            primary task and, for decision work items, its branch tasks.

        Raises:
            AweNotFoundError: If the work item or workflow does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "workflow_id": _str_id(workflow_id),
                "canvas_x": canvas_x,
                "canvas_y": canvas_y,
            }
        )
        return InstantiateWorkItemResponse.from_dict(
            self._http.post(f"/work-items/{_str_id(work_item_id)}/instantiate", json=body)
        )

    def list_branches(self, work_item_id: uuid.UUID | str) -> builtins.list[WorkItemBranch]:
        """Return all branches defined on a decision work item.

        Args:
            work_item_id: UUID of the work item.

        Returns:
            List of :class:`~pyawe.models.WorkItemBranch` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            WorkItemBranch.from_dict(b)
            for b in self._http.get(f"/work-items/{_str_id(work_item_id)}/branches")
        ]

    def create_branch(
        self,
        work_item_id: uuid.UUID | str,
        label: str,
        task_name: str,
        *,
        sort_order: int | None = None,
    ) -> WorkItemBranch:
        """Add a branch to a decision work item.

        Args:
            work_item_id: UUID of the work item.
            label: Branch label.
            task_name: Name given to the task created for this branch on instantiation.
            sort_order: Display order.

        Returns:
            The created :class:`~pyawe.models.WorkItemBranch`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact({"label": label, "task_name": task_name, "sort_order": sort_order})
        return WorkItemBranch.from_dict(
            self._http.post(f"/work-items/{_str_id(work_item_id)}/branches", json=body)
        )

    def update_branch(
        self,
        work_item_id: uuid.UUID | str,
        branch_id: uuid.UUID | str,
        *,
        label: str | None = None,
        task_name: str | None = None,
        sort_order: int | None = None,
    ) -> WorkItemBranch:
        """Update a work item branch; only supplied fields are changed.

        Args:
            work_item_id: UUID of the work item.
            branch_id: UUID of the branch.
            label: New label.
            task_name: New task name.
            sort_order: New sort order.

        Returns:
            The updated :class:`~pyawe.models.WorkItemBranch`.

        Raises:
            AweNotFoundError: If the branch does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact({"label": label, "task_name": task_name, "sort_order": sort_order})
        return WorkItemBranch.from_dict(
            self._http.put(
                f"/work-items/{_str_id(work_item_id)}/branches/{_str_id(branch_id)}", json=body
            )
        )

    def delete_branch(self, work_item_id: uuid.UUID | str, branch_id: uuid.UUID | str) -> None:
        """Delete a branch from a decision work item.

        Args:
            work_item_id: UUID of the work item.
            branch_id: UUID of the branch.

        Raises:
            AweNotFoundError: If the branch does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/work-items/{_str_id(work_item_id)}/branches/{_str_id(branch_id)}")


# ── checkpoint checks ────────────────────────────────────────────────────────


class CheckpointChecksClient:
    """Methods for checkpoint check management (``/tasks/{id}/checks``, etc.)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, task_id: uuid.UUID | str) -> builtins.list[CheckpointCheck]:
        """Return all checks gating a checkpoint task.

        Args:
            task_id: UUID of the checkpoint task.

        Returns:
            List of :class:`~pyawe.models.CheckpointCheck` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            CheckpointCheck.from_dict(c)
            for c in self._http.get(f"/tasks/{_str_id(task_id)}/checks")
        ]

    def create(
        self,
        task_id: uuid.UUID | str,
        name: str,
        check_type: str,
        *,
        description: str | None = None,
        required: bool | None = None,
        sort_order: int | None = None,
        related_port_names: Any | None = None,
        assigned_to: str | None = None,
    ) -> CheckpointCheck:
        """Add a check to a checkpoint task.

        Args:
            task_id: UUID of the checkpoint task.
            name: Check name.
            check_type: ``"manual"`` or ``"script"``.
            description: Optional description.
            required: Default ``True``.
            sort_order: Display order.
            related_port_names: Cosmetic list of related port names.
            assigned_to: User id responsible for a manual check.

        Returns:
            The created :class:`~pyawe.models.CheckpointCheck`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "check_type": check_type,
                "description": description,
                "required": required,
                "sort_order": sort_order,
                "related_port_names": related_port_names,
                "assigned_to": assigned_to,
            }
        )
        return CheckpointCheck.from_dict(
            self._http.post(f"/tasks/{_str_id(task_id)}/checks", json=body)
        )

    def update(
        self,
        task_id: uuid.UUID | str,
        check_id: uuid.UUID | str,
        *,
        name: str | None = None,
        description: str | None = None,
        required: bool | None = None,
        sort_order: int | None = None,
        related_port_names: Any | None = None,
        assigned_to: str | None = None,
    ) -> CheckpointCheck:
        """Update a checkpoint check; only supplied fields are changed.

        Args:
            task_id: UUID of the checkpoint task.
            check_id: UUID of the check.
            name: New name.
            description: New description.
            required: Required flag.
            sort_order: New sort order.
            related_port_names: New related port names.
            assigned_to: New assignee.

        Returns:
            The updated :class:`~pyawe.models.CheckpointCheck`.

        Raises:
            AweNotFoundError: If the check does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "description": description,
                "required": required,
                "sort_order": sort_order,
                "related_port_names": related_port_names,
                "assigned_to": assigned_to,
            }
        )
        return CheckpointCheck.from_dict(
            self._http.put(f"/tasks/{_str_id(task_id)}/checks/{_str_id(check_id)}", json=body)
        )

    def delete(self, task_id: uuid.UUID | str, check_id: uuid.UUID | str) -> None:
        """Delete a checkpoint check.

        Args:
            task_id: UUID of the checkpoint task.
            check_id: UUID of the check.

        Raises:
            AweNotFoundError: If the check does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/tasks/{_str_id(task_id)}/checks/{_str_id(check_id)}")

    def list_passthrough(self, workflow_id: uuid.UUID | str) -> PassthroughCheckpoints:
        """Return task IDs in a workflow that have a passthrough checkpoint check.

        Args:
            workflow_id: UUID of the workflow.

        Returns:
            :class:`~pyawe.models.PassthroughCheckpoints`.

        Raises:
            AweAuthError: If not authenticated.
        """
        return PassthroughCheckpoints.from_dict(
            self._http.get(f"/workflows/{_str_id(workflow_id)}/passthrough-checkpoints")
        )

    def get_script(
        self, task_id: uuid.UUID | str, check_id: uuid.UUID | str
    ) -> CheckpointCheckScript:
        """Fetch the script attached to a checkpoint check.

        Args:
            task_id: UUID of the checkpoint task.
            check_id: UUID of the check.

        Returns:
            :class:`~pyawe.models.CheckpointCheckScript`.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        return CheckpointCheckScript.from_dict(
            self._http.get(f"/tasks/{_str_id(task_id)}/checks/{_str_id(check_id)}/script")
        )

    def upsert_script(
        self,
        task_id: uuid.UUID | str,
        check_id: uuid.UUID | str,
        *,
        script_type: str | None = None,
        endpoint: str | None = None,
        script_body: str | None = None,
        timeout_secs: int | None = None,
        retry_limit: int | None = None,
        execution_profile_id: uuid.UUID | str | None = None,
        connection_id: uuid.UUID | str | None = None,
        locked_on_clone: bool | None = None,
    ) -> CheckpointCheckScript:
        """Create or fully replace the script on a checkpoint check.

        Args:
            task_id: UUID of the checkpoint task.
            check_id: UUID of the check.
            script_type: ``"webhook"`` (default), ``"shell"``, ``"python"``, or ``"mcp_tool"``.
            endpoint: Webhook URL.
            script_body: Script source.
            timeout_secs: Execution timeout in seconds.
            retry_limit: Maximum number of retry attempts.
            execution_profile_id: Execution profile for Kubernetes dispatch.
            connection_id: Connection profile to resolve auth from at run time.
            locked_on_clone: Prevent edits/removal once cloned onto a
                non-template task.

        Returns:
            The upserted :class:`~pyawe.models.CheckpointCheckScript`.

        Raises:
            AweNotFoundError: If the check does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "script_type": script_type,
                "endpoint": endpoint,
                "script_body": script_body,
                "timeout_secs": timeout_secs,
                "retry_limit": retry_limit,
                "execution_profile_id": _str_id(execution_profile_id),
                "connection_id": _str_id(connection_id),
                "locked_on_clone": locked_on_clone,
            }
        )
        return CheckpointCheckScript.from_dict(
            self._http.put(
                f"/tasks/{_str_id(task_id)}/checks/{_str_id(check_id)}/script", json=body
            )
        )

    def delete_script(self, task_id: uuid.UUID | str, check_id: uuid.UUID | str) -> None:
        """Remove the script from a checkpoint check.

        Args:
            task_id: UUID of the checkpoint task.
            check_id: UUID of the check.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/tasks/{_str_id(task_id)}/checks/{_str_id(check_id)}/script")

    def verify(
        self,
        task_id: uuid.UUID | str,
        check_id: uuid.UUID | str,
        passed: bool,
        *,
        note: str | None = None,
    ) -> CheckpointCheck:
        """Manually verify a ``"manual"``-type checkpoint check.

        Args:
            task_id: UUID of the checkpoint task.
            check_id: UUID of the check.
            passed: Whether the check passed.
            note: Optional note.

        Returns:
            The updated :class:`~pyawe.models.CheckpointCheck`.

        Raises:
            AweNotFoundError: If the check does not exist.
            AweValidationError: If the check is not a ``"manual"`` check, or
                the task is not in progress.
            AweAuthError: If not authenticated.
        """
        body = _compact({"passed": passed, "note": note})
        return CheckpointCheck.from_dict(
            self._http.post(
                f"/tasks/{_str_id(task_id)}/checks/{_str_id(check_id)}/verify", json=body
            )
        )

    def run(self, task_id: uuid.UUID | str, check_id: uuid.UUID | str) -> CheckpointCheckRun:
        """Run a ``"script"``-type checkpoint check.

        Args:
            task_id: UUID of the checkpoint task.
            check_id: UUID of the check.

        Returns:
            The new :class:`~pyawe.models.CheckpointCheckRun`.

        Raises:
            AweNotFoundError: If the check does not exist.
            AweValidationError: If the task is not in progress.
            AweAuthError: If not authenticated.
        """
        return CheckpointCheckRun.from_dict(
            self._http.post(f"/tasks/{_str_id(task_id)}/checks/{_str_id(check_id)}/run")
        )

    def list_runs(
        self, task_id: uuid.UUID | str, check_id: uuid.UUID | str
    ) -> builtins.list[CheckpointCheckRun]:
        """Return all execution run records for a checkpoint check.

        Args:
            task_id: UUID of the checkpoint task.
            check_id: UUID of the check.

        Returns:
            List of :class:`~pyawe.models.CheckpointCheckRun` objects, newest first.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            CheckpointCheckRun.from_dict(r)
            for r in self._http.get(f"/tasks/{_str_id(task_id)}/checks/{_str_id(check_id)}/runs")
        ]


# ── scheduled scripts ────────────────────────────────────────────────────────


class ScheduledScriptsClient:
    """Methods for the ``/scheduled-scripts`` resource: cron-scheduled, task-independent scripts."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, team_id: uuid.UUID | str | None = None) -> builtins.list[ScheduledScript]:
        """Return all scheduled scripts, optionally filtered by team.

        Args:
            team_id: When supplied, returns only scripts for this team.

        Returns:
            List of :class:`~pyawe.models.ScheduledScript` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: dict[str, Any] = {}
        if team_id is not None:
            params["team_id"] = _str_id(team_id)
        return [
            ScheduledScript.from_dict(s)
            for s in self._http.get("/scheduled-scripts", params=params)
        ]

    def create(
        self,
        name: str,
        team_id: uuid.UUID | str,
        cron_expression: str,
        *,
        description: str | None = None,
        is_active: bool | None = None,
        script_type: str | None = None,
        endpoint: str | None = None,
        script_body: str | None = None,
        timeout_secs: int | None = None,
        execution_profile_id: uuid.UUID | str | None = None,
        connection_id: uuid.UUID | str | None = None,
    ) -> ScheduledScript:
        """Create a new scheduled script.

        Args:
            name: Script name.
            team_id: Owning team.
            cron_expression: Standard 5-field cron expression, evaluated in UTC.
            description: Optional description.
            is_active: Whether the schedule is claimed by the relay (default ``True``).
            script_type: ``"webhook"`` (default), ``"shell"``, ``"python"``,
                ``"mcp_tool"``, or ``"email"``.
            endpoint: Webhook URL; required for ``"webhook"``.
            script_body: Script source; required for ``"shell"``, ``"python"``,
                and ``"mcp_tool"``. For ``"email"``, required as JSON
                ``{"to": "...", "subject": "...", "body_text": "..."}``.
            timeout_secs: Execution timeout in seconds.
            execution_profile_id: Execution profile for Kubernetes dispatch.
            connection_id: Connection profile; required (must reference an
                ``smtp`` connection) when ``script_type == "email"``.

        Returns:
            The newly created :class:`~pyawe.models.ScheduledScript`.

        Raises:
            AweAuthError: If not authenticated.
            AweValidationError: On a 400 response.
        """
        body = _compact(
            {
                "name": name,
                "team_id": _str_id(team_id),
                "cron_expression": cron_expression,
                "description": description,
                "is_active": is_active,
                "script_type": script_type,
                "endpoint": endpoint,
                "script_body": script_body,
                "timeout_secs": timeout_secs,
                "execution_profile_id": _str_id(execution_profile_id),
                "connection_id": _str_id(connection_id),
            }
        )
        return ScheduledScript.from_dict(self._http.post("/scheduled-scripts", json=body))

    def get(self, schedule_id: uuid.UUID | str) -> ScheduledScript:
        """Fetch a scheduled script.

        Args:
            schedule_id: UUID of the scheduled script.

        Returns:
            :class:`~pyawe.models.ScheduledScript`.

        Raises:
            AweNotFoundError: If the scheduled script does not exist.
            AweAuthError: If not authenticated.
        """
        return ScheduledScript.from_dict(
            self._http.get(f"/scheduled-scripts/{_str_id(schedule_id)}")
        )

    def update(
        self,
        schedule_id: uuid.UUID | str,
        *,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
        cron_expression: str | None = None,
        script_type: str | None = None,
        endpoint: str | None = None,
        script_body: str | None = None,
        timeout_secs: int | None = None,
        execution_profile_id: uuid.UUID | str | None = None,
        connection_id: uuid.UUID | str | None = None,
    ) -> ScheduledScript:
        """Update a scheduled script; only supplied fields are changed.

        Args:
            schedule_id: UUID of the scheduled script to update.
            name: New name.
            description: New description.
            is_active: Active flag; ``False`` pauses without losing history.
            cron_expression: New cron expression.
            script_type: New script type.
            endpoint: New webhook URL.
            script_body: New script source.
            timeout_secs: New timeout.
            execution_profile_id: New execution profile.
            connection_id: New connection profile.

        Returns:
            The updated :class:`~pyawe.models.ScheduledScript`.

        Raises:
            AweNotFoundError: If the scheduled script does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "name": name,
                "description": description,
                "is_active": is_active,
                "cron_expression": cron_expression,
                "script_type": script_type,
                "endpoint": endpoint,
                "script_body": script_body,
                "timeout_secs": timeout_secs,
                "execution_profile_id": _str_id(execution_profile_id),
                "connection_id": _str_id(connection_id),
            }
        )
        return ScheduledScript.from_dict(
            self._http.put(f"/scheduled-scripts/{_str_id(schedule_id)}", json=body)
        )

    def delete(self, schedule_id: uuid.UUID | str) -> None:
        """Delete a scheduled script.

        Args:
            schedule_id: UUID of the scheduled script to delete.

        Raises:
            AweNotFoundError: If the scheduled script does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/scheduled-scripts/{_str_id(schedule_id)}")

    def trigger(self, schedule_id: uuid.UUID | str) -> None:
        """Manually enqueue an immediate run of a scheduled script.

        Args:
            schedule_id: UUID of the scheduled script.

        Raises:
            AweNotFoundError: If the scheduled script does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.post(f"/scheduled-scripts/{_str_id(schedule_id)}/trigger")

    def get_dispatch(self, schedule_id: uuid.UUID | str) -> ScheduledScriptDispatch:
        """Fetch everything ``awe_runner`` needs to execute a scheduled script (service role only).

        Args:
            schedule_id: UUID of the scheduled script.

        Returns:
            :class:`~pyawe.models.ScheduledScriptDispatch`.

        Raises:
            AweNotFoundError: If the scheduled script does not exist.
            AweAuthError: If not authenticated.
        """
        return ScheduledScriptDispatch.from_dict(
            self._http.get(f"/scheduled-scripts/{_str_id(schedule_id)}/dispatch")
        )

    def list_runs(self, schedule_id: uuid.UUID | str) -> builtins.list[ScheduledScriptRun]:
        """Return all run records for a scheduled script.

        Args:
            schedule_id: UUID of the scheduled script.

        Returns:
            List of :class:`~pyawe.models.ScheduledScriptRun` objects, newest first.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            ScheduledScriptRun.from_dict(r)
            for r in self._http.get(f"/scheduled-scripts/{_str_id(schedule_id)}/runs")
        ]

    def report_run(
        self,
        schedule_id: uuid.UUID | str,
        triggered_by: str,
        status: str,
        *,
        runner_id: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        message: str | None = None,
        error_message: str | None = None,
        state: Any | None = None,
    ) -> ScheduledScriptRun:
        """Report a scheduled script run's outcome (runner use).

        Args:
            schedule_id: UUID of the scheduled script.
            triggered_by: ``"schedule"`` (fired by cron) or ``"manual"``.
            status: ``"Success"``, ``"Failure"``, or ``"Timeout"``.
            runner_id: Identifier of the runner that executed the script.
            started_at: When execution began.
            completed_at: When execution ended (or timed out).
            message: Optional human-readable outcome message.
            error_message: Error details when ``status != "Success"``.
            state: The script's emitted state, merged onto the schedule's stored state.

        Returns:
            The recorded :class:`~pyawe.models.ScheduledScriptRun`.

        Raises:
            AweNotFoundError: If the scheduled script does not exist.
            AweAuthError: If not authenticated.
        """
        body = _compact(
            {
                "triggered_by": triggered_by,
                "status": status,
                "runner_id": runner_id,
                "started_at": started_at.isoformat() if started_at else None,
                "completed_at": completed_at.isoformat() if completed_at else None,
                "message": message,
                "error_message": error_message,
                "state": state,
            }
        )
        return ScheduledScriptRun.from_dict(
            self._http.post(f"/scheduled-scripts/{_str_id(schedule_id)}/runs", json=body)
        )


# ── AI chat sessions ─────────────────────────────────────────────────────────


class AiChatSessionsClient:
    """Methods for the ``/ai-sessions`` resource: the authenticated user's own AI chat history."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self) -> builtins.list[ChatSession]:
        """Return all chat sessions for the authenticated user, newest first.

        Returns:
            List of :class:`~pyawe.models.ChatSession` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [ChatSession.from_dict(s) for s in self._http.get("/ai-sessions")]

    def create(self, title: str | None = None) -> ChatSession:
        """Create a new chat session for the authenticated user.

        Args:
            title: Session title (default ``"New chat"``).

        Returns:
            The newly created :class:`~pyawe.models.ChatSession`.

        Raises:
            AweAuthError: If not authenticated.
        """
        body = _compact({"title": title})
        return ChatSession.from_dict(self._http.post("/ai-sessions", json=body))

    def delete(self, session_id: uuid.UUID | str) -> None:
        """Delete a chat session and its messages.

        Args:
            session_id: UUID of the session to delete.

        Raises:
            AweNotFoundError: If the session does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/ai-sessions/{_str_id(session_id)}")

    def list_messages(self, session_id: uuid.UUID | str) -> builtins.list[ChatMessage]:
        """Return all messages in a session, oldest first.

        Args:
            session_id: UUID of the session.

        Returns:
            List of :class:`~pyawe.models.ChatMessage` objects.

        Raises:
            AweNotFoundError: If the session does not exist.
            AweAuthError: If not authenticated.
        """
        return [
            ChatMessage.from_dict(m)
            for m in self._http.get(f"/ai-sessions/{_str_id(session_id)}/messages")
        ]

    def append_message(self, session_id: uuid.UUID | str, role: str, content: str) -> ChatMessage:
        """Append a message to a chat session.

        Args:
            session_id: UUID of the session.
            role: Message role, e.g. ``"user"`` or ``"assistant"``.
            content: Message text.

        Returns:
            The created :class:`~pyawe.models.ChatMessage`.

        Raises:
            AweNotFoundError: If the session does not exist.
            AweAuthError: If not authenticated.
        """
        return ChatMessage.from_dict(
            self._http.post(
                f"/ai-sessions/{_str_id(session_id)}/messages",
                json={"role": role, "content": content},
            )
        )


# ── top-level client ──────────────────────────────────────────────────────────


class AweClient:
    """Client for the AWE (Advanced Workflow Engine) REST API.

    Authentication is handled by the ``ullav-user-management`` service
    (separate from the AWE server). Call :meth:`login` before making any
    API requests; a :exc:`~pyawe.exceptions.AweAuthError` will be raised
    otherwise.

    The JWT is stored in the session and attached to every subsequent
    request automatically. Tokens expire according to the server's
    configuration; call :meth:`login` again to refresh.

    Args:
        api_url: Base URL of the AWE server, e.g. ``"https://awe.example.com"``.
        auth_url: Base URL of the authentication service. When auth and AWE share
            the same DNS record / reverse-proxy host, omit this argument and
            ``api_url`` is used for both. Only needed when the auth service is
            on a separate host.

    Example:
        .. code-block:: python

            from pyawe import AweClient

            # Production: single DNS record, auth served at the same origin
            client = AweClient("https://awe.example.com")
            client.login(email="user@example.com", password="secret")

            # Development: separate ports for AWE and auth services
            client = AweClient(
                api_url="http://localhost:8080",
                auth_url="http://localhost:8081",
            )
            client.login(email="user@example.com", password="secret")

            # Workflows
            wfs = client.workflows.list()
            wf = client.workflows.create("My Workflow")

            # Tasks
            task = client.tasks.create("Review", workflow_id=wf.id)
            client.tasks.update(task.id, status="In Progress")

            # Jobs
            job = client.jobs.create("Q1 Campaign")
    """

    def __init__(self, api_url: str, auth_url: str | None = None) -> None:
        self._http = _HttpSession(api_url, auth_url or api_url)
        self.workflows = WorkflowsClient(self._http)
        self.tasks = TasksClient(self._http)
        self.task_links = TaskLinksClient(self._http)
        self.task_ports = TaskPortsClient(self._http)
        self.task_scripts = TaskScriptsClient(self._http)
        self.task_secrets = TaskSecretsClient(self._http)
        self.task_runs = TaskRunsClient(self._http)
        self.task_team_roles = TaskTeamRolesClient(self._http)
        self.jobs = JobsClient(self._http)
        self.projects = ProjectsClient(self._http)
        self.execution_profiles = ExecutionProfilesClient(self._http)
        self.loop_blocks = LoopBlocksClient(self._http)
        self.task_history = TaskHistoryClient(self._http)
        self.connections = ConnectionsClient(self._http)
        self.work_items = WorkItemsClient(self._http)
        self.checkpoint_checks = CheckpointChecksClient(self._http)
        self.scheduled_scripts = ScheduledScriptsClient(self._http)
        self.ai_chat_sessions = AiChatSessionsClient(self._http)

    def login(self, email: str, password: str) -> LoginInfo:
        """Authenticate and store the JWT for subsequent requests.

        Args:
            email: User email address.
            password: User password.

        Returns:
            :class:`~pyawe.models.LoginInfo` containing the token, user
            details, roles, and permissions.

        Raises:
            AweAuthError: If the credentials are invalid.
        """
        data = self._http.post_auth("/auth/login", {"email": email, "password": password})
        info = LoginInfo.from_dict(data)
        self._http.set_token(info.token)
        return info
