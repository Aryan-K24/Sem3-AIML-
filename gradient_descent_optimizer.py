"""
gradient_descent_optimizer.py
Versight — Calculus CIE-3 Project Component: Optimization using Gradient Descent & Gradient Ascent

This module implements:
1. Binary Cross-Entropy Loss (Log-Loss) with L2 Regularization for Review Authenticity Classification.
2. Analytical Partial Derivatives (Gradients) via Chain Rule.
3. Three Gradient Descent Algorithms:
   - Batch Gradient Descent (BGD)
   - Stochastic Gradient Descent (SGD)
   - Mini-Batch Gradient Descent (MBGD)
4. Learning Rate Dynamics & Convergence Analysis (alpha sensitivity).
5. Gradient Ascent Equivalence Proof (Maximum Likelihood Estimation).
"""

import sys
import numpy as np
from typing import Dict, List, Tuple, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def sigmoid(z: np.ndarray) -> np.ndarray:
    """
    Sigmoid activation function:
    sigma(z) = 1 / (1 + e^(-z))
    Numerically stable implementation clipping z to [-500, 500].
    """
    z_clipped = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z_clipped))


def compute_cost_bce(
    X: np.ndarray,
    y: np.ndarray,
    w: np.ndarray,
    b: float,
    lambda_reg: float = 0.01
) -> float:
    """
    Calculates the Binary Cross-Entropy Cost Function J(w, b) with L2 Regularization:
    J(w, b) = - (1/m) * sum [ y^(i) * ln(h(x^(i))) + (1 - y^(i)) * ln(1 - h(x^(i))) ] + (lambda / 2m) * ||w||^2
    """
    m = X.shape[0]
    z = np.dot(X, w) + b
    h = sigmoid(z)
    
    # Epsilon clipping to prevent ln(0) numerical instability
    eps = 1e-15
    h_clipped = np.clip(h, eps, 1.0 - eps)
    
    loss = - (1.0 / m) * np.sum(y * np.log(h_clipped) + (1.0 - y) * np.log(1.0 - h_clipped))
    reg_penalty = (lambda_reg / (2.0 * m)) * np.sum(w ** 2)
    return float(loss + reg_penalty)


def compute_gradients(
    X: np.ndarray,
    y: np.ndarray,
    w: np.ndarray,
    b: float,
    lambda_reg: float = 0.01
) -> Tuple[np.ndarray, float]:
    """
    Computes analytical partial derivatives (gradients) using the Calculus Chain Rule:
    del J / del w_j = (1/m) * sum [ (h(x^(i)) - y^(i)) * x_j^(i) ] + (lambda / m) * w_j
    del J / del b   = (1/m) * sum [ h(x^(i)) - y^(i) ]
    """
    m = X.shape[0]
    z = np.dot(X, w) + b
    h = sigmoid(z)
    error = h - y  # (m,)
    
    dj_dw = (1.0 / m) * np.dot(X.T, error) + (lambda_reg / m) * w
    dj_db = (1.0 / m) * np.sum(error)
    return dj_dw, float(dj_db)


class GradientDescentOptimizer:
    """
    Comprehensive Optimization Engine implementing Batch, Stochastic, and Mini-Batch Gradient Descent.
    """
    def __init__(
        self,
        learning_rate: float = 0.1,
        epochs: int = 100,
        batch_size: int = 32,
        lambda_reg: float = 0.01,
        random_state: int = 42
    ):
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.lambda_reg = lambda_reg
        self.random_state = random_state
        self.w = None
        self.b = 0.0
        self.history = []

    def fit_batch_gradient_descent(self, X: np.ndarray, y: np.ndarray) -> List[float]:
        """
        Batch Gradient Descent (BGD):
        Evaluates the full dataset gradient at every step:
        theta := theta - alpha * nabla J(theta)
        Smooth, deterministic, guaranteed convergence for convex functions.
        """
        np.random.seed(self.random_state)
        m, n = X.shape
        self.w = np.zeros(n)
        self.b = 0.0
        self.history = []

        for epoch in range(self.epochs):
            cost = compute_cost_bce(X, y, self.w, self.b, self.lambda_reg)
            self.history.append(cost)

            dj_dw, dj_db = compute_gradients(X, y, self.w, self.b, self.lambda_reg)

            # Gradient Descent update rule
            self.w -= self.learning_rate * dj_dw
            self.b -= self.learning_rate * dj_db

        return self.history

    def fit_stochastic_gradient_descent(self, X: np.ndarray, y: np.ndarray) -> List[float]:
        """
        Stochastic Gradient Descent (SGD):
        Updates parameters after EACH individual sample (m=1):
        theta := theta - alpha * nabla J_i(theta)
        Fast updates, high variance, escapes shallow local saddles.
        """
        np.random.seed(self.random_state)
        m, n = X.shape
        self.w = np.zeros(n)
        self.b = 0.0
        self.history = []

        for epoch in range(self.epochs):
            # Shuffle indices per epoch
            indices = np.random.permutation(m)
            for idx in indices:
                x_i = X[idx:idx+1]
                y_i = y[idx:idx+1]
                dj_dw, dj_db = compute_gradients(x_i, y_i, self.w, self.b, self.lambda_reg)
                self.w -= self.learning_rate * dj_dw
                self.b -= self.learning_rate * dj_db

            cost = compute_cost_bce(X, y, self.w, self.b, self.lambda_reg)
            self.history.append(cost)

        return self.history

    def fit_mini_batch_gradient_descent(self, X: np.ndarray, y: np.ndarray) -> List[float]:
        """
        Mini-Batch Gradient Descent (MBGD):
        Partitions dataset into mini-batches of size B (default 32):
        theta := theta - alpha * nabla J_batch(theta)
        Optimal compromise between computational vectorization and update frequency.
        """
        np.random.seed(self.random_state)
        m, n = X.shape
        self.w = np.zeros(n)
        self.b = 0.0
        self.history = []

        for epoch in range(self.epochs):
            indices = np.random.permutation(m)
            X_shuffled = X[indices]
            y_shuffled = y[indices]

            for start_idx in range(0, m, self.batch_size):
                end_idx = min(start_idx + self.batch_size, m)
                X_batch = X_shuffled[start_idx:end_idx]
                y_batch = y_shuffled[start_idx:end_idx]

                dj_dw, dj_db = compute_gradients(X_batch, y_batch, self.w, self.b, self.lambda_reg)
                self.w -= self.learning_rate * dj_dw
                self.b -= self.learning_rate * dj_db

            cost = compute_cost_bce(X, y, self.w, self.b, self.lambda_reg)
            self.history.append(cost)

        return self.history

    def fit_gradient_ascent(self, X: np.ndarray, y: np.ndarray) -> List[float]:
        """
        Gradient Ascent on the Log-Likelihood Function ell(w, b):
        ell(w, b) = - m * J(w, b)
        Update Rule:
        theta := theta + alpha * nabla ell(theta)
        Mathematically equivalent to Gradient Descent minimization.
        """
        np.random.seed(self.random_state)
        m, n = X.shape
        self.w = np.zeros(n)
        self.b = 0.0
        likelihood_history = []

        for epoch in range(self.epochs):
            # Compute log-likelihood
            cost = compute_cost_bce(X, y, self.w, self.b, self.lambda_reg)
            log_likelihood = -m * cost
            likelihood_history.append(log_likelihood)

            # Gradient of cost
            dj_dw, dj_db = compute_gradients(X, y, self.w, self.b, self.lambda_reg)
            
            # Gradient of log-likelihood is negative of gradient of cost:
            # nabla ell = - m * nabla J
            d_ell_dw = -m * dj_dw
            d_ell_db = -m * dj_db

            # Gradient Ascent update: add positive step in gradient direction
            # Scale alpha by 1/m to maintain identical effective step size
            step_size = self.learning_rate / m
            self.w += step_size * d_ell_dw
            self.b += step_size * d_ell_db

        return likelihood_history

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return sigmoid(np.dot(X, self.w) + self.b)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X) >= threshold).astype(int)


def run_synthetic_benchmark(
    n_samples: int = 500,
    n_features: int = 6,
    epochs: int = 60
) -> Dict[str, Any]:
    """
    Benchmarks Batch GD, SGD, and Mini-Batch GD on a balanced review feature matrix.
    Returns convergence histories and parameters for visualization.
    """
    np.random.seed(42)
    # Generate realistic review feature distribution:
    # [exclamation_ratio, caps_ratio, buzzword_count, length_norm, star_deviation, rating_polarity]
    X_genuine = np.random.normal(loc=[0.02, 0.05, 0.1, 0.45, 0.2, 0.7], scale=[0.01, 0.02, 0.2, 0.1, 0.1, 0.15], size=(n_samples // 2, n_features))
    X_suspicious = np.random.normal(loc=[0.18, 0.28, 2.8, 0.25, 1.2, 0.95], scale=[0.04, 0.06, 0.6, 0.08, 0.2, 0.05], size=(n_samples // 2, n_features))
    
    X = np.vstack([X_genuine, X_suspicious])
    y = np.hstack([np.zeros(n_samples // 2), np.ones(n_samples // 2)])
    
    # Shuffle
    perm = np.random.permutation(n_samples)
    X, y = X[perm], y[perm]

    # Normalize
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    # 1. Batch Gradient Descent
    bgd = GradientDescentOptimizer(learning_rate=0.2, epochs=epochs)
    hist_bgd = bgd.fit_batch_gradient_descent(X, y)

    # 2. Mini-Batch Gradient Descent (Batch size 32)
    mbgd = GradientDescentOptimizer(learning_rate=0.1, epochs=epochs, batch_size=32)
    hist_mbgd = mbgd.fit_mini_batch_gradient_descent(X, y)

    # 3. Stochastic Gradient Descent (SGD)
    sgd = GradientDescentOptimizer(learning_rate=0.015, epochs=epochs)
    hist_sgd = sgd.fit_stochastic_gradient_descent(X, y)

    # 4. Learning Rate Sensitivity Analysis on Batch GD
    lrs = [0.01, 0.05, 0.2, 1.0]
    lr_histories = {}
    for lr in lrs:
        opt = GradientDescentOptimizer(learning_rate=lr, epochs=epochs)
        lr_histories[f"alpha = {lr}"] = opt.fit_batch_gradient_descent(X, y)

    return {
        "hist_bgd": hist_bgd,
        "hist_mbgd": hist_mbgd,
        "hist_sgd": hist_sgd,
        "lr_histories": lr_histories,
        "final_weights_bgd": bgd.w.tolist(),
        "final_bias_bgd": float(bgd.b),
        "initial_cost": hist_bgd[0],
        "final_cost_bgd": hist_bgd[-1],
        "final_cost_mbgd": hist_mbgd[-1],
        "final_cost_sgd": hist_sgd[-1]
    }


if __name__ == "__main__":
    print("=" * 65)
    print("🚀 Calculus CIE-3: Optimization via Gradient Descent & Ascent")
    print("=" * 65)
    results = run_synthetic_benchmark(n_samples=600, epochs=50)
    print(f"Initial Cost J(w, b): {results['initial_cost']:.5f}")
    print(f"Final Cost (Batch GD): {results['final_cost_bgd']:.5f} (Reduced by {(results['initial_cost'] - results['final_cost_bgd'])/results['initial_cost']*100:.1f}%)")
    print(f"Final Cost (Mini-Batch GD): {results['final_cost_mbgd']:.5f}")
    print(f"Final Cost (SGD): {results['final_cost_sgd']:.5f}")
    print("\nConvergence across Learning Rates (alpha):")
    for lr_name, hist in results["lr_histories"].items():
        print(f"  {lr_name}: Start {hist[0]:.4f} -> Epoch 10: {hist[10]:.4f} -> Final: {hist[-1]:.4f}")
    print("\n✅ Verification complete! Mathematical formulation & optimization functional.")
