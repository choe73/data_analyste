"""Specialized analyzer implementations for different analysis types."""

import pandas as pd
import numpy as np
from typing import Dict, Any
from scipy import stats
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.cluster import KMeans
from statsmodels.stats.outliers_influence import variance_inflation_factor

from app.services.base_analyzer import BaseAnalyzer


class DescriptiveAnalyzer(BaseAnalyzer):
    """
    Analyzer for descriptive statistics.
    
    Demonstrates:
    - Inheritance: Extends BaseAnalyzer
    - Polymorphism: Implements execute() method
    - Robustness: Comprehensive statistical calculations
    """

    async def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute descriptive analysis.
        
        Args:
            df: Input DataFrame
            params: Should contain 'columns' key with list of columns to analyze
            
        Returns:
            Dictionary with descriptive statistics
        """
        self._validate_dataframe(df)

        columns = params.get("columns")
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        self._validate_columns(df, columns)

        # Select only numeric columns
        numeric_df = df[columns].select_dtypes(include=[np.number])

        if numeric_df.empty:
            raise ValueError("No numeric columns found for analysis")

        # Calculate comprehensive statistics
        stats_dict = {}
        for col in numeric_df.columns:
            data = numeric_df[col].dropna()

            if len(data) < 2:
                continue

            # Basic statistics
            stats_dict[col] = {
                "count": len(data),
                "mean": float(data.mean()),
                "median": float(data.median()),
                "std": float(data.std()),
                "min": float(data.min()),
                "max": float(data.max()),
                "q25": float(data.quantile(0.25)),
                "q75": float(data.quantile(0.75)),
                "iqr": float(data.quantile(0.75) - data.quantile(0.25)),
            }

            # Normality test (Shapiro-Wilk)
            if len(data) <= 5000:  # Shapiro-Wilk works best with n <= 5000
                stat, p_value = stats.shapiro(data)
                stats_dict[col]["shapiro_wilk_p_value"] = float(p_value)
                stats_dict[col]["is_normal"] = p_value > 0.05

            # Skewness and Kurtosis
            stats_dict[col]["skewness"] = float(stats.skew(data))
            stats_dict[col]["kurtosis"] = float(stats.kurtosis(data))

        # Correlation matrix (Spearman)
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr(method="spearman")
            stats_dict["correlation_matrix"] = corr_matrix.to_dict()

        return self._prepare_result(
            algorithm="Descriptive Statistics",
            metrics={"columns_analyzed": len(numeric_df.columns)},
            data=stats_dict,
        )


class RegressionAnalyzer(BaseAnalyzer):
    """
    Analyzer for linear regression analysis.
    
    Demonstrates:
    - Inheritance: Extends BaseAnalyzer
    - Polymorphism: Implements execute() method
    - Robustness: Multiple regression models with diagnostics
    """

    async def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute regression analysis.
        
        Args:
            df: Input DataFrame
            params: Must contain 'target_column' and 'feature_columns'
            
        Returns:
            Dictionary with regression results
        """
        self._validate_dataframe(df)

        target = params.get("target_column")
        features = params.get("feature_columns", [])
        model_type = params.get("model_type", "linear")  # linear, ridge, lasso

        if not target or not features:
            raise ValueError("target_column and feature_columns are required")

        self._validate_columns(df, [target] + features)

        # Clean data
        df_clean = self._clean_data(df, [target] + features)

        if len(df_clean) < 3:
            raise ValueError("Not enough data after cleaning")

        X = df_clean[features].values
        y = df_clean[target].values

        # Select model
        if model_type == "ridge":
            model = Ridge(alpha=1.0)
        elif model_type == "lasso":
            model = Lasso(alpha=0.1)
        else:
            model = LinearRegression()

        # Fit model
        model.fit(X, y)
        predictions = model.predict(X)

        # Calculate metrics
        r2 = float(model.score(X, y))
        rmse = float(np.sqrt(np.mean((y - predictions) ** 2)))
        mae = float(np.mean(np.abs(y - predictions)))

        # Residuals analysis
        residuals = y - predictions
        durbin_watson = float(
            np.sum(np.diff(residuals) ** 2) / np.sum(residuals ** 2)
        )

        # VIF (Variance Inflation Factor) for multicollinearity
        vif_data = {}
        try:
            for i, col in enumerate(features):
                vif = variance_inflation_factor(X, i)
                vif_data[col] = float(vif)
        except:
            pass

        # Prepare visualization data
        plot_data = {
            "x": df_clean[features[0]].tolist() if features else [],
            "y": y.tolist(),
            "predictions": predictions.tolist(),
        }

        return self._prepare_result(
            algorithm=f"{model_type.capitalize()} Regression",
            metrics={
                "r2_score": round(r2, 4),
                "rmse": round(rmse, 4),
                "mae": round(mae, 4),
                "durbin_watson": round(durbin_watson, 4),
            },
            data={
                "coefficients": dict(zip(features, np.round(model.coef_, 4).tolist())),
                "intercept": float(model.intercept_),
                "vif": vif_data,
            },
            visualizations={"plot_data": plot_data},
        )


class PCAAnalyzer(BaseAnalyzer):
    """
    Analyzer for Principal Component Analysis.
    
    Demonstrates:
    - Inheritance: Extends BaseAnalyzer
    - Polymorphism: Implements execute() method
    - Robustness: Proper standardization and variance analysis
    """

    async def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute PCA analysis.
        
        Args:
            df: Input DataFrame
            params: Should contain 'columns' and optionally 'n_components'
            
        Returns:
            Dictionary with PCA results
        """
        self._validate_dataframe(df)

        columns = params.get("columns")
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        self._validate_columns(df, columns)

        # Clean data
        df_clean = self._clean_data(df, columns)

        if len(df_clean) < 2:
            raise ValueError("Not enough data after cleaning")

        X = df_clean[columns].values

        # Standardization (MANDATORY for PCA)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Determine optimal number of components
        n_components = params.get("n_components")
        if not n_components:
            n_components = min(len(columns), len(df_clean) - 1)
            n_components = min(n_components, 3)  # Default to 3 if not specified

        # Apply PCA
        pca = PCA(n_components=n_components)
        components = pca.fit_transform(X_scaled)

        # Calculate cumulative variance
        variance_ratio = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(variance_ratio)

        # Prepare visualization data
        plot_data = {
            "components": components.tolist(),
            "variance_ratio": variance_ratio.tolist(),
            "cumulative_variance": cumulative_variance.tolist(),
        }

        return self._prepare_result(
            algorithm="Principal Component Analysis (PCA)",
            metrics={
                "n_components": n_components,
                "total_variance_explained": round(float(cumulative_variance[-1]), 4),
            },
            data={
                "loadings": pca.components_.tolist(),
                "explained_variance": variance_ratio.tolist(),
                "cumulative_variance": cumulative_variance.tolist(),
            },
            visualizations={"plot_data": plot_data},
        )


class ClassificationAnalyzer(BaseAnalyzer):
    """
    Analyzer for supervised classification.
    
    Demonstrates:
    - Inheritance: Extends BaseAnalyzer
    - Polymorphism: Implements execute() method
    - Robustness: Train/test split, hyperparameter tuning, multiple metrics
    """

    async def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute classification analysis.
        
        Args:
            df: Input DataFrame
            params: Must contain 'target_column' and 'feature_columns'
            
        Returns:
            Dictionary with classification results
        """
        self._validate_dataframe(df)

        target = params.get("target_column")
        features = params.get("feature_columns", [])

        if not target or not features:
            raise ValueError("target_column and feature_columns are required")

        self._validate_columns(df, [target] + features)

        # Clean data
        df_clean = self._clean_data(df, [target] + features)

        if len(df_clean) < 10:
            raise ValueError("Not enough data for classification")

        X = df_clean[features].values
        y = df_clean[target].values

        # Train/test split (80/20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train Random Forest with GridSearchCV
        param_grid = {
            "n_estimators": [50, 100],
            "max_depth": [5, 10, 15],
        }

        rf = RandomForestClassifier(random_state=42)
        grid_search = GridSearchCV(rf, param_grid, cv=3)
        grid_search.fit(X_train, y_train)

        # Best model
        best_model = grid_search.best_estimator_

        # Predictions
        y_pred = best_model.predict(X_test)

        # Metrics
        cm = confusion_matrix(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        recall = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

        return self._prepare_result(
            algorithm="Random Forest Classification",
            metrics={
                "precision": round(float(precision), 4),
                "recall": round(float(recall), 4),
                "f1_score": round(float(f1), 4),
                "best_params": grid_search.best_params_,
            },
            data={
                "confusion_matrix": cm.tolist(),
                "feature_importance": dict(
                    zip(features, best_model.feature_importances_.tolist())
                ),
            },
        )


class ClusteringAnalyzer(BaseAnalyzer):
    """
    Analyzer for unsupervised clustering.
    
    Demonstrates:
    - Inheritance: Extends BaseAnalyzer
    - Polymorphism: Implements execute() method
    - Robustness: Elbow method for optimal k determination
    """

    async def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute clustering analysis.
        
        Args:
            df: Input DataFrame
            params: Should contain 'columns' and optionally 'n_clusters'
            
        Returns:
            Dictionary with clustering results
        """
        self._validate_dataframe(df)

        columns = params.get("columns")
        if not columns:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        self._validate_columns(df, columns)

        # Clean data
        df_clean = self._clean_data(df, columns)

        if len(df_clean) < 3:
            raise ValueError("Not enough data for clustering")

        X = df_clean[columns].values

        # Standardization
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Determine optimal k using Elbow Method
        n_clusters = params.get("n_clusters")
        if not n_clusters:
            inertias = []
            silhouette_scores = []
            K_range = range(2, min(10, len(df_clean)))

            for k in K_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(X_scaled)
                inertias.append(kmeans.inertia_)

            # Simple elbow detection: find the "knee"
            n_clusters = 3  # Default
            if len(inertias) > 2:
                # Calculate second derivative
                second_derivative = np.diff(inertias, n=2)
                if len(second_derivative) > 0:
                    n_clusters = int(np.argmax(second_derivative)) + 2

        # Final clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)

        # Calculate silhouette score
        from sklearn.metrics import silhouette_score

        silhouette = silhouette_score(X_scaled, clusters)

        return self._prepare_result(
            algorithm="K-Means Clustering",
            metrics={
                "n_clusters": n_clusters,
                "inertia": round(float(kmeans.inertia_), 4),
                "silhouette_score": round(float(silhouette), 4),
            },
            data={
                "cluster_centers": kmeans.cluster_centers_.tolist(),
                "cluster_labels": clusters.tolist(),
            },
        )
