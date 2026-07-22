import os
os.environ["IS_TESTING"] = "1"

import pytest
from unittest.mock import MagicMock, patch

from schemas.query_context import BusinessContext, DomainSection, BusinessObservation
from schemas.reasoning_context import ReasoningContext
from schemas.forecast_context import ForecastContext, ForecastResult, ForecastMetric, ForecastAlgorithm
from schemas.retrieval_plan import RetrievalPlan, QueryType, QueryIntent
from schemas.report import BusinessDomain
from services.query_service import QueryService
from services.rag_service import RagService

@pytest.fixture
def rag_service():
    with patch("services.rag_service.RagService._configure_models"):
        with patch("services.rag_service.RagService._load_index", return_value=MagicMock()):
            with patch("llama_index.core.settings._Settings.llm", create=True) as mock_llm:
                # Also just set it on the module directly to be safe
                from llama_index.core import Settings
                Settings.llm = MagicMock()
                rs = RagService()
                return rs

@pytest.fixture
def query_service(rag_service):
    return QueryService(rag_service)

def make_obs():
    return BusinessObservation(
        domain=BusinessDomain.SALES,
        report_type="test",
        source_file="test.csv",
        sheet="Sheet1",
        key_values={"total_sales": "100"},
        raw_text="Test obs",
    )

def test_empty_forecast_context_omits_prompt_block(rag_service):
    with patch("llama_index.core.llms.mock.MockLLM.complete") as mock_complete:
        mock_complete.return_value = "Test response"
        
        # Empty forecast context
        fc = ForecastContext()
        rag_service.generate_response("q", "context", forecast_context=fc)
        
        prompt = mock_complete.call_args[0][0]
        assert "DETERMINISTIC FORECASTING RESULTS" not in prompt

def test_populated_forecast_context_includes_prompt_block(rag_service):
    with patch("llama_index.core.llms.mock.MockLLM.complete") as mock_complete:
        mock_complete.return_value = "Test response"
        
        result = ForecastResult(
            metric=ForecastMetric.SALES,
            forecast_period="Next Month",
            predicted_value=150.0,
            confidence=0.9,
            lower_bound=100.0,
            upper_bound=200.0,
            algorithm=ForecastAlgorithm.EXPONENTIAL_SMOOTHING,
            methodology="Test Method",
            observations_used=10,
            historical_period="Last 10",
        )
        fc = ForecastContext(results=[result])
        rag_service.generate_response("q", "context", forecast_context=fc)
        
        prompt = mock_complete.call_args[0][0]
        assert "DETERMINISTIC FORECASTING RESULTS" in prompt
        assert "Sales Forecast" in prompt
        assert "150.00" in prompt
        assert "90.0%" in prompt

def test_query_service_analytics_only(query_service):
    plan = RetrievalPlan(QueryType.SUMMARIZE, QueryIntent.SUMMARIZE_REPORT, [BusinessDomain.SALES])
    query_service._intent_analyzer = MagicMock(analyze=MagicMock(return_value=plan))
    query_service._retrieval_service = MagicMock(retrieve=MagicMock(return_value=[]))
    query_service._context_builder = MagicMock(build=MagicMock(return_value=BusinessContext(plan)))
    query_service._reasoning_service = MagicMock(reason=MagicMock(return_value=ReasoningContext([])))
    query_service._analytics_service = MagicMock(compute=MagicMock(return_value=MagicMock()))
    query_service._forecasting_service = MagicMock(compute=MagicMock())
    query_service._rag_service = MagicMock(generate_response=MagicMock())

    query_service.answer("test query")
    
    query_service._analytics_service.compute.assert_called_once()
    query_service._forecasting_service.compute.assert_not_called()
    
    rag_kwargs = query_service._rag_service.generate_response.call_args[1]
    assert rag_kwargs["analytics_context"] is not None
    assert rag_kwargs["forecast_context"] is None

def test_query_service_analytics_and_forecasting(query_service):
    plan = RetrievalPlan(
        QueryType.SUMMARIZE, 
        QueryIntent.SUMMARIZE_REPORT, 
        [BusinessDomain.SALES],
        forecast_metrics=[ForecastMetric.SALES]
    )
    query_service._intent_analyzer = MagicMock(analyze=MagicMock(return_value=plan))
    query_service._retrieval_service = MagicMock(retrieve=MagicMock(return_value=[]))
    query_service._context_builder = MagicMock(build=MagicMock(return_value=BusinessContext(plan)))
    query_service._reasoning_service = MagicMock(reason=MagicMock(return_value=ReasoningContext([])))
    query_service._analytics_service = MagicMock(compute=MagicMock(return_value=MagicMock()))
    query_service._forecasting_service = MagicMock(compute=MagicMock(return_value=MagicMock()))
    query_service._rag_service = MagicMock(generate_response=MagicMock())

    query_service.answer("test query")
    
    query_service._analytics_service.compute.assert_called_once()
    query_service._forecasting_service.compute.assert_called_once()
    
    rag_kwargs = query_service._rag_service.generate_response.call_args[1]
    assert rag_kwargs["analytics_context"] is not None
    assert rag_kwargs["forecast_context"] is not None
