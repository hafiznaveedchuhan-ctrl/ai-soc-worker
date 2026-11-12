"""`python -m wazuh_mcp` — serve over streamable HTTP (default http://127.0.0.1:8101/mcp)."""

from wazuh_mcp.server import build_server, source_from
from wazuh_mcp.settings import WazuhMcpSettings


def main() -> None:
    settings = WazuhMcpSettings()
    build_server(source_from(settings)).run(
        transport="streamable-http", host=settings.host, port=settings.port
    )


if __name__ == "__main__":
    main()
