function getHostname() {

    const params =
        new URLSearchParams(window.location.search);

    return params.get("hostname");
}

async function loadServerDetails() {

    const hostname = getHostname();

    const response =
        await fetch("http://192.168.7.239:8000/api/servers");

    const servers = await response.json();

    const server =
        servers.find(s => s.hostname == hostname);

    const container =
        document.getElementById("details-container");

    container.innerHTML = `

    <div class="details-card">

        <h1>${server.hostname}</h1>

        <p><b>IP:</b> ${server.ip_address}</p>

        <p><b>OS:</b> ${server.operating_system}</p>

        <p><b>Kernel:</b> ${server.kernel_version}</p>

        <p><b>Uptime:</b> ${server.uptime}</p>

        <p><b>CPU Usage:</b> ${server.cpu_usage}%</p>

        <p><b>Memory Usage:</b> ${server.used_memory_percentage}</p>

	<p>
	<b>NTP Status:</b>

	<span style="color:${server.status_ntp == 'RUNNING' ? 'lime' : 'red'}">
	${server.status_ntp}
	</span>
	</p>

	<p>
	<b>NTP Sync:</b>

	<span style="color:${server.ntp_sync_status == 'SYNCED' ? 'lime' : 'orange'}">
	${server.ntp_sync_status}
	</span>
	</p>

	<p><b>Processes:</b> ${server.total_processes}</p>

        
        <h2>Filesystem Usage</h2>

        <table>

            <tr>
                <th>Filesystem</th>
                <th>Size</th>
                <th>Used</th>
                <th>Avail</th>
                <th>Use%</th>
                <th>Mount</th>
            </tr>

            ${
                server.disk_data.map(disk => `
                <tr>
                    <td>${disk.filesystem}</td>
                    <td>${disk.size}</td>
                    <td>${disk.used}</td>
                    <td>${disk.avail}</td>
                    <td>${disk.use}</td>
                    <td>${disk.mount}</td>
                </tr>
                `).join("")
            }

        </table>

    </div>
    `;
}

loadServerDetails();

