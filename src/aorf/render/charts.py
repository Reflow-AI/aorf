"""Server-generated inline SVG.

No JavaScript charting library, therefore no CDN, therefore no CSP relaxation. Every chart
is a string of SVG computed here and embedded in the page.
"""

from __future__ import annotations

from html import escape

W, H = 720, 260
PAD_L, PAD_R, PAD_T, PAD_B = 56, 20, 20, 44


def _scale(values: list[float]) -> tuple[float, float]:
    """Padded value range, never zero-height, so a flat series still draws a line."""
    lo, hi = min(values), max(values)
    if hi == lo:
        pad = abs(hi) * 0.1 or 1.0
        return lo - pad, hi + pad
    span = hi - lo
    return lo - span * 0.15, hi + span * 0.15


def _fmt(v: float) -> str:
    return f"{v:.4f}".rstrip("0").rstrip(".") or "0"


def progress_chart(series: dict) -> str:
    """Primary metric over run_date, with the reference line the question compares against.

    The reference is the baseline when one exists and the question's metric_target when it
    does not, so a repo with `baseline: none` still gets a line to judge against.
    """
    points = series.get("points") or []
    if not points:
        return (
            '<p class="empty">No dated results with a primary metric yet, so there is '
            "nothing to plot.</p>"
        )

    reference = series.get("reference") or {}
    ref_value = reference.get("value")
    values = [p["value"] for p in points]
    if isinstance(ref_value, (int, float)):
        values = values + [float(ref_value)]
    lo, hi = _scale(values)

    plot_w, plot_h = W - PAD_L - PAD_R, H - PAD_T - PAD_B
    n = len(points)

    def x_at(i: int) -> float:
        return PAD_L + (plot_w / 2 if n == 1 else plot_w * i / (n - 1))

    def y_at(v: float) -> float:
        return PAD_T + plot_h - plot_h * (v - lo) / (hi - lo)

    out = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="{escape(series.get("metric") or "metric")} over time" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]

    for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
        v = lo + (hi - lo) * frac
        y = y_at(v)
        out.append(f'<line class="grid" x1="{PAD_L}" y1="{y:.1f}" x2="{W - PAD_R}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{PAD_L - 8}" y="{y + 4:.1f}">{_fmt(v)}</text>')

    if isinstance(ref_value, (int, float)):
        y = y_at(float(ref_value))
        label = "baseline" if reference.get("kind") == "baseline" else "target"
        out.append(f'<line class="ref" x1="{PAD_L}" y1="{y:.1f}" x2="{W - PAD_R}" y2="{y:.1f}"/>')
        out.append(
            f'<text class="ref-label" x="{W - PAD_R}" y="{y - 6:.1f}">'
            f"{label} {_fmt(float(ref_value))}</text>"
        )

    path = " ".join(
        f"{'M' if i == 0 else 'L'}{x_at(i):.1f},{y_at(p['value']):.1f}"
        for i, p in enumerate(points)
    )
    out.append(f'<path class="line" d="{path}"/>')

    for i, p in enumerate(points):
        x, y = x_at(i), y_at(p["value"])
        cls = "dot baseline" if p["kind"] == "baseline" else f"dot {escape(p.get('verdict') or '')}"
        out.append(
            f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="5">'
            f"<title>{escape(p['id'])}: {_fmt(p['value'])} on {escape(p['date'])}</title>"
            f"</circle>"
        )
        out.append(
            f'<text class="point-label" x="{x:.1f}" y="{y - 12:.1f}">'
            f'{_fmt(p["value"])}</text>'
        )
        out.append(
            f'<text class="xtick" x="{x:.1f}" y="{H - PAD_B + 18:.1f}">'
            f'{escape(p["date"][5:])}</text>'
        )

    out.append("</svg>")
    return "".join(out)


def sweep_scatter(runs: list[dict], metric_name: str = "") -> str:
    """Every run in a sweep against its index, so the spread is visible, not just the winner.

    A sweep's headline number is one run out of forty; the point of plotting all of them is
    that "supported in 31 of 40 configurations" is a different claim from "supported".
    """
    values: list[tuple[int, float, str]] = []
    for i, run in enumerate(runs):
        metrics = run.get("metrics") or {}
        if not isinstance(metrics, dict):
            continue
        value = metrics.get(metric_name) if metric_name else None
        if value is None:
            numeric = [v for v in metrics.values() if isinstance(v, (int, float))]
            value = numeric[0] if numeric else None
        if isinstance(value, (int, float)):
            values.append((i, float(value), str(run.get("run_id", i))))
    if not values:
        return ""

    lo, hi = _scale([v for _, v, _ in values])
    plot_w, plot_h = W - PAD_L - PAD_R, H - PAD_T - PAD_B
    n = len(values)

    out = [
        f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" '
        f'aria-label="sweep runs" xmlns="http://www.w3.org/2000/svg">'
    ]
    for frac in (0.0, 0.5, 1.0):
        v = lo + (hi - lo) * frac
        y = PAD_T + plot_h - plot_h * (v - lo) / (hi - lo)
        out.append(f'<line class="grid" x1="{PAD_L}" y1="{y:.1f}" x2="{W - PAD_R}" y2="{y:.1f}"/>')
        out.append(f'<text class="tick" x="{PAD_L - 8}" y="{y + 4:.1f}">{_fmt(v)}</text>')

    best = max(values, key=lambda t: t[1])
    for i, value, run_id in values:
        x = PAD_L + (plot_w / 2 if n == 1 else plot_w * i / (n - 1))
        y = PAD_T + plot_h - plot_h * (value - lo) / (hi - lo)
        cls = "dot best" if (i, value, run_id) == best else "dot"
        out.append(
            f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="4">'
            f"<title>{escape(run_id)}: {_fmt(value)}</title></circle>"
        )
    out.append(
        f'<text class="xtick" x="{PAD_L}" y="{H - PAD_B + 18}">run 1</text>'
        f'<text class="xtick" x="{W - PAD_R}" y="{H - PAD_B + 18}" '
        f'text-anchor="end">run {n}</text>'
    )
    out.append("</svg>")
    return "".join(out)


def delta_bar(value: float | None, scale: float) -> str:
    """A one-line signed bar for a delta, so a table column reads at a glance."""
    if value is None or not scale:
        return ""
    width = min(abs(value) / scale, 1.0) * 50
    cls = "up" if value >= 0 else "down"
    x = 50 if value >= 0 else 50 - width
    return (
        f'<svg class="sparkbar" viewBox="0 0 100 12" xmlns="http://www.w3.org/2000/svg">'
        f'<line class="axis" x1="50" y1="0" x2="50" y2="12"/>'
        f'<rect class="{cls}" x="{x:.1f}" y="3" width="{width:.1f}" height="6"/></svg>'
    )
