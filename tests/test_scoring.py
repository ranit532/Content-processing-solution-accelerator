from src.services.scoring import calculate_confidence


def test_confidence_basic():
    extracted = {'text': 'Invoice 123'}
    mapped = {'invoice_number': '123', 'total': '100'}
    score = calculate_confidence(extracted, mapped)
    assert score > 0.5
