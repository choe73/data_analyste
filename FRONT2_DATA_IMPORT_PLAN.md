# 🛡️ FRONT 2: Data Import & Auto-Analysis

## Objectif
Permettre aux utilisateurs d'importer des fichiers CSV/Excel, détecter automatiquement les types de colonnes, et générer une analyse descriptive.

---

## PHASE 1: Backend - Upload & Type Detection

### 1.1 Créer l'endpoint d'upload

Créer `backend/app/api/endpoints/imports.py` (améliorer l'existant) :

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import io
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User as UserModel
from app.models.dataset import Dataset

router = APIRouter()

@router.post("/imports/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and analyze a CSV/Excel file."""
    try:
        # Read file
        contents = await file.read()
        
        # Detect file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        # Analyze columns
        columns_info = []
        for col in df.columns:
            col_type = detect_column_type(df[col])
            columns_info.append({
                "name": col,
                "type": col_type,
                "non_null_count": int(df[col].notna().sum()),
                "null_count": int(df[col].isna().sum()),
                "unique_count": int(df[col].nunique())
            })
        
        # Create dataset record
        dataset = Dataset(
            user_id=current_user.id,
            name=file.filename.replace('.csv', '').replace('.xlsx', ''),
            description=f"Imported from {file.filename}",
            row_count=len(df),
            column_count=len(df.columns),
            columns_info=columns_info,
            file_path=f"uploads/{current_user.id}/{file.filename}"
        )
        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)
        
        return {
            "id": dataset.id,
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "columns": columns_info,
            "message": "File uploaded successfully"
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


def detect_column_type(series):
    """Detect column type: numeric, categorical, or text."""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    elif series.nunique() / len(series) < 0.05:  # Less than 5% unique values
        return "categorical"
    else:
        return "text"


@router.get("/imports/{import_id}")
async def get_import(
    import_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get import details."""
    query = select(Dataset).where(
        Dataset.id == import_id,
        Dataset.user_id == current_user.id
    )
    result = await db.execute(query)
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Import not found")
    
    return {
        "id": dataset.id,
        "name": dataset.name,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "columns": dataset.columns_info,
        "created_at": dataset.created_at
    }
```

### 1.2 Mettre à jour le modèle Dataset

Vérifier que `backend/app/models/dataset.py` a les colonnes nécessaires :

```python
class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    columns_info = Column(JSON, default=[])  # Array of column metadata
    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## PHASE 2: Frontend - Upload UI

### 2.1 Créer `frontend/src/pages/DataImport.tsx`

```tsx
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Upload, AlertCircle, CheckCircle } from 'lucide-react';

export default function DataImport() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.match(/\.(csv|xlsx|xls)$/)) {
        setError('Only CSV and Excel files are supported');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/api/v1/imports/upload`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        }
      );

      if (!response.ok) throw new Error('Upload failed');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Importer des données</h1>
        <p className="text-gray-600 mt-2">
          Téléchargez un fichier CSV ou Excel pour commencer l'analyse
        </p>
      </div>

      {/* Upload Area */}
      <Card className="p-8">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">
            Glissez-déposez votre fichier ou cliquez pour sélectionner
          </p>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileChange}
            className="hidden"
            id="file-input"
          />
          <label htmlFor="file-input">
            <Button as="span" variant="outline">
              Sélectionner un fichier
            </Button>
          </label>
        </div>

        {file && (
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm font-medium text-blue-900">
              Fichier sélectionné: {file.name}
            </p>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-50 rounded-lg flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {file && !result && (
          <Button
            onClick={handleUpload}
            disabled={loading}
            className="w-full mt-4 bg-green-600"
          >
            {loading ? 'Téléchargement...' : 'Télécharger et analyser'}
          </Button>
        )}
      </Card>

      {/* Results */}
      {result && (
        <Card className="p-6">
          <div className="flex items-start mb-4">
            <CheckCircle className="w-6 h-6 text-green-600 mr-3 flex-shrink-0" />
            <div>
              <h2 className="text-xl font-bold">{result.name}</h2>
              <p className="text-gray-600">
                {result.row_count} lignes × {result.column_count} colonnes
              </p>
            </div>
          </div>

          {/* Columns Info */}
          <div className="mt-6">
            <h3 className="font-semibold mb-4">Colonnes détectées</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.columns.map((col: any) => (
                <div key={col.name} className="p-4 border rounded-lg">
                  <p className="font-medium">{col.name}</p>
                  <div className="text-sm text-gray-600 mt-2 space-y-1">
                    <p>Type: <span className="font-semibold capitalize">{col.type}</span></p>
                    <p>Non-null: {col.non_null_count}</p>
                    <p>Unique: {col.unique_count}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <Button
            onClick={() => {
              setResult(null);
              setFile(null);
            }}
            className="w-full mt-6"
            variant="outline"
          >
            Importer un autre fichier
          </Button>
        </Card>
      )}
    </div>
  );
}
```

---

## PHASE 3: Auto-Analysis

### 3.1 Créer l'endpoint d'analyse automatique

Ajouter à `backend/app/api/endpoints/imports.py` :

```python
@router.post("/imports/{import_id}/analyze")
async def auto_analyze(
    import_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate automatic analysis for imported dataset."""
    try:
        # Get dataset
        query = select(Dataset).where(
            Dataset.id == import_id,
            Dataset.user_id == current_user.id
        )
        result = await db.execute(query)
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Load data
        df = pd.read_csv(dataset.file_path)  # or read_excel
        
        # Generate statistics
        stats = {
            "numeric_columns": [],
            "categorical_columns": [],
            "correlation_matrix": None,
            "missing_values": {}
        }
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                stats["numeric_columns"].append({
                    "name": col,
                    "mean": float(df[col].mean()),
                    "std": float(df[col].std()),
                    "min": float(df[col].min()),
                    "max": float(df[col].max()),
                    "median": float(df[col].median())
                })
            else:
                stats["categorical_columns"].append({
                    "name": col,
                    "unique_count": int(df[col].nunique()),
                    "top_values": df[col].value_counts().head(5).to_dict()
                })
            
            stats["missing_values"][col] = int(df[col].isna().sum())
        
        # Correlation matrix for numeric columns
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        if len(numeric_df.columns) > 1:
            stats["correlation_matrix"] = numeric_df.corr().to_dict()
        
        return {
            "dataset_id": import_id,
            "analysis": stats,
            "message": "Analysis completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
```

---

## PHASE 4: Tests

### Test 1: Upload CSV
```bash
curl -X POST "https://datacollect-cameroun-prod.onrender.com/api/v1/imports/upload" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@data.csv"
```

### Test 2: Get Import Details
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  "https://datacollect-cameroun-prod.onrender.com/api/v1/imports/1"
```

### Test 3: Auto-Analyze
```bash
curl -X POST -H "Authorization: Bearer <TOKEN>" \
  "https://datacollect-cameroun-prod.onrender.com/api/v1/imports/1/analyze"
```

---

## Checklist d'Implémentation

- [ ] Améliorer endpoint `/imports/upload` avec détection de type
- [ ] Mettre à jour modèle Dataset avec `columns_info`
- [ ] Créer endpoint `/imports/{id}/analyze`
- [ ] Créer page DataImport.tsx
- [ ] Tester upload CSV
- [ ] Tester détection de colonnes
- [ ] Tester analyse automatique
- [ ] Afficher résultats dans ImportResults.tsx

---

## Prochaines étapes après FRONT 2

**FRONT 3**: Connecter les datasets aux algorithmes Scikit-Learn
- Regression, PCA, Classification, Clustering
- Visualisations avec Plotly/Chart.js

**FRONT 4**: Intégration Gemini AI
- Interprétation naturelle des résultats
- Recommandations basées sur le domaine

**FRONT 5**: Form Builder
- Création de formulaires
- Collecte de réponses
- Analyse des réponses

**FRONT 6**: Automatisation & Caching
- Collecte de données automatique
- Smart caching
- Performance optimization
