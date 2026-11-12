"""`python -m api_gateway` — serve the public API (default 127.0.0.1:8000)."""

import os

import uvicorn

from api_gateway.agent_client import AgentClient
from api_gateway.app import create_app
from api_gateway.db import make_engine
from api_gateway.settings import GatewaySettings


def main() -> None:
    s = GatewaySettings()
    engine = make_engine(s.db_url.get_secret_value())
    agent = AgentClient(s.agent_url, s.agent_internal_token.get_secret_value())
    uvicorn.run(
        create_app(s, engine, agent),
        host=os.environ.get("GATEWAY_HOST", "127.0.0.1"),
        port=int(os.environ.get("GATEWAY_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
