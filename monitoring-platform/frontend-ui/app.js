function getBarClass(value) {

    value = parseFloat(value);

    if (value < 50)
        return "low";

    if (value < 80)
        return "medium";

    return "high";
}

async function loadServers() {

    const response =
        await fetch("http://xxx.xxx.xxx.xxx:8000/api/servers");

    const servers = await response.json();

    const container =
        document.getElementById("server-container");

    container.innerHTML = "";

    servers.forEach(server => {

        let overallStatus = "RUNNING";

        if (
            parseFloat(server.cpu_usage) > 90 ||
            parseFloat(server.used_memory_percentage) > 90 ||
            server.status_ntp != "RUNNING"
        ) {
            overallStatus = "ISSUE";
        }

        let hostnameDisplay =
            server.hostname.includes(".cdot.in")
            ? server.hostname
            : server.hostname + ".cdot.in";

        container.innerHTML += `

        <a href="server.html?hostname=${server.hostname}"
           class="server-link">

            <div class="summary-card">

                <h2>${hostnameDisplay}</h2>

                <p>
                    <b>IP:</b>
                    ${server.ip_address}
                </p>

                <p>
                    <b>Status:</b>

                    <span class="${
                        overallStatus == 'RUNNING'
                        ? 'green'
                        : 'red'
                    }">
                        ${overallStatus}
                    </span>
                </p>

                <p>
                    <b>NTP:</b>

                    <span class="${
                        server.status_ntp == 'RUNNING'
                        ? 'green'
                        : 'red'
                    }">
                        ${server.status_ntp}
                    </span>
                </p>

                <hr>

                <p>
                    <b>CPU:</b>
                    ${server.cpu_usage}%
                </p>

                <div class="progress-bar">

                    <div class="progress ${getBarClass(server.cpu_usage)}"
                         style="width:${server.cpu_usage}%">

                    </div>

                </div>

                <p>
                    <b>Memory:</b>
                    ${server.used_memory_percentage}
                </p>

                <div class="progress-bar">

                    <div class="progress ${getBarClass(server.used_memory_percentage)}"
                         style="width:${server.used_memory_percentage}">

                    </div>

                </div>

            </div>

        </a>
        `;
    });

    const bastion =
        servers.find(s =>
            s.hostname.includes("ansible")
        );

    if (bastion) {

        container.innerHTML += `

        <div class="full-width">

            <h1 class="service-title">
                Infrastructure Services
            </h1>

            <div class="service-main-grid">

                <div class="service-card">

                    <h2>Nexus</h2>

                    <p>
                        <b>URL:</b><br>
                        m2mnexus.cdot.in:8081
                    </p>

                    <p>
                        <b>IP:</b><br>
                        192.168.126.143
                    </p>

                    <p>
                        <b>Status:</b>
                        <span class="${bastion.status_nexus == 'RUNNING' ? 'green' : 'red'}">
                            ${bastion.status_nexus}
                        </span>
                    </p>

                </div>

                <div class="service-card">

                    <h2>Rancher</h2>

                    <p>
                        <b>URL:</b><br>
                        m2mrancher.cdot.in
                    </p>

                    <p>
                        <b>IP:</b><br>
                        192.168.126.141
                    </p>

                    <p>
                        <b>Status:</b>
                        <span class="${bastion.status_rancher == 'RUNNING' ? 'green' : 'red'}">
                            ${bastion.status_rancher}
                        </span>
                    </p>

                </div>

                <div class="service-card">

                    <h2>FreeIPA</h2>

                    <p>
                        <b>URL:</b><br>
                        freeipam2m.cdot.in
                    </p>

                    <p>
                        <b>IP:</b><br>
                        192.168.126.142
                    </p>

                    <p>
                        <b>Status:</b>
                        <span class="${bastion.status_freeipa == 'RUNNING' ? 'green' : 'red'}">
                            ${bastion.status_freeipa}
                        </span>
                    </p>

                </div>

                <div class="service-card">

                    <h2>OVirt</h2>

                    <p>
                        <b>URL:</b><br>
                        novirtmgr.cdot.in
                    </p>

                    <p>
                        <b>IP:</b><br>
                        192.168.126.224
                    </p>

                    <p>
                        <b>Status:</b>
                        <span class="${bastion.status_ovirt == 'RUNNING' ? 'green' : 'red'}">
                            ${bastion.status_ovirt}
                        </span>
                    </p>

                </div>

            </div>

        </div>
        `;
    }
}

loadServers();

setInterval(loadServers, 60000);

function logout() {

    localStorage.removeItem(
        "authenticated"
    );

    window.location.href =
        "login.html";
}
