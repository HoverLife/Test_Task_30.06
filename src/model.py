import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import numpy as np

#загружаю обучающую выборку
df = pd.read_csv('data/processed_dataset.csv', parse_dates=['reportdate'])

#фичи и таргет
X = df[['1110', '1150', '2110']]
y = df['default_flag']

#лог.рег.
model = LogisticRegression(solver='liblinear')
model.fit(X, y)
y_scores = model.predict_proba(X)[:, 1]

#GINI встроенная + собственная
auc = roc_auc_score(y, y_scores)
gini_builtin = 2 * auc - 1

fpr, tpr, _ = roc_curve(y, y_scores)
gini_manual = np.trapezoid(tpr, fpr) * 2 - 1

#вывожу метрики при запуске файла
print(f"AUC: {auc:.4f}")
print(f"Gini (встроенный): {gini_builtin:.4f}")
print(f"Gini (собственный): {gini_manual:.4f}")

#строю ROC-кривую на графике
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f'AUC = {auc:.3f}')
plt.plot([0, 1], [0, 1], 'k--', label='Random')
plt.title('ROC-кривая логистической регрессии')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.grid(True)
plt.legend(loc='lower right')
plt.tight_layout()

#для удобства вывел GINI возле графика
plt.figtext(0.99, 0.01, f'Gini = {gini_manual:.4f}', horizontalalignment='right')

plt.savefig('results/roc_curve.png')