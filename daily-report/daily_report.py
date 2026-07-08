import psycopg2
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_HOST = "<IP>"
DB_NAME = "monitoring"
DB_USER = "monitor"
DB_PASSWORD = "monitor123"

SMTP_SERVER = "<smtp server>"
SMTP_PORT = 587

FROM_MAIL = "<mail>"

SMTP_USERNAME = "<mail>"

SMTP_PASSWORD = "xxxxxxx"

TO_MAILS = [
    "<mail>",
    "<2ndmail>",
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
    status_ovirt,
    total_cpu,
    total_memory,
    free_memory_percent,
    available_memory_percent,
    total_swap,
    used_swap_percent,
    disk_data
FROM node_metrics
ORDER BY hostname, id DESC
""")

rows = cur.fetchall()

total_nodes = len(rows)

healthy_nodes = 0

issue_nodes = 0

html = """

<h1>Infrastructure Monitoring Daily Report</h1>

"""

for row in rows:

    hostname = row[0]

    cpu = float(row[1])

    memory = float(row[2].replace('%',''))

    ntp = row[3]

    total_cpu = row[10]

    total_memory = row[11]

    free_memory = row[12]

    available_memory = row[13]

    total_swap = row[14]

    used_swap = row[15]

    disk_data = row[16]

    node_status = "HEALTHY"

    if cpu > 90 or memory > 90 or ntp != "RUNNING":

        node_status = "ISSUE"

        issue_nodes += 1

    else:

        healthy_nodes += 1

    html += f"""

    <h2>{hostname}</h2>

    <table border="1" cellpadding="8" cellspacing="0">

    <tr style="background-color:#dddddd;">
        <th colspan="2">System Summary</th>
    </tr>

    <tr>
        <td><b>Status</b></td>
        <td>{node_status}</td>
    </tr>

    <tr>
        <td><b>CPU Usage</b></td>
        <td>{cpu}%</td>
    </tr>

    <tr>
        <td><b>Total CPU Cores</b></td>
        <td>{total_cpu}</td>
    </tr>

    <tr>
        <td><b>Memory Usage</b></td>
        <td>{memory}%</td>
    </tr>

    <tr>
        <td><b>Total Memory</b></td>
        <td>{total_memory}</td>
    </tr>

    <tr>
        <td><b>Free Memory</b></td>
        <td>{free_memory}</td>
    </tr>

    <tr>
        <td><b>Available Memory</b></td>
        <td>{available_memory}</td>
    </tr>

    <tr>
        <td><b>Total Swap</b></td>
        <td>{total_swap}</td>
    </tr>

    <tr>
        <td><b>Swap Used</b></td>
        <td>{used_swap}</td>
    </tr>

    <tr>
        <td><b>NTP Status</b></td>
        <td>{ntp}</td>
    </tr>

    </table>

    <br>

    <table border="1" cellpadding="8" cellspacing="0">

    <tr style="background-color:#dddddd;">
        <th colspan="6">Disk Partition Details</th>
    </tr>

    <tr style="background-color:#eeeeee;">
        <th>Filesystem</th>
        <th>Size</th>
        <th>Used</th>
        <th>Available</th>
        <th>Usage</th>
        <th>Mount</th>
    </tr>

    """

    for disk in disk_data:

        html += f"""

        <tr>
            <td>{disk['filesystem']}</td>
            <td>{disk['size']}</td>
            <td>{disk['used']}</td>
            <td>{disk['avail']}</td>
            <td>{disk['use']}</td>
            <td>{disk['mount']}</td>
        </tr>

        """

    html += "</table><br><hr><br>"

html += f"""

<h2>Infrastructure Summary</h2>

<b>Total Nodes:</b> {total_nodes}<br>

<b>Healthy Nodes:</b> {healthy_nodes}<br>

<b>Issue Nodes:</b> {issue_nodes}<br>

<br>

<h2>Bastion Services</h2>

"""

for row in rows:

    if row[0] == "bastiont":

        html += f"""

        <table border="1" cellpadding="8" cellspacing="0">

        <tr style="background-color:#dddddd;">
            <th>Service</th>
            <th>Status</th>
        </tr>

        <tr>
            <td>Nexus</td>
            <td>{row[4]}</td>
        </tr>

        <tr>
            <td>FreeIPA</td>
            <td>{row[5]}</td>
        </tr>

        <tr>
            <td>Rancher</td>
            <td>{row[6]}</td>
        </tr>

        <tr>
            <td>ELK</td>
            <td>{row[7]}</td>
        </tr>

        <tr>
            <td>Ingress</td>
            <td>{row[8]}</td>
        </tr>

        <tr>
            <td>OVirt</td>
            <td>{row[9]}</td>
        </tr>

        </table>

        """

msg = MIMEMultipart("alternative")

msg["Subject"] = "Daily Infrastructure Monitoring Report"

msg["From"] = FROM_MAIL

msg['To'] = ", ".join(TO_MAILS)

html_part = MIMEText(html, "html")

msg.attach(html_part)

server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

server.starttls()

server.login(SMTP_USERNAME, SMTP_PASSWORD)

server.sendmail(
    FROM_MAIL,
    TO_MAILS,
    msg.as_string()
)

server.quit()

print("Daily report mail sent successfully")

cur.close()

conn.close()
