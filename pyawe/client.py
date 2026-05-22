"""AweClient and resource sub-clients for the AWE API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ._http import _HttpSession, _compact, _str_id
from .exceptions import AweAuthError
from .models import (
    CreateLoopBlockResponse,
    DataBinding,
    ExecutionProfile,
    Job,
    JobWithWorkflows,
    LoginInfo,
    LoopBlock,
    Note,
    NoteFolder,
    ScheduleStatus,
    Status,
    Task,
    TaskType,
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

# Sentinel used to distinguish "not provided" from ``None`` for the tri-state
# ``assigned_to`` field on task updates.
_UNSET: Any = object()


# ── workflows ─────────────────────────────────────────────────────────────────


class WorkflowsClient:
    """Methods for the ``/workflows`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, team_id: Optional[Union[uuid.UUID, str]] = None) -> List[Workflow]:
        """Return all visible workflows, optionally filtered by team.

        Args:
            team_id: When supplied, returns only workflows for this team.

        Returns:
            List of :class:`~pyawe.models.Workflow` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: Dict[str, Any] = {}
        if team_id is not None:
            params["team_id"] = _str_id(team_id)
        return [Workflow.from_dict(w) for w in self._http.get("/workflows", params=params)]

    def create(
        self,
        name: str,
        *,
        is_template: Optional[bool] = None,
        description: Optional[str] = None,
        status: Optional[Union[Status, str]] = None,
        schedule_status: Optional[Union[ScheduleStatus, str]] = None,
        job_id: Optional[Union[uuid.UUID, str]] = None,
        team_id: Optional[Union[uuid.UUID, str]] = None,
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
            }
        )
        return Workflow.from_dict(self._http.post("/workflows", json=body))

    def get(self, workflow_id: Union[uuid.UUID, str]) -> WorkflowWithTasks:
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
        workflow_id: Union[uuid.UUID, str],
        *,
        name: Optional[str] = None,
        is_template: Optional[bool] = None,
        description: Optional[str] = None,
        status: Optional[Union[Status, str]] = None,
        schedule_status: Optional[Union[ScheduleStatus, str]] = None,
        job_id: Optional[Union[uuid.UUID, str]] = None,
        is_shared: Optional[bool] = None,
    ) -> Workflow:
        """Update a workflow; only supplied fields are changed.

        Args:
            workflow_id: UUID of the workflow to update.
            name: New name.
            is_template: Template flag.
            description: New description.
            status: New status.
            schedule_status: New schedule status.
            job_id: Reassign to a different job.
            is_shared: Visibility flag for team members.

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
            }
        )
        return Workflow.from_dict(
            self._http.put(f"/workflows/{_str_id(workflow_id)}", json=body)
        )

    def delete(self, workflow_id: Union[uuid.UUID, str]) -> None:
        """Delete a workflow.

        Args:
            workflow_id: UUID of the workflow to delete.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/workflows/{_str_id(workflow_id)}")

    def set_team(
        self, workflow_id: Union[uuid.UUID, str], team_id: Union[uuid.UUID, str]
    ) -> Workflow:
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

    def clear_team(self, workflow_id: Union[uuid.UUID, str]) -> Workflow:
        """Remove the team assignment from a workflow.

        Args:
            workflow_id: UUID of the workflow.

        Returns:
            The updated :class:`~pyawe.models.Workflow`.

        Raises:
            AweNotFoundError: If the workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return Workflow.from_dict(
            self._http.delete(f"/workflows/{_str_id(workflow_id)}/team")
        )

    def merge(
        self,
        workflow_id: Union[uuid.UUID, str],
        other_id: Union[uuid.UUID, str],
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
            self._http.post(
                f"/workflows/{_str_id(workflow_id)}/merge/{_str_id(other_id)}"
            )
        )

    def duplicate(self, workflow_id: Union[uuid.UUID, str]) -> WorkflowWithTasks:
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


# ── tasks ─────────────────────────────────────────────────────────────────────


class TasksClient:
    """Methods for the ``/tasks`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, workflow_id: Optional[Union[uuid.UUID, str]] = None) -> List[Task]:
        """List tasks, optionally filtered by workflow.

        Args:
            workflow_id: When supplied, returns only tasks within this workflow.

        Returns:
            List of :class:`~pyawe.models.Task` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: Dict[str, Any] = {}
        if workflow_id is not None:
            params["workflow_id"] = _str_id(workflow_id)
        return [Task.from_dict(t) for t in self._http.get("/tasks", params=params)]

    def list_mine(
        self,
        role_ids: Optional[List[Union[uuid.UUID, str]]] = None,
    ) -> List[TaskWithContext]:
        """Return tasks assigned to the authenticated user or their team roles.

        Args:
            role_ids: Team role UUIDs to include alongside direct assignments.

        Returns:
            List of :class:`~pyawe.models.TaskWithContext` objects, each enriched
            with workflow and job names.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: Dict[str, Any] = {}
        if role_ids:
            params["role_ids"] = ",".join(_str_id(r) for r in role_ids)  # type: ignore[misc]
        return [TaskWithContext.from_dict(t) for t in self._http.get("/tasks/mine", params=params)]

    def create(
        self,
        name: str,
        workflow_id: Union[uuid.UUID, str],
        *,
        is_template: Optional[bool] = None,
        description: Optional[str] = None,
        status: Optional[Union[Status, str]] = None,
        schedule_status: Optional[Union[ScheduleStatus, str]] = None,
        rework_task_id: Optional[Union[uuid.UUID, str]] = None,
        is_start: Optional[bool] = None,
        is_end: Optional[bool] = None,
        task_type: Optional[Union[TaskType, str]] = None,
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
                ``"automated"``, or ``"loop_block"``.

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
            }
        )
        return Task.from_dict(self._http.post("/tasks", json=body))

    def get(self, task_id: Union[uuid.UUID, str]) -> Task:
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
        task_id: Union[uuid.UUID, str],
        *,
        name: Optional[str] = None,
        is_template: Optional[bool] = None,
        description: Optional[str] = None,
        status: Optional[Union[Status, str]] = None,
        schedule_status: Optional[Union[ScheduleStatus, str]] = None,
        rework_task_id: Optional[Union[uuid.UUID, str]] = None,
        is_start: Optional[bool] = None,
        is_end: Optional[bool] = None,
        task_type: Optional[Union[TaskType, str]] = None,
        assigned_to: Any = _UNSET,
    ) -> Task:
        """Update a task; only supplied fields are changed.

        ``assigned_to`` is a tri-state field:

        - **Omitted** (default): assignment is left unchanged.
        - **``None``**: clears the current assignment.
        - **A user ID string**: sets the assignment to that user.

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
            }
        )
        if assigned_to is not _UNSET:
            body["assigned_to"] = assigned_to  # None → clear; str → set
        return Task.from_dict(self._http.put(f"/tasks/{_str_id(task_id)}", json=body))

    def delete(self, task_id: Union[uuid.UUID, str]) -> None:
        """Delete a task.

        Args:
            task_id: UUID of the task to delete.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/tasks/{_str_id(task_id)}")

    def decide(self, task_id: Union[uuid.UUID, str], branch_label: str) -> Task:
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

    def clear_rework(self, task_id: Union[uuid.UUID, str]) -> Task:
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


# ── task links ────────────────────────────────────────────────────────────────


class TaskLinksClient:
    """Methods for task link management (``/task-links`` and ``/tasks/{id}/…``)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def create(
        self,
        from_task_id: Union[uuid.UUID, str],
        to_task_id: Union[uuid.UUID, str],
        *,
        branch_label: Optional[str] = None,
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
        body: Dict[str, Any] = {
            "from_task_id": _str_id(from_task_id),
            "to_task_id": _str_id(to_task_id),
        }
        if branch_label is not None:
            body["branch_label"] = branch_label
        return TaskLink.from_dict(self._http.post("/task-links", json=body))

    def delete(
        self,
        from_task_id: Union[uuid.UUID, str],
        to_task_id: Union[uuid.UUID, str],
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

    def get_next(self, task_id: Union[uuid.UUID, str]) -> List[Task]:
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

    def get_previous(self, task_id: Union[uuid.UUID, str]) -> List[Task]:
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

    def get_outgoing(self, task_id: Union[uuid.UUID, str]) -> List[TaskLink]:
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
        from_task_id: Union[uuid.UUID, str],
        to_task_id: Union[uuid.UUID, str],
        bindings: List[DataBinding],
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

    def list_specs(self, task_id: Union[uuid.UUID, str]) -> List[TaskPortSpec]:
        """Return all port specs (inputs and outputs) for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            List of :class:`~pyawe.models.TaskPortSpec` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            TaskPortSpec.from_dict(s)
            for s in self._http.get(f"/tasks/{_str_id(task_id)}/ports")
        ]

    def create_spec(
        self,
        task_id: Union[uuid.UUID, str],
        direction: str,
        name: str,
        value_type: str,
        *,
        required: Optional[bool] = None,
        description: Optional[str] = None,
        default_value: Optional[Any] = None,
        sort_order: Optional[int] = None,
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
        task_id: Union[uuid.UUID, str],
        port_id: Union[uuid.UUID, str],
        *,
        name: Optional[str] = None,
        value_type: Optional[str] = None,
        required: Optional[bool] = None,
        description: Optional[str] = None,
        default_value: Optional[Any] = None,
        sort_order: Optional[int] = None,
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
        task_id: Union[uuid.UUID, str],
        port_id: Union[uuid.UUID, str],
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

    def get_inputs(self, task_id: Union[uuid.UUID, str]) -> TaskPortValues:
        """Return input port specs and current values for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            :class:`~pyawe.models.TaskPortValues` with ``direction == "input"`` specs.

        Raises:
            AweAuthError: If not authenticated.
        """
        return TaskPortValues.from_dict(self._http.get(f"/tasks/{_str_id(task_id)}/inputs"))

    def patch_inputs(
        self, task_id: Union[uuid.UUID, str], values: Dict[str, Any]
    ) -> TaskPortValues:
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

    def get_outputs(self, task_id: Union[uuid.UUID, str]) -> TaskPortValues:
        """Return output port specs and current values for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            :class:`~pyawe.models.TaskPortValues` with ``direction == "output"`` specs.

        Raises:
            AweAuthError: If not authenticated.
        """
        return TaskPortValues.from_dict(self._http.get(f"/tasks/{_str_id(task_id)}/outputs"))


# ── task scripts ──────────────────────────────────────────────────────────────


class TaskScriptsClient:
    """Methods for automated task script management (``/tasks/{id}/script``)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def get(self, task_id: Union[uuid.UUID, str]) -> TaskScript:
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
        task_id: Union[uuid.UUID, str],
        *,
        script_type: Optional[str] = None,
        endpoint: Optional[str] = None,
        script_body: Optional[str] = None,
        timeout_secs: Optional[int] = None,
        retry_limit: Optional[int] = None,
        execution_profile_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> TaskScript:
        """Create or fully replace the script on a task.

        Args:
            task_id: UUID of the task.
            script_type: ``"webhook"`` (default), ``"shell"``,
                ``"python"``, or ``"mcp_tool"``.
            endpoint: Webhook URL; required when ``script_type == "webhook"``.
            script_body: Script source; required for ``"shell"``, ``"python"``,
                and ``"mcp_tool"`` types.
            timeout_secs: Execution timeout in seconds.
            retry_limit: Maximum number of retry attempts.
            execution_profile_id: Execution profile for Kubernetes dispatch
                (``"shell"`` and ``"python"`` only).

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
            }
        )
        return TaskScript.from_dict(
            self._http.put(f"/tasks/{_str_id(task_id)}/script", json=body)
        )

    def delete(self, task_id: Union[uuid.UUID, str]) -> None:
        """Remove the script from a task.

        Args:
            task_id: UUID of the task.

        Raises:
            AweNotFoundError: If no script is attached.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/tasks/{_str_id(task_id)}/script")


# ── task runs ─────────────────────────────────────────────────────────────────


class TaskRunsClient:
    """Methods for automated task execution history (``/tasks/{id}/runs``)."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self, task_id: Union[uuid.UUID, str]) -> List[TaskRun]:
        """Return all execution run records for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            List of :class:`~pyawe.models.TaskRun` objects, newest first.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [
            TaskRun.from_dict(r) for r in self._http.get(f"/tasks/{_str_id(task_id)}/runs")
        ]

    def create(
        self,
        task_id: Union[uuid.UUID, str],
        outcome: str,
        started_at: datetime,
        completed_at: datetime,
        *,
        run_id: Optional[Union[uuid.UUID, str]] = None,
        runner_id: Optional[str] = None,
        input_json: Optional[Any] = None,
        output_json: Optional[Any] = None,
        error_message: Optional[str] = None,
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

        Returns:
            The recorded :class:`~pyawe.models.TaskRun`.

        Raises:
            AweNotFoundError: If the task does not exist.
            AweAuthError: If not authenticated.
        """
        body: Dict[str, Any] = {
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
        return TaskRun.from_dict(
            self._http.post(f"/tasks/{_str_id(task_id)}/runs", json=body)
        )

    def get(
        self,
        task_id: Union[uuid.UUID, str],
        run_id: Union[uuid.UUID, str],
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

    def list(self, task_id: Union[uuid.UUID, str]) -> List[TaskTeamRole]:
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
        task_id: Union[uuid.UUID, str],
        team_role_id: Union[uuid.UUID, str],
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
        task_id: Union[uuid.UUID, str],
        team_role_id: Union[uuid.UUID, str],
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

    def list(self, team_id: Optional[Union[uuid.UUID, str]] = None) -> List[Job]:
        """Return all jobs, optionally filtered by team.

        Args:
            team_id: When supplied, returns only jobs for this team.

        Returns:
            List of :class:`~pyawe.models.Job` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: Dict[str, Any] = {}
        if team_id is not None:
            params["team_id"] = _str_id(team_id)
        return [Job.from_dict(j) for j in self._http.get("/jobs", params=params)]

    def create(
        self,
        name: str,
        *,
        status: Optional[Union[Status, str]] = None,
        schedule_status: Optional[Union[ScheduleStatus, str]] = None,
        team_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> Job:
        """Create a new job.

        Args:
            name: Job name.
            status: Initial status (default ``"Not Started"``).
            schedule_status: Initial schedule status (default ``"N/A"``).
            team_id: Assign to a team.

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
            }
        )
        return Job.from_dict(self._http.post("/jobs", json=body))

    def get(self, job_id: Union[uuid.UUID, str]) -> JobWithWorkflows:
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
        job_id: Union[uuid.UUID, str],
        *,
        name: Optional[str] = None,
        status: Optional[Union[Status, str]] = None,
        schedule_status: Optional[Union[ScheduleStatus, str]] = None,
        archived: Optional[bool] = None,
    ) -> Job:
        """Update a job; only supplied fields are changed.

        Args:
            job_id: UUID of the job to update.
            name: New name.
            status: New status.
            schedule_status: New schedule status.
            archived: Archive flag.

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
            }
        )
        return Job.from_dict(self._http.put(f"/jobs/{_str_id(job_id)}", json=body))

    def delete(self, job_id: Union[uuid.UUID, str]) -> None:
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
        job_id: Union[uuid.UUID, str],
        workflow_id: Union[uuid.UUID, str],
    ) -> WorkflowWithTasks:
        """Clone a workflow template into a job.

        Args:
            job_id: UUID of the target job.
            workflow_id: UUID of the workflow template to clone.

        Returns:
            The new :class:`~pyawe.models.WorkflowWithTasks` inside the job.

        Raises:
            AweNotFoundError: If the job or workflow does not exist.
            AweAuthError: If not authenticated.
        """
        return WorkflowWithTasks.from_dict(
            self._http.post(
                f"/jobs/{_str_id(job_id)}/workflows/from-template/{_str_id(workflow_id)}"
            )
        )

    def set_team(
        self, job_id: Union[uuid.UUID, str], team_id: Union[uuid.UUID, str]
    ) -> Job:
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

    def clear_team(self, job_id: Union[uuid.UUID, str]) -> Job:
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

    def list(self) -> List[ExecutionProfile]:
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
        description: Optional[str] = None,
        cpu_request: Optional[str] = None,
        cpu_limit: Optional[str] = None,
        memory_request: Optional[str] = None,
        memory_limit: Optional[str] = None,
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
            }
        )
        return ExecutionProfile.from_dict(self._http.post("/execution-profiles", json=body))

    def get(self, profile_id: Union[uuid.UUID, str]) -> ExecutionProfile:
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
        profile_id: Union[uuid.UUID, str],
        *,
        name: Optional[str] = None,
        image: Optional[str] = None,
        description: Optional[str] = None,
        cpu_request: Optional[str] = None,
        cpu_limit: Optional[str] = None,
        memory_request: Optional[str] = None,
        memory_limit: Optional[str] = None,
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
            }
        )
        return ExecutionProfile.from_dict(
            self._http.put(f"/execution-profiles/{_str_id(profile_id)}", json=body)
        )

    def delete(self, profile_id: Union[uuid.UUID, str]) -> None:
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
        workflow_id: Union[uuid.UUID, str],
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

    def get(self, loop_block_id: Union[uuid.UUID, str]) -> LoopBlock:
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
        loop_block_id: Union[uuid.UUID, str],
        *,
        name: Optional[str] = None,
        loop_type: Optional[str] = None,
        loop_config: Optional[Any] = None,
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

    def delete(self, loop_block_id: Union[uuid.UUID, str]) -> None:
        """Delete a loop block.

        Args:
            loop_block_id: UUID of the loop block.

        Raises:
            AweNotFoundError: If the loop block does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/loop-blocks/{_str_id(loop_block_id)}")


# ── notes ─────────────────────────────────────────────────────────────────────


class NotesClient:
    """Methods for the ``/notes`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[Union[uuid.UUID, str]] = None,
    ) -> List[Note]:
        """Return top-level notes visible to the authenticated user.

        Returns notes the caller owns plus all shared notes. Replies are
        excluded; use :meth:`list_replies` to fetch them.

        Args:
            entity_type: Filter by entity type: ``"task"``, ``"workflow"``,
                or ``"job"``.
            entity_id: Filter by the entity's UUID (requires *entity_type*).

        Returns:
            List of :class:`~pyawe.models.Note` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        params: Dict[str, Any] = {}
        if entity_type is not None:
            params["entity_type"] = entity_type
        if entity_id is not None:
            params["entity_id"] = _str_id(entity_id)
        return [Note.from_dict(n) for n in self._http.get("/notes", params=params)]

    def create(
        self,
        entity_type: str,
        entity_id: Union[uuid.UUID, str],
        title: str,
        *,
        body: Optional[str] = None,
        is_shared: bool = False,
    ) -> Note:
        """Create a top-level note on an entity.

        Args:
            entity_type: ``"task"``, ``"workflow"``, or ``"job"``.
            entity_id: UUID of the entity.
            title: Note title.
            body: Optional Markdown body.
            is_shared: When ``True``, visible to all team members with access
                to the entity.

        Returns:
            The newly created :class:`~pyawe.models.Note`.

        Raises:
            AweAuthError: If not authenticated.
        """
        payload: Dict[str, Any] = {
            "entity_type": entity_type,
            "entity_id": _str_id(entity_id),
            "title": title,
            "is_shared": is_shared,
        }
        if body is not None:
            payload["body"] = body
        return Note.from_dict(self._http.post("/notes", json=payload))

    def get(self, note_id: Union[uuid.UUID, str]) -> Note:
        """Fetch a single note.

        Args:
            note_id: UUID of the note.

        Returns:
            :class:`~pyawe.models.Note`.

        Raises:
            AweNotFoundError: If the note does not exist.
            AweAuthError: If not authenticated.
        """
        return Note.from_dict(self._http.get(f"/notes/{_str_id(note_id)}"))

    def update(
        self,
        note_id: Union[uuid.UUID, str],
        *,
        title: Optional[str] = None,
        body: Optional[str] = None,
        is_shared: Optional[bool] = None,
    ) -> Note:
        """Update a note; only supplied fields are changed.

        Args:
            note_id: UUID of the note.
            title: New title.
            body: New Markdown body.
            is_shared: New visibility setting.

        Returns:
            The updated :class:`~pyawe.models.Note`.

        Raises:
            AweNotFoundError: If the note does not exist.
            AweAuthError: If not authenticated.
        """
        payload = _compact({"title": title, "body": body, "is_shared": is_shared})
        return Note.from_dict(self._http.put(f"/notes/{_str_id(note_id)}", json=payload))

    def delete(self, note_id: Union[uuid.UUID, str]) -> None:
        """Delete a note.

        Args:
            note_id: UUID of the note to delete.

        Raises:
            AweNotFoundError: If the note does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/notes/{_str_id(note_id)}")

    def list_replies(self, note_id: Union[uuid.UUID, str]) -> List[Note]:
        """Return all replies to a note.

        Args:
            note_id: UUID of the parent note.

        Returns:
            List of reply :class:`~pyawe.models.Note` objects.

        Raises:
            AweNotFoundError: If the note does not exist.
            AweAuthError: If not authenticated.
        """
        return [
            Note.from_dict(n) for n in self._http.get(f"/notes/{_str_id(note_id)}/replies")
        ]

    def create_reply(self, note_id: Union[uuid.UUID, str], body: str) -> Note:
        """Post a reply to a note.

        Args:
            note_id: UUID of the parent note.
            body: Reply text (Markdown supported).

        Returns:
            The created reply :class:`~pyawe.models.Note`.

        Raises:
            AweNotFoundError: If the note does not exist.
            AweAuthError: If not authenticated.
        """
        return Note.from_dict(
            self._http.post(f"/notes/{_str_id(note_id)}/replies", json={"body": body})
        )

    def move(
        self,
        note_id: Union[uuid.UUID, str],
        folder_id: Optional[Union[uuid.UUID, str]],
    ) -> Note:
        """Move a note to a folder, or remove it from any folder.

        Args:
            note_id: UUID of the note.
            folder_id: UUID of the destination folder, or ``None`` to unfile.

        Returns:
            The updated :class:`~pyawe.models.Note`.

        Raises:
            AweNotFoundError: If the note does not exist.
            AweAuthError: If not authenticated.
        """
        return Note.from_dict(
            self._http.put(
                f"/notes/{_str_id(note_id)}/folder",
                json={"folder_id": _str_id(folder_id)},
            )
        )


# ── note folders ──────────────────────────────────────────────────────────────


class NoteFoldersClient:
    """Methods for the ``/note-folders`` resource."""

    def __init__(self, http: _HttpSession) -> None:
        self._http = http

    def list(self) -> List[NoteFolder]:
        """Return all note folders for the authenticated user.

        Returns:
            List of :class:`~pyawe.models.NoteFolder` objects.

        Raises:
            AweAuthError: If not authenticated.
        """
        return [NoteFolder.from_dict(f) for f in self._http.get("/note-folders")]

    def create(self, name: str) -> NoteFolder:
        """Create a note folder.

        Args:
            name: Folder name.

        Returns:
            The newly created :class:`~pyawe.models.NoteFolder`.

        Raises:
            AweAuthError: If not authenticated.
        """
        return NoteFolder.from_dict(self._http.post("/note-folders", json={"name": name}))

    def update(self, folder_id: Union[uuid.UUID, str], name: str) -> NoteFolder:
        """Rename a note folder.

        Args:
            folder_id: UUID of the folder.
            name: New name.

        Returns:
            The updated :class:`~pyawe.models.NoteFolder`.

        Raises:
            AweNotFoundError: If the folder does not exist.
            AweAuthError: If not authenticated.
        """
        return NoteFolder.from_dict(
            self._http.put(f"/note-folders/{_str_id(folder_id)}", json={"name": name})
        )

    def delete(self, folder_id: Union[uuid.UUID, str]) -> None:
        """Delete a note folder.

        Args:
            folder_id: UUID of the folder to delete.

        Raises:
            AweNotFoundError: If the folder does not exist.
            AweAuthError: If not authenticated.
        """
        self._http.delete(f"/note-folders/{_str_id(folder_id)}")


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
        api_url: Base URL of the AWE server, e.g. ``"http://localhost:8080"``.
        auth_url: Base URL of the authentication service,
            e.g. ``"http://localhost:8081"``. Defaults to *api_url* when
            auth and AWE are served behind the same proxy.

    Example:
        .. code-block:: python

            from pyawe import AweClient

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

    def __init__(self, api_url: str, auth_url: Optional[str] = None) -> None:
        self._http = _HttpSession(api_url, auth_url or api_url)
        self.workflows = WorkflowsClient(self._http)
        self.tasks = TasksClient(self._http)
        self.task_links = TaskLinksClient(self._http)
        self.task_ports = TaskPortsClient(self._http)
        self.task_scripts = TaskScriptsClient(self._http)
        self.task_runs = TaskRunsClient(self._http)
        self.task_team_roles = TaskTeamRolesClient(self._http)
        self.jobs = JobsClient(self._http)
        self.execution_profiles = ExecutionProfilesClient(self._http)
        self.loop_blocks = LoopBlocksClient(self._http)
        self.notes = NotesClient(self._http)
        self.note_folders = NoteFoldersClient(self._http)

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
