"""Analysis service for statistical operations with real ML."""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
    r2_score,
    mean_squared_error,
    mean_absolute_error,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from scipy import stats
import json
import warnings

from app.schemas.analysis import (
    DescriptiveRequest,
    DescriptiveAnalysisResponse,
    RegressionRequest,
    RegressionResult,
    PCARequest,
    PCAResult,
    ClassificationRequest,
    ClassificationResult,
    ClusteringRequest,
    ClusteringResult,
)
from app.models.processed_data import ProcessedData

warnings.filterwarnings("ignore")

MAX_ROWS = 5000


class AnalysisService:
    """Service for statistical analysis operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _load_dataset(self, dataset_id: int) -> Optional[pd.DataFrame]:
        """Load dataset from database with row limit for memory safety."""
        result = await self.db.execute(
            select(ProcessedData).where(ProcessedData.dataset_id == dataset_id)
        )
        rows = result.scalars().all()
        if not rows:
            return None
        data_list = []
        for row in rows:
            record = {"id": row.id, "region": row.region, "indicator": row.indicator}
            if row.data:
                try:
                    record.update(json.loads(row.data))
                except:
                    pass
            data_list.append(record)
        df = pd.DataFrame(data_list)
        if len(df) > MAX_ROWS:
            df = df.sample(n=MAX_ROWS, random_state=42)
        return df

    async def descriptive_analysis(
        self, request: DescriptiveRequest
    ) -> DescriptiveAnalysisResponse:
        """Perform descriptive statistical analysis."""
        df = await self._load_dataset(request.dataset_id)
        if df is None or df.empty:
            return DescriptiveAnalysisResponse(
                statistics=[],
                correlations=None,
                plot_data=None,
            )
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return DescriptiveAnalysisResponse(
                statistics=[],
                correlations=None,
                plot_data=None,
            )
        desc = df[numeric_cols].describe().to_dict()
        statistics = [
            {"column": col, "stats": stats}
            for col, stats in desc.items()
        ]
        corr = df[numeric_cols].corr().to_dict() if len(numeric_cols) > 1 else None
        plot_data = {
            "histograms": {
                col: df[col].dropna().head(100).tolist()
                for col in numeric_cols[:5]
            }
        }
        return DescriptiveAnalysisResponse(
            statistics=statistics,
            correlations=corr,
            plot_data=plot_data,
        )

    async def regression_analysis(self, request: RegressionRequest) -> RegressionResult:
        """Perform regression analysis with real sklearn."""
        df = await self._load_dataset(request.dataset_id)
        if df is None or df.empty:
            return RegressionResult(
                intercept=0.0,
                coefficients=[],
                metrics=None,
                diagnostics=None,
                predictions=[],
                residuals=[],
                actual_values=[],
                plot_data=None,
                method=request.method,
                warning_messages=["No data available"],
            )
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return RegressionResult(
                intercept=0.0,
                coefficients=[],
                metrics=None,
                diagnostics=None,
                predictions=[],
                residuals=[],
                actual_values=[],
                plot_data=None,
                method=request.method,
                warning_messages=["Need at least 2 numeric columns"],
            )
        target = request.target_column or numeric_cols[-1]
        features = [c for c in numeric_cols if c != target]
        if request.feature_columns:
            features = [f for f in request.feature_columns if f in numeric_cols]
        if not features:
            features = [numeric_cols[0]]
        X = df[features].fillna(0).values
        y = df[target].fillna(0).values
        if len(X) < 10:
            return RegressionResult(
                intercept=0.0,
                coefficients=[],
                metrics=None,
                diagnostics=None,
                predictions=[],
                residuals=[],
                actual_values=[],
                plot_data=None,
                method=request.method,
                warning_messages=["Insufficient data points"],
            )
        model = {
            "linear": LinearRegression(),
            "ridge": Ridge(alpha=1.0),
            "lasso": Lasso(alpha=1.0),
            "elasticnet": ElasticNet(alpha=1.0, l1_ratio=0.5),
        }.get(request.method, LinearRegression())
        model.fit(X, y)
        y_pred = model.predict(X)
        residuals = y - y_pred
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y, y_pred)
        metrics = {
            "r2_score": round(r2, 4),
            "mse": round(mse, 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
        }
        coefficients = (
            list(model.coef_) if hasattr(model, "coef_") else []
        )
        intercept = float(model.intercept_) if hasattr(model, "intercept_") else 0.0
        diagnostics = {
            "skewness": round(float(stats.skew(residuals)), 4),
            "kurtosis": round(float(stats.kurtosis(residuals)), 4),
        }
        return RegressionResult(
            intercept=intercept,
            coefficients=coefficients,
            metrics=metrics,
            diagnostics=diagnostics,
            predictions=y_pred[:50].tolist(),
            residuals=residuals[:50].tolist(),
            actual_values=y[:50].tolist(),
            plot_data={
                "scatter": {
                    "x": y_pred.tolist()[:100],
                    "y": y.tolist()[:100],
                }
            },
            method=request.method,
            warning_messages=[],
        )

    async def pca_analysis(self, request: PCARequest) -> PCAResult:
        """Perform PCA analysis with real sklearn."""
        df = await self._load_dataset(request.dataset_id)
        if df is None or df.empty:
            return PCAResult(
                n_components=2,
                components=[],
                individuals=[],
                correlation_circle=None,
                scree_plot_data={},
                biplot_data=None,
                explained_variance={},
            )
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return PCAResult(
                n_components=2,
                components=[],
                individuals=[],
                correlation_circle=None,
                scree_plot_data={},
                biplot_data=None,
                explained_variance={},
            )
        features = request.feature_columns or numeric_cols
        features = [f for f in features if f in numeric_cols]
        if len(features) < 2:
            return PCAResult(
                n_components=2,
                components=[],
                individuals=[],
                correlation_circle=None,
                scree_plot_data={},
                biplot_data=None,
                explained_variance={},
            )
        X = df[features].fillna(0).values
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        n_comp = min(request.n_components or 2, len(features))
        pca = PCA(n_components=n_comp)
        components = pca.fit_transform(X_scaled)
        explained_var = pca.explained_variance_ratio_
        return PCAResult(
            n_components=n_comp,
            components=pca.components_.tolist(),
            individuals=components[:100].tolist(),
            correlation_circle={
                "x": pca.components_[0].tolist() if n_comp > 0 else [],
                "y": pca.components_[1].tolist() if n_comp > 1 else [],
                "labels": features,
            },
            scree_plot_data={
                "components": list(range(1, len(explained_var) + 1)),
                "variance": explained_var.tolist(),
            },
            biplot_data={
                "scores": components[:50].tolist(),
                "loadings": pca.components_.tolist(),
            },
            explained_variance={
                "explained_variance_ratio": explained_var.tolist(),
                "cumulative": np.cumsum(explained_var).tolist(),
            },
        )

    async def classification_analysis(
        self, request: ClassificationRequest
    ) -> ClassificationResult:
        """Perform supervised classification with real sklearn."""
        df = await self._load_dataset(request.dataset_id)
        if df is None or df.empty:
            return ClassificationResult(
                algorithm=request.algorithm,
                overall_metrics=None,
                class_metrics=[],
                confusion_matrix=None,
                roc_curve_data=None,
                feature_importances=None,
                grid_search_results=None,
                best_params=None,
                cross_validation_scores=None,
            )
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        if not numeric_cols or not cat_cols:
            return ClassificationResult(
                algorithm=request.algorithm,
                overall_metrics=None,
                class_metrics=[],
                confusion_matrix=None,
                roc_curve_data=None,
                feature_importances=None,
                grid_search_results=None,
                best_params=None,
                cross_validation_scores=None,
            )
        target_col = request.target_column or cat_cols[0]
        if target_col not in df.columns:
            return ClassificationResult(
                algorithm=request.algorithm,
                overall_metrics=None,
                class_metrics=[],
                confusion_matrix=None,
                roc_curve_data=None,
                feature_importances=None,
                grid_search_results=None,
                best_params=None,
                cross_validation_scores=None,
            )
        features = [c for c in numeric_cols if c != target_col]
        if request.feature_columns:
            features = [f for f in request.feature_columns if f in numeric_cols]
        if not features:
            return ClassificationResult(
                algorithm=request.algorithm,
                overall_metrics=None,
                class_metrics=[],
                confusion_matrix=None,
                roc_curve_data=None,
                feature_importances=None,
                grid_search_results=None,
                best_params=None,
                cross_validation_scores=None,
            )
        le = LabelEncoder()
        y = le.fit_transform(df[target_col].astype(str))
        X = df[features].fillna(0).values
        if len(np.unique(y)) < 2:
            return ClassificationResult(
                algorithm=request.algorithm,
                overall_metrics=None,
                class_metrics=[],
                confusion_matrix=None,
                roc_curve_data=None,
                feature_importances=None,
                grid_search_results=None,
                best_params=None,
                cross_validation_scores=None,
            )
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.svm import SVC
        from sklearn.neighbors import KNeighborsClassifier
        models = {
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "gradient_boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "svm": SVC(kernel="rbf", probability=True, random_state=42),
            "knn": KNeighborsClassifier(n_neighbors=5),
        }
        model = models.get(request.algorithm, RandomForestClassifier(n_estimators=100))
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
        rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        cm = confusion_matrix(y_test, y_pred).tolist()
        cv_scores = cross_val_score(model, X, y, cv=5).tolist()
        feature_importances = (
            model.feature_importances_.tolist() if hasattr(model, "feature_importances_") else None
        )
        return ClassificationResult(
            algorithm=request.algorithm,
            overall_metrics={
                "accuracy": round(acc, 4),
                "precision": round(prec, 4),
                "recall": round(rec, 4),
                "f1_score": round(f1, 4),
            },
            class_metrics=[
                {"class": str(c), "precision": 0.0, "recall": 0.0, "f1": 0.0}
                for c in le.classes_
            ],
            confusion_matrix=cm,
            roc_curve_data=None,
            feature_importances=feature_importances,
            grid_search_results=None,
            best_params=None,
            cross_validation_scores=cv_scores,
        )

    async def clustering_analysis(self, request: ClusteringRequest) -> ClusteringResult:
        """Perform unsupervised clustering with real sklearn."""
        df = await self._load_dataset(request.dataset_id)
        if df is None or df.empty:
            return ClusteringResult(
                algorithm=request.algorithm,
                n_clusters=3,
                clusters=[],
                metrics=None,
                optimal_k_analysis=None,
                elbow_plot_data=None,
                silhouette_plot_data=None,
                cluster_visualization=None,
            )
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return ClusteringResult(
                algorithm=request.algorithm,
                n_clusters=3,
                clusters=[],
                metrics=None,
                optimal_k_analysis=None,
                elbow_plot_data=None,
                silhouette_plot_data=None,
                cluster_visualization=None,
            )
        features = request.feature_columns or numeric_cols
        features = [f for f in features if f in numeric_cols]
        if len(features) < 2:
            return ClusteringResult(
                algorithm=request.algorithm,
                n_clusters=3,
                clusters=[],
                metrics=None,
                optimal_k_analysis=None,
                elbow_plot_data=None,
                silhouette_plot_data=None,
                cluster_visualization=None,
            )
        X = df[features].fillna(0).values
        n_clusters = request.n_clusters or 3
        if request.algorithm == "kmeans":
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        elif request.algorithm == "dbscan":
            model = DBSCAN(eps=0.5, min_samples=5)
            n_clusters = len(set(model.fit_predict(X))) - (1 if -1 in model.labels_ else 0)
        elif request.algorithm == "hierarchical":
            model = AgglomerativeClustering(n_clusters=n_clusters)
        elif request.algorithm == "gmm":
            model = GaussianMixture(n_components=n_clusters, random_state=42)
        else:
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = model.fit_predict(X)
        sil = silhouette_score(X, labels) if len(set(labels)) > 1 else 0
        cal = calinski_harabasz_score(X, labels) if len(set(labels)) > 1 else 0
        db = davies_bouldin_score(X, labels) if len(set(labels)) > 1 else 0
        if request.find_optimal_k and request.algorithm == "kmeans":
            inertias = []
            silhouettes = []
            for k in range(2, min(10, len(X))):
                km = KMeans(n_clusters=k, random_state=42, n_init=10)
                lbls = km.fit_predict(X)
                inertias.append(km.inertia_)
                silhouettes.append(silhouette_score(X, lbls))
            elbow_data = {"k": list(range(2, len(inertias) + 2)), "inertia": inertias}
            sil_data = {"k": list(range(2, len(silhouettes) + 2)), "silhouette": silhouettes}
        else:
            elbow_data = None
            sil_data = None
        return ClusteringResult(
            algorithm=request.algorithm,
            n_clusters=n_clusters,
            clusters=labels[:100].tolist(),
            metrics={
                "silhouette": round(sil, 4),
                "calinski_harabasz": round(cal, 4),
                "davies_bouldin": round(db, 4),
            },
            optimal_k_analysis={"suggested_k": n_clusters} if request.find_optimal_k else None,
            elbow_plot_data=elbow_data,
            silhouette_plot_data=sil_data,
            cluster_visualization={
                "x": X[:100, 0].tolist() if X.shape[1] > 0 else [],
                "y": X[:100, 1].tolist() if X.shape[1] > 1 else [],
                "labels": labels[:100].tolist(),
            },
        )

    async def get_result(self, result_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a previous analysis result."""
        return None
