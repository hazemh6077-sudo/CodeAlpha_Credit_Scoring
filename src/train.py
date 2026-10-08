import sys
from pathlib import Path
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from preprocessing import load_data, build_preprocessor, split_data

# Load data and split
X, y = load_data()
X_train, X_test, y_train, y_test = split_data(X, y)

models = {
    "logistic_regression": LogisticRegression(
        max_iter=1000, class_weight="balanced", random_state=42
    ),
    "random_forest": RandomForestClassifier(
        n_estimators=300, class_weight="balanced", random_state=42
    ),
}

best_name, best_cv_auc, best_pipe = None, 0, None

print("Evaluating candidate models using 5-Fold Cross-Validation on training set...")
for name, model in models.items():
    pipe = Pipeline([
        ("prep", build_preprocessor(X_train)),
        ("model", model),
    ])
    # Model selection based on Cross-Validation on X_train to prevent test data leakage
    cv_scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="roc_auc")
    mean_cv_auc = cv_scores.mean()
    print(f"{name}: 5-Fold CV ROC-AUC = {mean_cv_auc:.3f} (+/- {cv_scores.std():.3f})")

    if mean_cv_auc > best_cv_auc:
        best_name, best_cv_auc, best_pipe = name, mean_cv_auc, pipe

# Train the selected champion model on full training set
print(f"\nChampion model selected: {best_name} (CV ROC-AUC = {best_cv_auc:.3f})")
best_pipe.fit(X_train, y_train)

# Final unbiased test set evaluation
test_auc = roc_auc_score(y_test, best_pipe.predict_proba(X_test)[:, 1])
print(f"Final Test Set ROC-AUC = {test_auc:.3f}")

# Save the trained pipeline
model_save_path = PROJECT_ROOT / "models" / "credit_scoring_model.pkl"
model_save_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(best_pipe, model_save_path)
print(f"Saved model pipeline to {model_save_path}")