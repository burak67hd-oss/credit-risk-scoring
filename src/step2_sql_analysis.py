"""Step 2 — Run the SQL analysis queries, save the results and two charts."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from utils import FIG_DIR, RESULTS_DIR, SQL_DIR, connect, read_named_queries


def bar_chart(df: pd.DataFrame, x: str, title: str, filename: str) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(df[x].astype(str), df["default_rate_pct"], color="#1F3864")
    for i, v in enumerate(df["default_rate_pct"]):
        ax.text(i, v + 0.8, f"{v:.1f}%", ha="center", fontsize=9)
    ax.set_ylabel("Default rate (%)")
    ax.set_title(title)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / filename, dpi=150)
    plt.close(fig)


def run_analysis() -> dict[str, pd.DataFrame]:
    RESULTS_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(exist_ok=True)
    con = connect()
    tables = {}
    for name, query in read_named_queries(SQL_DIR / "03_analysis.sql").items():
        df = pd.read_sql_query(query, con)
        df.to_csv(RESULTS_DIR / f"{name}.csv", index=False)
        tables[name] = df
        print(f"\n== {name}\n{df.to_string(index=False)}")
    con.close()

    status = tables["default_by_last_repayment_status"]
    bar_chart(status, "last_status", "Default rate by most recent repayment status",
              "default_by_last_status.png")
    age = tables["default_by_age_band"]
    bar_chart(age, "age_band", "Default rate by age band", "default_by_age_band.png")
    return tables


if __name__ == "__main__":
    run_analysis()
