import psycopg2
import smtplib
from email.mime.text import MIMEText

DB_HOST = "192.168.7.239"
DB_NAME = "monitoring"
DB_USER = "monitor"
DB_PASSWORD = "monitor123"

SMTP_SERVER = "smtp.mgovcloud.in"
SMTP_PORT = 587

FROM_MAIL = "csgdevops@cdot.in"

SMTP_USERNAME = "csgdevops@cdot.in"

SMTP_PASSWORD = "L6ePYJPVBwZE"

TO_MAILS = [
    "csgdevops@cdot.in",
    "mrajak@cdot.in",
]

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

cur = conn.cursor()

cur.execute("""
SELECT DISTINCT ON (hostname)
    hostname,
    cpu_usage,
    used_memory_percentage,
    status_ntp,
    status_nexus,
    status_freeipa,
    status_rancher,
    status_elk,
    status_ingress,
    status_ovirt
FROM node_metrics
ORDER BY hostname, id DESC
""")

rows = cur.fetchall()

alerts = []

for row in rows:

    hostname = row[0]

    cpu = float(row[1])

    memory = float(row[2].replace('%',''))

    if cpu > 90:
        alerts.append(f"{hostname} CPU usage high: {cpu}%")

    if memory > 90:
        alerts.append(f"{hostname} Memory usage high: {memory}%")

    if row[3] != "RUNNING":
        alerts.append(f"{hostname} NTP service DOWN")

    if hostname == "bastiont":

        if row[4] != "RUNNING":
            alerts.append("Nexus DOWN")

        if row[5] != "RUNNING":
            alerts.append("FreeIPA DOWN")

        if row[6] != "RUNNING":
            alerts.append("Rancher DOWN")

        if row[7] != "RUNNING":
            alerts.append("ELK DOWN")

        if row[8] != "RUNNING":
            alerts.append("Ingress DOWN")

        if row[9] != "RUNNING":
            alerts.append("OVirt DOWN")

if alerts:

    body = "\n".join(alerts)

    msg = MIMEText(body)

    msg['Subject'] = "Infrastructure Monitoring Alerts"

    msg['From'] = FROM_MAIL

    msg['To'] = ", ".join(TO_MAILS)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

    server.set_debuglevel(1)

    server.starttls()

    server.login(SMTP_USERNAME, SMTP_PASSWORD)

    server.sendmail(
        FROM_MAIL,
        TO_MAIL,
        msg.as_string()
    )

    server.quit()

    print("Alert mail sent successfully")

else:

    print("No alerts")

cur.close()

conn.close()