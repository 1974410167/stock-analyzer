from __future__ import annotations

import json

from advisor import generate_advice
from analyser import analyse_price_movements
from config import load_config
from ibkr_fetcher import FlexServiceError, extract_trade_rows, fetch_statement_xml


def main() -> None:
    config = load_config()

    try:
        statement_xml = fetch_statement_xml(config)
        trades = extract_trade_rows(statement_xml)
        analysis = analyse_price_movements(trades)
        advice = generate_advice(analysis)
    except FlexServiceError as exc:
        print(f"IBKR Flex error: {exc}")
        return
    except Exception as exc:  # pragma: no cover
        print(f"Unexpected error: {exc}")
        return

    print("Analysis:")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    print("\nAdvice:")
    print(advice)


if __name__ == "__main__":
    main()
