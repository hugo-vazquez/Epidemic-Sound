# Installation & Usage

## Clone and Navigate
```
git clone https://github.com/hugo-vazquez/Epidemic-Sound.git
cd Epidemic-Sound
```

## Set environmental variables
```
export OKTA_DOMAIN="https://dev-04279224-admin.okta.com"
export OKTA_API_TOKEN="00ta_mfskUB028k6X7EqBrDKWbqboefIFmTlSSUpXw"
```

## Start application
```
./run.sh
```

## User data from OKTA
```
curl -X GET "${OKTA_DOMAIN}/api/v1/users?search=profile.employeeNumber+eq+%2212345%22" -H "Authorization: SSWS ${OKTA_API_TOKEN}
" -H "Accept: application/json"
```

## Onboard a User 
```
curl -X POST http://localhost:8000/hr_user \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "12345",
    "first_name": "Jane",
    "last_name": "Doe",
    "preferred_name": "Janey",
    "email": "jane.doe@example.com",
    "title": "Software Engineer",
    "department": "Engineering",
    "manager_email": "john.smith@example.com",
    "location": "Stockholm",
    "office": "HQ",
    "employment_type": "Full-Time",
    "employment_status": "Active",
    "start_date": "2024-01-15",
    "termination_date": null,
    "cost_center": "ENG-SE-001",
    "employee_type": "Regular",
    "work_phone": "+46 8 123 456 78",
    "mobile_phone": "+46 70 987 6543",
    "country": "Sweden",
    "time_zone": "Europe/Stockholm",
    "legal_entity": "Epidemic Sound AB",
    "division": "Product & Engineering"
  }'
```

## Get user after enrichment
```
curl http://localhost:8000/user/12345
```

## NOTE: 
Enriched user is stored in local memmory. All data is lost when the app restarts

## Tech choices - Python, FastAPI, Pydantic, Okta
The application is built in FastAPI which is a Python based. Python makes it easy to handle JSON, error handling, REST APIs, it's easy to read and write and has a large community and a bast library of packages available.
FastAPI it's a framework with a short learning curve, easy to maintain and extend and with a strong community support
Pydantic is a python library for data validation, it's used to validate the data received from the user and ensure it meets the expected format before processing, which helps to prevent errors and ensure data integrity.

## Trade off or Challenges
## Anything you'd improve with more time
Persistent storage, potentially containerization of the application.
