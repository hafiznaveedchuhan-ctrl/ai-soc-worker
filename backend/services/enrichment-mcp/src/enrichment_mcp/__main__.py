"""`python -m enrichment_mcp` — serve over streamable HTTP (default http://127.0.0.1:8102/mcp)."""

from enrichment_mcp.server import build_server
from enrichment_mcp.settings import EnrichmentSettings


def main() -> None:
    settings = EnrichmentSettings()
    build_server(settings).run(transport="streamable-http", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
