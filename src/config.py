from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class FlexConfig:
    token: str
    query_id: str
    api_version: str = "3"
    send_request_url: str = (
        "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"
    )
    timeout_seconds: int = 30
    wait_seconds: int = 5


def load_config() -> FlexConfig:
    return FlexConfig(
        token=os.getenv("IBKR_FLEX_TOKEN", "134125430631770270589696"),
        query_id=os.getenv("IBKR_FLEX_QUERY_ID", "1419985"),
    )
