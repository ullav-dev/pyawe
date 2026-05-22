"""Print tasks assigned to the authenticated user."""

import os
import sys

from pyawe import AweClient, AweAuthError, AweError

API_URL = os.environ.get("AWE_API_URL", "http://localhost:8080")
AUTH_URL = os.environ.get("AWE_AUTH_URL", API_URL)
EMAIL = os.environ["AWE_EMAIL"]
PASSWORD = os.environ["AWE_PASSWORD"]

client = AweClient(api_url=API_URL, auth_url=AUTH_URL)

try:
    client.login(email=EMAIL, password=PASSWORD)
except AweAuthError as e:
    print(f"Login failed: {e}", file=sys.stderr)
    sys.exit(1)

try:
    tasks = client.tasks.list_mine()
except AweError as e:
    print(f"Error fetching tasks: {e}", file=sys.stderr)
    sys.exit(1)

if not tasks:
    print("No tasks assigned to you.")
    sys.exit(0)

for twc in tasks:
    context = twc.workflow_name
    if twc.job_name:
        context = f"{twc.job_name} / {twc.workflow_name}"
    print(f"[{twc.task.status}]  {twc.task.name}  ({context})")
