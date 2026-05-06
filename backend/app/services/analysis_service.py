"""Analysis service - statistical operations using existing ML stack."""

import json
import warnings
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.preprocessing import PolynomialFeatures, StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score, davies_bouldin_score,
    r2_score, mean_squared_error, mean_absolute_error,
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
)
from sklearn.model_selection import train_test_split, cross_val_score
from scipy import stats

from app.schemas.analysis import (
    DescriptiveRequest, DescriptiveAnalysisResponse, DescriptiveResult, CorrelationMatrix,
    RegressionRequest, RegressionResult, RegressionMetrics, RegressionDiagnostics, CoefficientInfo,
    PCARequest, PCAResult, PCAComponent, PCAIndividual,
    ClassificationRequest, ClassificationResult, ClassificationMetrics, ClassMetrics, ConfusionMatrix,
    ClusteringRequest, ClusteringResult, ClusteringMetrics, ClusterInfo,
)
from app.models.processed_data import ProcessedData
from app.models.raw_data import RawData
from app.models.form import DataImport

warnings.filterwarnings("ignore")
MAX_ROWS = 5000


class AnalysisService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _load_dataset(self, dataset_id: int) -> Optional[pd.DataFrame]:
        """Load dataset - negative IDs = user imports, positive IDs = datasets table."""
        # Negative ID = user import (DataImport table)
        if dataset_id < 0:
            real_id = -dataset_id
            result = await self.db.execute(
                select(DataImport).where(DataImport.id == real_id)
            )
            imp = result.scalar_one_or_none()
            if imp:
                # Try data_json first (persistent, survives restarts)
                if imp.data_json:
                    try:
                        df = pd.DataFrame(imp.data_json)
                        if len(df) > MAX_ROWS:
                            df = df.sample(n=MAX_ROWS, random_state=42)
                        return df
                    except Exception:
                        pass
                # Fallback: try file on disk
                if imp.storage_path:
                    import os
                    if os.path.exists(imp.storage_path):
                        ext = os.path.splitext(imp.storage_path)[1].lower()
                        try:
                            if ext == ".csv":
                                df = pd.read_csv(imp.storage_path)
                            elif ext in (".xlsx", ".xls"):
                                df = pd.read_excel(imp.storage_path)
                            else:
                                df = pd.read_json(imp.storage_path)
                            if len(df) > MAX_ROWS:
                                df = df.sample(n=MAX_ROWS, random_state=42)
                            return df
                        except Exception:
                            pass
            return None

        # Positive ID = Dataset table (API-collected data)
        from app.models.dataset import Dataset as DatasetModel
        ds_result = await self.db.execute(
            select(DatasetModel).where(DatasetModel.id == dataset_id)
        )
        ds = ds_result.scalar_one_or_none()
        if not ds:
            return None

        # Try to load from file_path if available
        if ds.file_path:
            import os
            if os.path.exists(ds.file_path):
                try:
                    return pd.read_csv(ds.file_path)
                except Exception:
                    pass

        # Load from RawData (JSON) by dataset name
        result = await self.db.execute(
            select(RawData).where(RawData.dataset_name == ds.name).limit(MAX_ROWS)
        )
        raw_rows = result.scalars().all()
        if raw_rows:
            try:
                # Combine all raw data - each row has a data field that's a dict
                all_data = []
                for row in raw_rows:
                    # row.data is already a dict (SQLAlchemy deserializes JSON)
                    if isinstance(row.data, dict):
                        all_data.append(row.data)
                    elif isinstance(row.data, list):
                        all_data.extend(row.data)
                
                if all_data:
                    df = pd.DataFrame(all_data)
                    # Convert date columns to datetime
                    for col in df.columns:
                        if 'date' in col.lower():
                            try:
                                df[col] = pd.to_datetime(df[col])
                            except Exception:
                                pass
                    if len(df) > MAX_ROWS:
                        df = df.sample(n=MAX_ROWS, random_state=42)
                    return df
            except Exception as e:
                # Log the error for debugging
                import traceback
                print(f"Error loading from RawData: {e}")
                traceback.print_exc()
                pass

        # Fallback: load from ProcessedData by domain
        if ds.domain:
            result = await self.db.execute(
                select(ProcessedData).where(ProcessedData.domain == ds.domain).limit(MAX_ROWS)
            )
            rows = result.scalars().all()
            if rows:
                data_list = []
                for row in rows:
                    # Build base record
                    record = {
                        "region": row.region,
                        "indicator": row.indicator,
                        "value": float(row.numeric_value) if row.numeric_value else None,
                        "date": row.date_value,
                        "text_value": row.text_value,
                    }
                    
                    # Extract meta_info fields if available (for meteorological data)
                    if row.meta_info and isinstance(row.meta_info, dict):
                        # Map common meteorological fields
                        if "temperature" in row.meta_info:
                            record["temp"] = row.meta_info["temperature"]
                        if "T2M" in row.meta_info:
                            record["temp"] = row.meta_info["T2M"]
                        # Temperature is in value column, so map it
                        if record.get("value") is not None:
                            record["temp"] = record["value"]
                        
                        if "precipitation" in row.meta_info:
                            record["precip"] = row.meta_info["precipitation"]
                        if "PRECTOTCORR" in row.meta_info:
                            record["precip"] = row.meta_info["PRECTOTCORR"]
                        
                        if "humidity" in row.meta_info:
                            record["humidity"] = row.meta_info["humidity"]
                        if "RH2M" in row.meta_info:
                            record["humidity"] = row.meta_info["RH2M"]
                        
                        if "wind_speed" in row.meta_info:
                            record["wind"] = row.meta_info["wind_speed"]
                        if "WS10M" in row.meta_info:
                            record["wind"] = row.meta_info["WS10M"]
                        
                        # Add any other meta fields
                        for key, val in row.meta_info.items():
                            if key not in record and isinstance(val, (int, float)):
                                record[key] = val
                    
                    data_list.append(record)
                
                if data_list:
                    df = pd.DataFrame(data_list)
                    # Ensure date column is datetime
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    return df

        return None

    async def descriptive_analysis(self, request: DescriptiveRequest) -> DescriptiveAnalysisResponse:
        df = await self._load_dataset(request.dataset_id)
        if df is None or df.empty:
            return DescriptiveAnalysisResponse(statistics=[], correlations=None, plot_data=None)

        # Filter to requested columns if specified
        cols = [c for c in request.columns if c in df.columns] if request.columns else df.columns.tolist()
        numeric_cols = df[cols].select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_cols:
            return DescriptiveAnalysisResponse(statistics=[], correlations=None, plot_data=None)

        statistics = []
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) == 0:
                continue
            n = len(series)
            mean = float(series.mean())
            std = float(series.std())
            # Confidence interval
            ci = stats.t.interval(request.confidence_level, df=n - 1, loc=mean, scale=stats.sem(series))
            statistics.append(DescriptiveResult(
                column=col,
                count=n,
                mean=round(mean, 4),
                std=round(std, 4),
                min=round(float(series.min()), 4),
                q25=round(float(series.quantile(0.25)), 4),
                median=round(float(series.median()), 4),
                q75=round(float(series.quantile(0.75)), 4),
                max=round(float(series.max()), 4),
                ci_lower=round(float(ci[0]), 4),
                ci_upper=round(float(ci[1]), 4),
                skewness=round(float(stats.skew(series)), 4),
                kurtosis=round(float(stats.kurtosis(series)), 4),
                missing_count=int(df[col].isnull().sum()),
                unique_count=int(df[col].nunique()),
            ))

        # Correlation matrix
        corr_result = None
        if len(numeric_cols) > 1:
            corr_df = df[numeric_cols].corr(method="pearson")
            corr_result = CorrelationMatrix(
                columns=numeric_cols,
                values=corr_df.values.tolist(),
                method="pearson",
            )

        # Plot data: histograms + boxplot data
        plot_data = {
            "histograms": {col: df[col].dropna().tolist()[:500] for col in numeric_cols[:6]},
            "boxplot": {
                col: {
                    "min": float(df[col].min()), "q1": float(df[col].quantile(0.25)),
                    "median": float(df[col].median()), "q3": float(df[col].quantile(0.75)),
                    "max": float(df[col].max()),
                } for col in numeric_cols[:6]
            },
        }

        return DescriptiveAnalysisResponse(statistics=statistics, correlations=corr_result, plot_data=plot_data)

    async def regression_analysis(self, request: RegressionRequest) -> RegressionResult:
        df = await self._load_dataset(request.dataset_id)
        warnings_list = []

        if df is None or df.empty:
            return self._empty_regression(request, ["No data available"])

        # Validate columns
        all_cols = [request.target_column] + request.feature_columns
        missing = [c for c in all_cols if c not in df.columns]
        if missing:
            return self._empty_regression(request, [f"Missing columns: {missing}"])

        df_clean = df[all_cols].dropna()
        if len(df_clean) < 10:
            return self._empty_regression(request, ["Not enough data (min 10 rows)"])

        X = df_clean[request.feature_columns].values
        y = df_clean[request.target_column].values

        # Split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=request.test_size, random_state=42)

        # Model selection
        if request.method == "polynomial":
            degree = request.polynomial_degree or 2
            poly = PolynomialFeatures(degree=degree, include_bias=False)
            X_train = poly.fit_transform(X_train)
            X_test = poly.transform(X_test)
            feature_names = poly.get_feature_names_out(request.feature_columns)
            model = LinearRegression()
        elif request.method == "ridge":
            model = Ridge(alpha=request.alpha)
            feature_names = request.feature_columns
        elif request.method == "lasso":
            model = Lasso(alpha=request.alpha)
            feature_names = request.feature_columns
        elif request.method == "elasticnet":
            model = ElasticNet(alpha=request.alpha, l1_ratio=request.l1_ratio)
            feature_names = request.feature_columns
        else:
            model = LinearRegression()
            feature_names = request.feature_columns

        model.fit(X_train, y_train)
        y_pred_test = model.predict(X_test)
        y_pred_all = model.predict(X if request.method != "polynomial" else poly.transform(X))
        residuals = y - y_pred_all

        # Metrics
        r2 = r2_score(y_test, y_pred_test)
        n, p = len(y), len(feature_names)
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1) if n > p + 1 else None
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
        mae = float(mean_absolute_error(y_test, y_pred_test))
        mse = float(mean_squared_error(y_test, y_pred_test))

        # F-statistic
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        f_stat = ((ss_tot - ss_res) / p) / (ss_res / (n - p - 1)) if n > p + 1 else None
        f_pval = float(stats.f.sf(f_stat, p, n - p - 1)) if f_stat else None

        # Durbin-Watson
        dw = float(np.sum(np.diff(residuals) ** 2) / ss_res) if ss_res > 0 else None

        # Coefficients with VIF
        coefs = []
        coef_values = model.coef_.tolist() if hasattr(model, "coef_") else []
        for i, (name, val) in enumerate(zip(feature_names, coef_values)):
            vif = None
            if len(feature_names) > 1 and request.method == "linear":
                try:
                    from statsmodels.stats.outliers_influence import variance_inflation_factor
                    vif = float(variance_inflation_factor(X, i))
                except Exception:
                    pass
            coefs.append(CoefficientInfo(name=name, value=round(float(val), 6), vif=vif))

        if len(coef_values) == 0:
            warnings_list.append("Model has no coefficients")

        return RegressionResult(
            intercept=round(float(model.intercept_), 6) if hasattr(model, "intercept_") else 0.0,
            coefficients=coefs,
            metrics=RegressionMetrics(
                r2_score=round(r2, 4), adjusted_r2=round(adj_r2, 4) if adj_r2 else None,
                rmse=round(rmse, 4), mae=round(mae, 4), mse=round(mse, 4),
                f_statistic=round(f_stat, 4) if f_stat else None,
                f_pvalue=round(f_pval, 6) if f_pval else None,
            ),
            diagnostics=RegressionDiagnostics(
                durbin_watson=round(dw, 4) if dw else None,
                high_vif_features=[c.name for c in coefs if c.vif and c.vif > 10],
            ),
            predictions=y_pred_test[:100].tolist(),
            residuals=residuals[:100].tolist(),
            actual_values=y[:100].tolist(),
            plot_data={
                "scatter": {"x": y_pred_all[:200].tolist(), "y": y[:200].tolist()},
                "residuals": {"x": y_pred_all[:200].tolist(), "y": residuals[:200].tolist()},
            },
            method=request.method,
            warning_messages=warnings_list,
        )

    def _empty_regression(self, request: RegressionRequest, warnings_list: List[str]) -> RegressionResult:
        return RegressionResult(
            intercept=0.0, coefficients=[],
            metrics=RegressionMetrics(r2_score=0, rmse=0, mae=0, mse=0),
            diagnostics=RegressionDiagnostics(),
            predictions=[], residuals=[], actual_values=[],
            plot_data=None, method=request.method, warning_messages=warnings_list,
        )

    async def pca_analysis(self, request: PCARequest) -> PCAResult:
        df = await self._load_dataset(request.dataset_id)
        empty = PCAResult(n_components=0, components=[], individuals=[], scree_plot_data={}, explained_variance={})

        if df is None or df.empty:
            return empty

        cols = [c for c in request.columns if c in df.columns]
        if len(cols) < 2:
            return empty

        df_clean = df[cols].dropna()
        if len(df_clean) < 3:
            return empty

        X = df_clean.values
        if request.standardize:
            scaler = StandardScaler()
            X = scaler.fit_transform(X)

        # Determine n_components
        max_comp = min(len(cols), len(df_clean))
        if request.method == "kaiser":
            # Run full PCA first to find eigenvalues > 1
            pca_full = PCA(n_components=max_comp)
            pca_full.fit(X)
            n_comp = max(1, int(np.sum(pca_full.explained_variance_ > 1)))
        elif request.method == "variance_80":
            pca_full = PCA(n_components=max_comp)
            pca_full.fit(X)
            cumvar = np.cumsum(pca_full.explained_variance_ratio_)
            n_comp = max(1, int(np.searchsorted(cumvar, 0.80) + 1))
        else:
            n_comp = request.n_components or min(2, max_comp)

        n_comp = min(n_comp, max_comp)
        pca = PCA(n_components=n_comp)
        scores = pca.fit_transform(X)

        components = []
        for i in range(n_comp):
            loadings = {col: round(float(pca.components_[i][j]), 4) for j, col in enumerate(cols)}
            components.append(PCAComponent(
                component_number=i + 1,
                eigenvalue=round(float(pca.explained_variance_[i]), 4),
                variance_explained_pct=round(float(pca.explained_variance_ratio_[i]) * 100, 2),
                cumulative_variance_pct=round(float(np.cumsum(pca.explained_variance_ratio_)[i]) * 100, 2),
                loadings=loadings,
            ))

        individuals = []
        for idx in range(min(len(scores), 500)):
            cos2 = [round(float(scores[idx, k] ** 2 / np.sum(scores[idx] ** 2)), 4) for k in range(n_comp)]
            contrib = [round(float(scores[idx, k] ** 2 / np.sum(scores[:, k] ** 2) * 100), 4) for k in range(n_comp)]
            individuals.append(PCAIndividual(
                id=idx, coordinates=[round(float(v), 4) for v in scores[idx]], cos2=cos2, contribution=contrib,
            ))

        return PCAResult(
            n_components=n_comp,
            components=components,
            individuals=individuals,
            correlation_circle={
                "variables": cols,
                "x": pca.components_[0].tolist(),
                "y": pca.components_[1].tolist() if n_comp > 1 else [0.0] * len(cols),
            },
            scree_plot_data={
                "components": list(range(1, n_comp + 1)),
                "eigenvalues": pca.explained_variance_.tolist(),
                "variance_pct": (pca.explained_variance_ratio_ * 100).tolist(),
            },
            biplot_data={
                "scores": scores[:200].tolist(),
                "loadings": pca.components_.tolist(),
                "feature_names": cols,
            },
            explained_variance={
                "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
                "cumulative": np.cumsum(pca.explained_variance_ratio_).tolist(),
            },
        )

    async def classification_analysis(self, request: ClassificationRequest) -> ClassificationResult:
        df = await self._load_dataset(request.dataset_id)
        empty = ClassificationResult(
            algorithm=request.algorithm,
            overall_metrics=ClassificationMetrics(accuracy=0, precision=0, recall=0, f1_score=0),
            class_metrics=[], confusion_matrix=ConfusionMatrix(labels=[], matrix=[]),
        )

        if df is None or df.empty:
            return empty

        all_cols = [request.target_column] + request.feature_columns
        missing = [c for c in all_cols if c not in df.columns]
        if missing:
            return empty

        df_clean = df[all_cols].dropna()
        if len(df_clean) < 10:
            return empty

        le = LabelEncoder()
        y = le.fit_transform(df_clean[request.target_column].astype(str))
        X = df_clean[request.feature_columns].select_dtypes(include=[np.number]).values

        if X.shape[1] == 0 or len(np.unique(y)) < 2:
            return empty

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=request.test_size, random_state=42)

        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.svm import SVC
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.naive_bayes import GaussianNB

        model_map = {
            "logistic": LogisticRegression(max_iter=1000, random_state=42),
            "svm": SVC(kernel="rbf", probability=True, random_state=42),
            "random_forest": RandomForestClassifier(n_estimators=100, random_state=42),
            "gradient_boosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
            "knn": KNeighborsClassifier(n_neighbors=5),
            "naive_bayes": GaussianNB(),
        }
        model = model_map.get(request.algorithm, RandomForestClassifier(n_estimators=100, random_state=42))
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
        rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

        cm = confusion_matrix(y_test, y_pred)
        labels = le.classes_.tolist()

        # Per-class metrics
        prec_per = precision_score(y_test, y_pred, average=None, zero_division=0)
        rec_per = recall_score(y_test, y_pred, average=None, zero_division=0)
        f1_per = f1_score(y_test, y_pred, average=None, zero_division=0)
        support = np.bincount(y_test)

        class_metrics = []
        for i, cls in enumerate(labels):
            if i < len(prec_per):
                class_metrics.append(ClassMetrics(
                    class_name=str(cls),
                    precision=round(float(prec_per[i]), 4),
                    recall=round(float(rec_per[i]), 4),
                    f1_score=round(float(f1_per[i]), 4),
                    support=int(support[i]) if i < len(support) else 0,
                ))

        cv_scores = cross_val_score(model, X, y, cv=min(request.cv_folds, len(np.unique(y)))).tolist()

        feat_imp = None
        if hasattr(model, "feature_importances_"):
            feat_imp = {f: round(float(v), 4) for f, v in zip(request.feature_columns, model.feature_importances_)}

        return ClassificationResult(
            algorithm=request.algorithm,
            overall_metrics=ClassificationMetrics(
                accuracy=round(acc, 4), precision=round(prec, 4),
                recall=round(rec, 4), f1_score=round(f1, 4),
            ),
            class_metrics=class_metrics,
            confusion_matrix=ConfusionMatrix(labels=labels, matrix=cm.tolist()),
            feature_importances=feat_imp,
            cross_validation_scores=cv_scores,
        )

    async def clustering_analysis(self, request: ClusteringRequest) -> ClusteringResult:
        df = await self._load_dataset(request.dataset_id)
        empty = ClusteringResult(
            algorithm=request.algorithm, n_clusters=0, clusters=[],
            metrics=ClusteringMetrics(silhouette_score=0),
        )

        if df is None or df.empty:
            return empty

        cols = [c for c in request.columns if c in df.columns]
        if len(cols) < 2:
            return empty

        df_clean = df[cols].dropna()
        if len(df_clean) < 4:
            return empty

        scaler = StandardScaler()
        X = scaler.fit_transform(df_clean[cols].select_dtypes(include=[np.number]).values)

        if X.shape[1] < 2:
            return empty

        # Elbow / silhouette to find optimal k
        elbow_data = None
        sil_data = None
        n_clusters = request.n_clusters or 3

        if request.method in ("elbow", "silhouette", "auto") and request.algorithm == "kmeans":
            k_range = range(2, min(11, len(df_clean)))
            inertias, silhouettes = [], []
            for k in k_range:
                km = KMeans(n_clusters=k, random_state=42, n_init=10)
                lbls = km.fit_predict(X)
                inertias.append(float(km.inertia_))
                silhouettes.append(float(silhouette_score(X, lbls)))
            k_list = list(k_range)
            elbow_data = {"k": k_list, "inertia": inertias}
            sil_data = {"k": k_list, "silhouette": silhouettes}
            if request.method in ("silhouette", "auto") and not request.n_clusters:
                n_clusters = k_list[int(np.argmax(silhouettes))]

        # Fit final model
        if request.algorithm == "kmeans":
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = model.fit_predict(X)
        elif request.algorithm == "dbscan":
            eps = request.eps or 0.5
            min_s = request.min_samples or 5
            model = DBSCAN(eps=eps, min_samples=min_s)
            labels = model.fit_predict(X)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        elif request.algorithm == "hierarchical":
            model = AgglomerativeClustering(n_clusters=n_clusters)
            labels = model.fit_predict(X)
        elif request.algorithm == "gmm":
            model = GaussianMixture(n_components=n_clusters, random_state=42)
            labels = model.fit_predict(X)
        else:
            model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = model.fit_predict(X)

        unique_labels = set(labels)
        if len(unique_labels) < 2:
            return empty

        sil = float(silhouette_score(X, labels))
        cal = float(calinski_harabasz_score(X, labels))
        db = float(davies_bouldin_score(X, labels))
        inertia = float(model.inertia_) if hasattr(model, "inertia_") else None

        # Build cluster info
        clusters = []
        for cid in sorted(unique_labels):
            if cid == -1:
                continue
            mask = labels == cid
            centroid = X[mask].mean(axis=0).tolist()
            clusters.append(ClusterInfo(
                cluster_id=int(cid),
                size=int(mask.sum()),
                centroid=[round(v, 4) for v in centroid],
                individuals=np.where(mask)[0][:50].tolist(),
            ))

        # 2D visualization via PCA if needed
        if X.shape[1] > 2:
            pca2 = PCA(n_components=2)
            X_2d = pca2.fit_transform(X)
        else:
            X_2d = X

        # Calculate average profiles per cluster
        average_profiles = []
        for cid in sorted(unique_labels):
            if cid == -1:
                continue
            mask = labels == cid
            cluster_data = df_clean[mask][cols].select_dtypes(include=[np.number])
            if len(cluster_data) > 0:
                avg_profile = cluster_data.mean().to_dict()
                average_profiles.append({
                    "cluster": int(cid),
                    **{k: round(v, 2) if isinstance(v, float) else v for k, v in avg_profile.items()}
                })

        return ClusteringResult(
            algorithm=request.algorithm,
            n_clusters=n_clusters,
            clusters=clusters,
            metrics=ClusteringMetrics(
                silhouette_score=round(sil, 4),
                calinski_harabasz_score=round(cal, 4),
                davies_bouldin_score=round(db, 4),
                inertia=round(inertia, 2) if inertia else None,
            ),
            elbow_plot_data=elbow_data,
            silhouette_plot_data=sil_data,
            cluster_visualization={
                "x": X_2d[:500, 0].tolist(),
                "y": X_2d[:500, 1].tolist(),
                "labels": labels[:500].tolist(),
            },
            average_profiles=average_profiles,
        )

    async def get_result(self, result_id: int) -> Optional[Dict[str, Any]]:
        return None
