"""Base analyzer class with abstract methods for data analysis."""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseAnalyzer(ABC):
    """
    Abstract base class for all data analyzers.
    
    Demonstrates:
    - Abstraction: Defines the contract for all analyzers
    - Polymorphism: Each child implements execute() differently
    - Strategy Pattern: Each analyzer is a strategy for a specific analysis type
    
    This is the foundation of the Strategy pattern for analysis.
    """

    @abstractmethod
    async def execute(
        self,
        df: pd.DataFrame,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute the analysis algorithm.
        
        This method MUST be implemented by each child class.
        Each analysis type has different algorithms and outputs.
        
        Args:
            df: Input DataFrame
            params: Analysis parameters (target_column, features, etc.)
            
        Returns:
            Dictionary containing analysis results
            
        Raises:
            ValueError: If parameters are invalid
            Exception: If analysis fails
        """
        pass

    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """
        Validate that the DataFrame is suitable for analysis.
        
        This method is inherited by all analyzers (Composition).
        It handles common validation logic.
        
        Args:
            df: DataFrame to validate
            
        Raises:
            ValueError: If DataFrame is invalid
        """
        if df is None or df.empty:
            raise ValueError("DataFrame is empty or None")

        if len(df) < 2:
            raise ValueError("DataFrame must have at least 2 rows")

    def _validate_columns(
        self,
        df: pd.DataFrame,
        required_columns: list,
    ) -> None:
        """
        Validate that required columns exist in DataFrame.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            
        Raises:
            ValueError: If required columns are missing
        """
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

    def _clean_data(
        self,
        df: pd.DataFrame,
        columns: list,
    ) -> pd.DataFrame:
        """
        Clean data by removing rows with missing values.
        
        This method is inherited by all analyzers (Composition).
        It handles common data cleaning logic.
        
        Args:
            df: DataFrame to clean
            columns: Columns to check for missing values
            
        Returns:
            Cleaned DataFrame
        """
        return df.dropna(subset=columns)

    def _prepare_result(
        self,
        algorithm: str,
        metrics: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        visualizations: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Prepare the result dictionary in a standardized format.
        
        This method is inherited by all analyzers (Composition).
        It ensures consistent output format across all analyzers.
        
        Args:
            algorithm: Name of the algorithm used
            metrics: Dictionary of calculated metrics
            data: Additional data (coefficients, components, etc.)
            visualizations: Visualization data (plot_data, etc.)
            
        Returns:
            Standardized result dictionary
        """
        return {
            "algorithm": algorithm,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "data": data or {},
            "visualizations": visualizations or {},
        }


class AnalysisContext:
    """
    Context class that orchestrates the analysis strategies.
    
    Demonstrates:
    - Strategy Pattern: Selects the appropriate analyzer based on analysis type
    - Composition: Contains multiple analyzer instances
    - Polymorphism: Calls execute() on different analyzer types
    
    This is the main entry point for all analyses.
    """

    def __init__(self):
        """Initialize the analysis context with available strategies."""
        self.strategies: Dict[str, BaseAnalyzer] = {}

    def register_strategy(self, analysis_type: str, analyzer: BaseAnalyzer) -> None:
        """
        Register an analyzer strategy.
        
        Args:
            analysis_type: Type of analysis (e.g., "regression", "pca")
            analyzer: Analyzer instance
        """
        self.strategies[analysis_type] = analyzer

    async def run_analysis(
        self,
        analysis_type: str,
        df: pd.DataFrame,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Run the specified analysis.
        
        This method demonstrates polymorphism:
        - It doesn't know which analyzer will be used
        - It just calls execute() on the selected strategy
        - Each strategy implements execute() differently
        
        Args:
            analysis_type: Type of analysis to run
            df: Input DataFrame
            params: Analysis parameters
            
        Returns:
            Analysis results
            
        Raises:
            ValueError: If analysis type is not supported
        """
        if analysis_type not in self.strategies:
            raise ValueError(
                f"Analysis type '{analysis_type}' not supported. "
                f"Available: {list(self.strategies.keys())}"
            )

        analyzer = self.strategies[analysis_type]
        return await analyzer.execute(df, params)
