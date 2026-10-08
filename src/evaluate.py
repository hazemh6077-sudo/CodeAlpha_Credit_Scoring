import sys
from pathlib import Path
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report, confusion_matrix, ConfusionMatrixDisplay,
    roc_auc_score, RocCurveDisplay,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from preprocessing import load_data, split_data

X, y = load_data()
X_train, X_test, y_train, y_test = split_data(X, y)

model_path = PROJECT_ROOT / "models" / "credit_scoring_model.pkl"
model = joblib.load(model_path)

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("=== Classification Report ===")
print(classification_report(y_test, y_pred, target_names=["bad", "good"]))
print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")

models_dir = PROJECT_ROOT / "models"
models_dir.mkdir(parents=True, exist_ok=True)

# Confusion Matrix
cm_display = ConfusionMatrixDisplay(confusion_matrix(y_test, y_pred), display_labels=["bad", "good"])
cm_display.plot(cmap="Blues")
plt.title("Confusion Matrix - Test Set")
plt.tight_layout()
cm_path = models_dir / "confusion_matrix.png"
plt.savefig(cm_path, dpi=150)
plt.close()

# ROC Curve
RocCurveDisplay.from_predictions(y_test, y_proba)
plt.title("ROC Curve - Test Set")
plt.tight_layout()
roc_path = models_dir / "roc_curve.png"
plt.savefig(roc_path, dpi=150)
plt.close()

print(f"Saved evaluation plots to: {models_dir}")