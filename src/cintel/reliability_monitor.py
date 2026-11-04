"""Monitor rolling error rates using two window sizes.

Author: Darrion Maurice Stringer
Date: 2026-11
"""

from pathlib import Path

import polars as pl


def main() -> None:
    """Save rolling reliability signals and a time-series chart."""
    root = Path.cwd()
    artifacts = root / "artifacts"
    images = root / "docs" / "images"
    artifacts.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)

    data = pl.read_csv(
        root / "data" / "system_metrics_timeseries.csv",
        try_parse_dates=True,
    ).sort("timestamp")

    required = ["timestamp", "requests", "errors"]
    if not all(column in data.columns for column in required):
        raise ValueError("Required columns are missing.")
    if any(data[column].null_count() for column in required):
        raise ValueError("Required columns contain missing values.")
    if data["timestamp"].n_unique() != data.height:
        raise ValueError("Duplicate timestamps require review.")
    if data.filter(
        (pl.col("requests") < 0)
        | (pl.col("errors") < 0)
        | (pl.col("errors") > pl.col("requests"))
    ).height:
        raise ValueError("Invalid request or error counts.")

    signals = data.with_columns(
        pl.when(pl.col("requests") > 0)
        .then(100 * pl.col("errors") / pl.col("requests"))
        .otherwise(None)
        .alias("error_rate_pct")
    ).with_columns(
        pl.col("error_rate_pct").rolling_mean(3).alias("rolling_error_pct_3"),
        pl.col("error_rate_pct").rolling_mean(5).alias("rolling_error_pct_5"),
    )

    # Illustrative review threshold, not an established service standard.
    threshold = 3.0
    signals = signals.with_columns(
        (pl.col("rolling_error_pct_3") > threshold).alias("review_window3"),
        (pl.col("rolling_error_pct_5") > threshold).alias("review_window5"),
    )
    signals.write_csv(artifacts / "rolling_reliability.csv")

    summary_rows = []
    for window in (3, 5):
        column = f"rolling_error_pct_{window}"
        valid = signals.filter(pl.col(column).is_not_null())
        peak = valid.sort(column, descending=True).row(0, named=True)
        flagged = valid.filter(pl.col(column) > threshold)
        summary_rows.append(
            {
                "window_size": window,
                "complete_windows": valid.height,
                "peak_error_rate_pct": peak[column],
                "peak_timestamp": str(peak["timestamp"]),
                "observations_above_3pct": flagged.height,
            }
        )
    summary = pl.DataFrame(summary_rows)
    summary.write_csv(artifacts / "reliability_summary.csv")

    # Plot actual elapsed time along the horizontal axis.
    times = signals["timestamp"].to_list()
    duration = (times[-1] - times[0]).total_seconds()
    if duration <= 0:
        raise ValueError("At least two different timestamps are required.")
    maximum = max(6.0, signals["error_rate_pct"].max() * 1.1)

    def x_position(timestamp):
        elapsed = (timestamp - times[0]).total_seconds()
        return 80 + elapsed / duration * 740

    def y_position(value):
        return 340 - value / maximum * 240

    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="460" viewBox="0 0 900 460">',
        '<rect width="900" height="460" fill="white"/>',
        '<g font-family="Arial" fill="#172033">',
        '<text x="40" y="35" font-size="24">Rolling Error Rates Over Time</text>',
        '<text x="40" y="65" font-size="14">Trailing windows; each point uses current and earlier observations.</text>',
    ]
    for tick in range(int(maximum) + 1):
        y = y_position(tick)
        svg.append(f'<path d="M80 {y:.2f} H820" stroke="#e5e7eb"/>')
        svg.append(f'<text x="40" y="{y + 5:.2f}" font-size="13">{tick}%</text>')

    threshold_y = y_position(threshold)
    svg.append(
        f'<path d="M80 {threshold_y:.2f} H820" stroke="#dc2626" stroke-dasharray="6 4"/>'
    )
    for column, color in (
        ("error_rate_pct", "#9ca3af"),
        ("rolling_error_pct_3", "#2563eb"),
        ("rolling_error_pct_5", "#9333ea"),
    ):
        # Separate segments at missing values rather than bridging gaps.
        segment = []
        for timestamp, value in zip(times, signals[column].to_list(), strict=True):
            if value is None:
                if segment:
                    points = " ".join(segment)
                    svg.append(
                        f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>'
                    )
                    segment = []
            else:
                segment.append(f"{x_position(timestamp):.2f},{y_position(value):.2f}")
        if segment:
            points = " ".join(segment)
            svg.append(
                f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>'
            )

    for index in (0, 12, 24, 36, 48, 59):
        timestamp = times[index]
        x = x_position(timestamp)
        label = timestamp.strftime("%H:%M")
        svg.append(
            f'<text x="{x:.2f}" y="365" text-anchor="middle" font-size="13">{label}</text>'
        )
    svg.extend(
        [
            '<text x="350" y="395" font-size="14">Time on February 1, 2026</text>',
            '<text x="80" y="425" fill="#6b7280" font-size="14">Gray: observed error rate</text>',
            '<text x="330" y="425" fill="#2563eb" font-size="14">Blue: window 3</text>',
            '<text x="530" y="425" fill="#9333ea" font-size="14">Purple: window 5</text>',
            '<text x="80" y="450" fill="#dc2626" font-size="13">Dashed red: illustrative 3% review threshold</text>',
            "</g></svg>",
        ]
    )
    (images / "rolling-reliability.svg").write_text(
        "\n".join(svg) + "\n", encoding="utf-8"
    )

    print(summary)
    print("Saved artifacts/rolling_reliability.csv")
    print("Saved artifacts/reliability_summary.csv")
    print("Saved docs/images/rolling-reliability.svg")


if __name__ == "__main__":
    main()
