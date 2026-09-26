"""Deterministic unit-economics calculator, so pricing decisions don't rest on model arithmetic."""

from __future__ import annotations

import json
from typing import Any

from anthropic import beta_tool


def unit_economics(
    price_per_client_month: float,
    clients: int,
    variable_cost_per_client_month: float,
    fixed_cost_month: float,
    setup_fee: float = 0.0,
    payment_fee_pct: float = 2.9,
    monthly_churn_pct: float = 5.0,
) -> dict[str, Any]:
    revenue = price_per_client_month * clients
    payment_fees = revenue * payment_fee_pct / 100 + 0.30 * clients
    cogs = variable_cost_per_client_month * clients + fixed_cost_month + payment_fees
    gross = revenue - cogs
    per_client_contribution = (
        price_per_client_month * (1 - payment_fee_pct / 100) - 0.30 - variable_cost_per_client_month
    )
    churn = max(monthly_churn_pct, 0.1) / 100
    return {
        "mrr": round(revenue, 2),
        "monthly_cost": round(cogs, 2),
        "gross_profit_month": round(gross, 2),
        "gross_margin_pct": round(100 * gross / revenue, 1) if revenue else None,
        "breakeven_clients": (
            int(-(-fixed_cost_month // per_client_contribution)) if per_client_contribution > 0 else None
        ),
        "expected_lifetime_months": round(1 / churn, 1),
        "ltv_per_client": round(per_client_contribution / churn + setup_fee, 2),
    }


def unit_economics_tool() -> Any:
    @beta_tool
    def calculate_unit_economics(
        price_per_client_month: float,
        clients: int,
        variable_cost_per_client_month: float,
        fixed_cost_month: float,
        setup_fee: float = 0.0,
        payment_fee_pct: float = 2.9,
        monthly_churn_pct: float = 5.0,
    ) -> str:
        """Compute MRR, gross margin, break-even client count and LTV for a pricing
        scenario. Use it instead of doing the arithmetic yourself.

        Args:
            price_per_client_month: Monthly retainer or subscription price in USD.
            clients: Number of paying clients in the scenario.
            variable_cost_per_client_month: Usage costs per client (minutes, tokens, SMS, seats).
            fixed_cost_month: Platform and tool subscriptions shared across clients.
            setup_fee: One-time onboarding fee per client.
            payment_fee_pct: Card processing percentage (Stripe US is 2.9 plus $0.30).
            monthly_churn_pct: Expected share of clients lost per month.
        """
        return json.dumps(
            unit_economics(
                price_per_client_month,
                clients,
                variable_cost_per_client_month,
                fixed_cost_month,
                setup_fee,
                payment_fee_pct,
                monthly_churn_pct,
            )
        )

    return calculate_unit_economics
