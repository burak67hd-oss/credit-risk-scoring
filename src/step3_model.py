"""Step 3 — Train and evaluate two credit-scoring models on the SQL feature view.

Models
  * Logistic regression: the standard, interpretable baseline used in credit scoring.
  * Gradient boosting: a more flexible model, to check whether non-linear effects add value.

Metrics
  * ROC AUC: probability that a random defaulter gets a higher score than a random non-defaulter.
  * Gini = 2 * AUC - 1: the usual way banks report the discriminatory power of a score.
  * KS: maximum gap between the score distributions of defaulters and non-defaulters.
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from utils import FIG_DIR, RESULTS_DIR, connect

RANDOM_STATE = 42
# Amounts are very skewed (a few huge values), so they are log-transformed for the logistic model
AMOUNTS = ["limit_bal", "last_payment", "last_bill"]
NUMERIC = ["age", "max_delay_6m", "n_months_late_6m",
           "utilisation_last", "utilisation_avg_6m", "payment_ratio_6m"]
# The repayment status is treated as a category: "revolving" is less risky than "paid on time",
# so the raw codes (-2, -1, 0, 1, 2...) do not have a linear relation with risk.
# Sex is deliberately excluded: using gender in a credit decision raises fairness and legal issues.
CATEGORICAL = ["education", "marriage", "last_status_group"]
TARGET = "default_next_month"


def log_amounts(x):
    """log(1 + x) on amounts, negative values (credit balances) set to 0 first."""
    return np.log1p(np.clip(x, 0, None))


def load_features() -> pd.DataFrame:
    con = connect()
    df = pd.read_sql_query("SELECT * FROM client_features", con)
    con.close()
    return df


def ks_statistic(y_true, scores) -> float:
    fpr, tpr, _ = roc_curve(y_true, scores)
    return float(np.max(tpr - fpr))


def build_models() -> dict[str, Pipeline]:
    preprocess = ColumnTransformer([
        ("amt", Pipeline([("log", FunctionTransformer(log_amounts, feature_names_out="one-to-one")),
                          ("scale", StandardScaler())]), AMOUNTS),
        ("num", StandardScaler(), NUMERIC),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    logit = Pipeline([
        ("prep", preprocess),
        ("model", LogisticRegression(max_iter=1000)),
    ])
    # Trees do not need scaling or log transforms: amounts and numbers are passed as they are
    gbm = Pipeline([
        ("prep", ColumnTransformer([
            ("num", "passthrough", AMOUNTS + NUMERIC),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ])),
        ("model", HistGradientBoostingClassifier(
            max_iter=300, learning_rate=0.05, max_leaf_nodes=15,
            random_state=RANDOM_STATE)),
    ])
    return {"Logistic regression": logit, "Gradient boosting": gbm}


def run_models() -> dict:
    df = load_features()
    X, y = df[AMOUNTS + NUMERIC + CATEGORICAL], df[TARGET]

    # 80/20 split, stratified so both sets keep the same default rate (~22%)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    results, curves = {}, {}

    for name, pipe in build_models().items():
        # 5-fold cross-validation on the training set only
        cv_auc = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="roc_auc")

        # Final fit on the full training set, evaluation on the untouched test set
        pipe.fit(X_train, y_train)
        scores = pipe.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, scores)

        results[name] = {
            "cv_auc_mean": round(float(cv_auc.mean()), 4),
            "cv_auc_std": round(float(cv_auc.std()), 4),
            "test_auc": round(float(auc), 4),
            "test_gini": round(float(2 * auc - 1), 4),
            "test_ks": round(ks_statistic(y_test, scores), 4),
        }
        curves[name] = roc_curve(y_test, scores)[:2]
        print(f"\n== {name}\n{json.dumps(results[name], indent=2)}")

    # Decision threshold for the logistic model: flag the 20% riskiest clients
    logit = build_models()["Logistic regression"].fit(X_train, y_train)
    scores = logit.predict_proba(X_test)[:, 1]
    threshold = float(np.quantile(scores, 0.80))
    y_pred = (scores >= threshold).astype(int)
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    results["Logistic regression"]["decision_rule"] = {
        "rule": "flag the 20% highest scores",
        "threshold": round(threshold, 4),
        "recall_defaulters": round(report["1"]["recall"], 4),
        "precision_defaulters": round(report["1"]["precision"], 4),
        "confusion_matrix [[TN, FP], [FN, TP]]": cm.tolist(),
    }
    print("\nDecision rule (logistic regression):")
    print(json.dumps(results["Logistic regression"]["decision_rule"], indent=2))

    # Logistic regression coefficients (on standardised variables)
    names = logit.named_steps["prep"].get_feature_names_out()
    coefs = pd.Series(logit.named_steps["model"].coef_[0], index=names)
    coefs = coefs.reindex(coefs.abs().sort_values(ascending=False).index)
    coefs.round(4).to_csv(RESULTS_DIR / "logit_coefficients.csv", header=["coefficient"])
    print("\nTop logistic regression coefficients:\n" + coefs.head(8).round(3).to_string())

    # ROC curves
    fig, ax = plt.subplots(figsize=(5.5, 5))
    for (name, (fpr, tpr)), color in zip(curves.items(), ["#1F3864", "#C0504D"]):
        ax.plot(fpr, tpr, color=color, label=f"{name} (AUC = {results[name]['test_auc']:.3f})")
    ax.plot([0, 1], [0, 1], "--", color="grey", linewidth=1)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title("ROC curves on the test set")
    ax.legend(loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "roc_curves.png", dpi=150)
    plt.close(fig)

    with open(RESULTS_DIR / "model_metrics.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    return results


if __name__ == "__main__":
    run_models()
