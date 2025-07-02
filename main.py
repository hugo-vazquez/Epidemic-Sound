#!/usr/bin/python3

"""FastAPI application for onboarding and enriching user data from HR and Okta sources."""
from typing import List, Optional
import os
import logging
import requests # type: ignore
from fastapi import FastAPI, HTTPException # type: ignore
from pydantic import BaseModel # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# In-memory store for enriched users
enriched_users = {}

# Okta configuration
OKTA_DOMAIN = os.getenv("OKTA_DOMAIN", "https://dev-04279224-admin.okta.com")
OKTA_TOKEN = os.getenv("OKTA_API_TOKEN", "00ta_mfskUB028k6X7EqBrDKWbqboefIFmTlSSUpXw")

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
    """Represents an enriched user record combining HR and Okta data."""
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
def load_okta_data(email: str) -> Optional[OktaUser]:
    """Load Okta user data using the Okta API based on the provided email.

    Args:
        email (str): The email address to search for in the Okta user data.

    Returns:
        Optional[OktaUser]: An OktaUser object if found, otherwise None.
    """
    headers = {
        "Authorization": f"SSWS {OKTA_TOKEN}",
        "Accept": "application/json"
    }
    try:
        # Search users by email
        resp = requests.get(
            f"{OKTA_DOMAIN}/api/v1/users?q={email}",
            headers=headers,
            timeout=10
        )
        resp.raise_for_status()
        users = resp.json()
        if not users:
            logging.warning("No Okta user found for email: %s", email)
            return None

        user = users[0]
        user_id = user.get("id")

        # Fetch user groups
        groups_resp = requests.get(
            f"{OKTA_DOMAIN}/api/v1/users/{user_id}/groups",
            headers=headers,
            timeout=10
        )
        groups_resp.raise_for_status()
        groups = [g["profile"]["name"] for g in groups_resp.json()]

        # For simplicity, simulate application list
        applications = ["Google Workspace", "Slack", "Jira"]

        return OktaUser(profile=user["profile"], groups=groups, applications=applications)
    except requests.RequestException as e:
        logging.error("Failed to fetch Okta user data: %s", e)
        return None

def merge_user_data(hr: HRUser, okta: OktaUser) -> EnrichedUser:
    """Merge HR user data with Okta user data to create an enriched user record.

    Args:
        hr (HRUser): The HR user data.
        okta (OktaUser): The Okta user data.

    Returns:
        EnrichedUser: The enriched user record combining HR and Okta data.
    """
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
    """Endpoint to onboard and enrich a user.

    Accepts HR user data, loads corresponding Okta data, merges them, and stores the enriched user.
    Raises HTTP 404 if Okta data is not found.

    Args:
        hr_user (HRUser): The HR user data from the request body.

    Returns:
        dict: Success message if onboarding is successful.
    """
    logging.info("Received HR data for %s", hr_user.email)
    okta_data = load_okta_data(hr_user.email)
    if not okta_data:
        raise HTTPException(status_code=404, detail="Okta data not found")

    enriched = merge_user_data(hr_user, okta_data)
    enriched_users[hr_user.employee_id] = enriched
    logging.info("Enriched user %s stored", hr_user.employee_id)
    return {"message": "User onboarded successfully."}

@app.get("/user/{user_id}", response_model=EnrichedUser)
def get_user(user_id: str):
    """Endpoint to retrieve enriched user data by user ID.

    Args:
        user_id (str): The employee ID of the user.

    Returns:
        EnrichedUser: The enriched user data if found.

    Raises:
        HTTPException: If the user is not found.
    """
    user = enriched_users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
