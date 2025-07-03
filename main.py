#!/usr/bin/python3
# pylint: disable=too-few-public-methods disable=import-error

"""FastAPI application for onboarding and enriching user data from HR and Okta sources."""
from typing import List, Optional
import os
import logging
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

# In-memory store for enriched users
enriched_users = {}

# Okta configuration
OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
OKTA_TOKEN = os.getenv("OKTA_API_TOKEN")

# ------------------- Models -------------------
class HRUser(BaseModel):
    """Represents a user record from the HR system.
    This is a data model for HR user information. It is used for data validation and serialization.
    The class intentionally contains no public methods, as it is a Pydantic model.
    """
    employee_id: str
    first_name: str
    last_name: str
    preferred_name: Optional[str]
    email: str
    title: str
    department: str
    manager_email: str
    location: str
    office: str
    employment_type: str
    employment_status: str
    start_date: str
    termination_date: Optional[str]
    cost_center: str
    employee_type: str
    work_phone: str
    mobile_phone: str
    country: str
    time_zone: str
    legal_entity: str
    division: str

class OktaUser(BaseModel):
    """Represents a user record from Okta, including profile, groups, and applications."""
    profile: dict
    groups: List[str]
    applications: List[str]

class EnrichedUser(BaseModel):
    """Model representing the enriched user data combining HR and Okta information."""
    id: str
    name: str
    email: str
    title: str
    department: str
    startDate: str
    groups: List[str]
    applications: List[str]
    onboarded: bool

# ------------------- Helper Functions -------------------
def load_okta_data(employee_id: str) -> Optional[OktaUser]:
    """Fetch Okta user data using employee ID."""
    headers = {
        "Authorization": f"SSWS {OKTA_TOKEN}",
        "Accept": "application/json"
    }
    try:
        search_url = f'{OKTA_DOMAIN}/api/v1/users?search=profile.employeeNumber+eq+"{employee_id}"'
        logging.debug("Searching Okta with employee ID: %s", employee_id)
        logging.debug("Request URL: %s", search_url)

        resp = requests.get(search_url, headers=headers, timeout=10)
        logging.debug("Raw Okta response: %s", resp.text)
        resp.raise_for_status()
        users = resp.json()

        if not users:
            logging.warning("No Okta user found for employee_id: %s", employee_id)
            return None

        user = users[0]
        user_id = user.get("id")

        # Fetch groups
        groups_url = f"{OKTA_DOMAIN}/api/v1/users/{user_id}/groups"
        logging.debug("Fetching user groups: %s", groups_url)
        groups_resp = requests.get(groups_url, headers=headers, timeout=10)
        groups_resp.raise_for_status()
        groups = [g["profile"]["name"] for g in groups_resp.json()]

        # Simulated applications
        applications = ["Google Workspace", "Slack", "Jira"]

        return OktaUser(profile=user["profile"], groups=groups, applications=applications)

    except requests.RequestException as e:
        logging.error("Failed to fetch Okta user data: %s", e)
        return None

def merge_user_data(hr: HRUser, okta: OktaUser) -> EnrichedUser:
    """Merge HR and Okta data into a unified EnrichedUser model."""
    name = f"{hr.first_name} {hr.last_name}"
    return EnrichedUser(
        id=hr.employee_id,
        name=name,
        email=hr.email,
        title=hr.title,
        department=hr.department,
        startDate=hr.start_date,
        groups=okta.groups,
        applications=okta.applications,
        onboarded=True
    )

# ------------------- API Routes -------------------
@app.post("/hr_user")
def post_hr_user(hr_user: HRUser):
    """Onboard and enrich a user using HR + Okta data."""
    logging.info("Received HR data for %s", hr_user.email)
    okta_data = load_okta_data(hr_user.employee_id)
    if not okta_data:
        raise HTTPException(status_code=404, detail="Okta data not found")

    enriched = merge_user_data(hr_user, okta_data)
    enriched_users[hr_user.employee_id] = enriched
    logging.info("Enriched user %s stored", hr_user.employee_id)
    return {"message": "User onboarded successfully."}

@app.get("/user/{user_id}", response_model=EnrichedUser)
def get_user(user_id: str):
    """Retrieve enriched user by employee ID."""
    user = enriched_users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
