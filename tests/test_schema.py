"""Unit tests for Card and RawItem schemas."""

from pipeline.schema import Card, RawItem, generate_card_id


def test_generate_card_id():
    url = "https://github.com/vllm-project/vllm/releases/tag/v0.6.2"
    card_id_1 = generate_card_id(url)
    card_id_2 = generate_card_id(url)

    assert isinstance(card_id_1, str)
    assert len(card_id_1) == 12
    assert card_id_1 == card_id_2


def test_card_serialization():
    card = Card(
        id="test-123",
        tab="trending",
        headline="vLLM Update",
        summary="vLLM release notes",
        why_it_matters="Improves throughput",
        colab_runnable=True,
        source_name="GitHub",
        source_url="https://github.com/vllm-project/vllm",
        date="2026-09-17",
    )

    card_dict = card.to_dict()
    assert card_dict["id"] == "test-123"
    assert card_dict["tab"] == "trending"
    assert card_dict["colab_runnable"] is True

    reconstructed = Card.from_dict(card_dict)
    assert reconstructed.id == card.id
    assert reconstructed.tab == card.tab
    assert reconstructed.colab_runnable == card.colab_runnable
