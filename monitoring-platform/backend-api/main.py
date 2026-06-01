from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

import psycopg2
import psycopg2.extras
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_HOST = os.getenv("DB_HOST", "monitoring-postgres")
DB_USER = os.getenv("DB_USER", "monitor")
DB_PASSWORD = os.getenv("DB_PASSWORD", "monitor123")
DB_NAME = os.getenv("DB_NAME", "monitoring")


class NodeMetric(BaseModel):

    hostname: str
    ip_address: str

    operating_system: str
    kernel_version: str
    uptime: str

    current_time_stamp: str

    status_ntp: str
    ntp_sync_status: str

    status_nexus: str
    status_freeipa: str
    status_rancher: str
    status_elk: str
    status_ingress: str
    status_ovirt: str

    total_cpu: int
    cpu_usage: float

    total_processes: int

    total_memory: str
    used_memory_percentage: str
    free_memory_percent: str
    available_memory_percent: str

    total_swap: str
    used_swap_percent: str

    disk_data: List[Dict]

    active_users: int


@app.get("/")
def home():
    return {"status": "Monitoring Backend Running"}


@app.post("/api/node_metrics")
def insert_metrics(metric: NodeMetric):

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO node_metrics (
            hostname,
            ip_address,
            operating_system,
            kernel_version,
            uptime,
            current_time_stamp,
            status_ntp,
            ntp_sync_status,
            status_nexus,
            status_freeipa,
            status_rancher,
            status_elk,
            status_ingress,
            status_ovirt,
            total_cpu,
            cpu_usage,
            total_processes,
            total_memory,
            used_memory_percentage,
            free_memory_percent,
            available_memory_percent,
            total_swap,
            used_swap_percent,
            disk_data,
            active_users
        )
        VALUES (
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s
        )
    """, (
        metric.hostname,
        metric.ip_address,
        metric.operating_system,
        metric.kernel_version,
        metric.uptime,
        metric.current_time_stamp,
        metric.status_ntp,
        metric.ntp_sync_status,
        metric.status_nexus,
        metric.status_freeipa,
        metric.status_rancher,
        metric.status_elk,
        metric.status_ingress,
        metric.status_ovirt,
        metric.total_cpu,
        metric.cpu_usage,
        metric.total_processes,
        metric.total_memory,
        metric.used_memory_percentage,
        metric.free_memory_percent,
        metric.available_memory_percent,
        metric.total_swap,
        metric.used_swap_percent,
        psycopg2.extras.Json(metric.disk_data),
        metric.active_users
    ))

    conn.commit()

    cur.close()
    conn.close()

    return {"message": "metrics inserted"}


@app.get("/api/servers")
def get_servers():

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT ON (hostname)
            *
        FROM node_metrics
        ORDER BY hostname, id DESC
    """)

    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]

    result = []

    for row in rows:
        result.append(dict(zip(columns, row)))

    cur.close()
    conn.close()

    return result
