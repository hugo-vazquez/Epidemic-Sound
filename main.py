#!/usr/bin/python3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import logging

#Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

