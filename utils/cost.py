"""
Token usage tracking and cost estimation for Anthropic Claude API calls.
Prices are per million tokens (MTok) as of 2025-04.
"""

# Cost per million tokens in USD
# Source: https://www.anthropic.com/pricing
_PRICING = {
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
    "claude-opus-4-5":   {"input": 15.00, "output": 75.00},
    "claude-haiku-4-5":  {"input": 0.80,  "output": 4.00},
    # fallback for unknown models
    "default":           {"input": 3.00,  "output": 15.00},
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> dict:
    """
    Calculate the estimated USD cost of a Claude API call.

    Args:
        model: Claude model ID string (e.g. 'claude-sonnet-4-5').
        input_tokens: Number of input tokens consumed.
        output_tokens: Number of output tokens generated.

    Returns:
        dict with keys: input_tokens, output_tokens, total_tokens, cost_usd (str formatted).
    """
    rates = _PRICING.get(model, _PRICING["default"])
    cost = (input_tokens / 1_000_000 * rates["input"]) + \
           (output_tokens / 1_000_000 * rates["output"])
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": f"${cost:.4f}",
        "cost_float": cost,
    }


def format_usage_badge(usage_data: dict) -> str:
    """
    Format usage stats into a compact display string for the Streamlit UI.

    Args:
        usage_data: dict returned by calculate_cost().

    Returns:
        Human-readable string, e.g. '1,234 tokens | $0.0021'
    """
    total = usage_data.get("total_tokens", 0)
    cost = usage_data.get("cost_usd", "$0.0000")
    return f"{total:,} tokens | {cost}"
