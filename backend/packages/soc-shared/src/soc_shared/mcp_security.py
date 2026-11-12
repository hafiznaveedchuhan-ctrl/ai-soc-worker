"""DNS-rebinding protection for our MCP servers when they listen on 0.0.0.0 inside compose.

mcp 2.3.0 enables it automatically only for 127.0.0.1; in a container we set it explicitly from
MCP_ALLOWED_HOSTS, e.g. "wazuh-mcp:*,127.0.0.1:*,localhost:*".
"""

import os
from typing import Any


def transport_security_kwargs() -> dict[str, Any]:
    hosts = [h.strip() for h in os.environ.get("MCP_ALLOWED_HOSTS", "").split(",") if h.strip()]
    if not hosts:
        return {}
    from mcp.server.transport_security import TransportSecuritySettings

    return {
        "transport_security": TransportSecuritySettings(
            enable_dns_rebinding_protection=True, allowed_hosts=hosts, allowed_origins=[]
        )
    }
