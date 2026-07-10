import pytest
from app.services.ai.assistant.reasoning.evidence_ranker import EvidenceRanker
from tests.fixtures.tool_results import PUBLIC_RDS, PRIVATE_RDS

def test_evidence_ranker_empty():
    ranker = EvidenceRanker()
    findings, evidence = ranker.rank_evidence([])
    assert findings == []
    assert evidence == []

def test_evidence_ranker_sorting_and_top_n():
    ranker = EvidenceRanker()
    # Create 50 results (duplicating PUBLIC_RDS and PRIVATE_RDS for test volume)
    results = [PUBLIC_RDS] * 25 + [PRIVATE_RDS] * 25
    findings, evidence = ranker.rank_evidence(results)
    
    assert len(evidence) <= 8 # top 8
    
    # Verify sorting by confidence
    for i in range(1, len(evidence)):
        assert evidence[i-1].confidence >= evidence[i].confidence
