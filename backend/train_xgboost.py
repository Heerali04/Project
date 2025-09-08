import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("zoonotic_train_large.csv")
df.columns = df.columns.str.strip()

# Target column
target_col = "label"
X = df.drop(target_col, axis=1)
y = df[target_col]

# Encode labels
label_encoder = LabelEncoder()
y_enc = label_encoder.fit_transform(y)

# Inject Noise (flip 5% of labels)
np.random.seed(42)
n_samples = len(y_enc)
n_noisy = int(0.05 * n_samples)

noisy_indices = np.random.choice(n_samples, n_noisy, replace=False)
for idx in noisy_indices:
    current_label = y_enc[idx]
    possible_labels = [l for l in np.unique(y_enc) if l != current_label]
    y_enc[idx] = np.random.choice(possible_labels)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
)

# Train model
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.1,
    max_depth=6,
    random_state=42,
    use_label_encoder=False,
    eval_metric="mlogloss"
)
model.fit(X_train, y_train)

# Evaluate and print only accuracy
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"{acc:.4f}")
