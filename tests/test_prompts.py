import pytest

from legalbias import prompts


def test_paraphrase_zero_is_the_original_instruction():
    assert prompts.instruction("CRED", 0) == prompts.TASKS["CRED"]["instruction"]
    msgs = prompts.build_messages("CRED", "A case.")
    assert msgs[1]["content"].endswith(prompts.TASKS["CRED"]["instruction"])


# low (unfavourable) and high (favourable) anchors of the scale in each wording
ANCHORS = {
    1: ("1 means the account cannot be relied on at all", "10 means it can be fully relied on"),
    2: ("1 (no weight, not credible)", "10 (full weight, entirely"),
}


@pytest.mark.parametrize("k", [1, 2])
def test_paraphrases_keep_scale_direction_and_format(k):
    text = prompts.instruction("CRED", k)
    assert text != prompts.TASKS["CRED"]["instruction"]
    assert text.rstrip().endswith("SCORE: <integer from 1 to 10>")
    low, high = ANCHORS[k]
    flat = " ".join(text.split())
    assert low in flat and high in flat           # 1 = not credible, 10 = fully credible
    msgs = prompts.build_messages("CRED", "A case.", paraphrase=k)
    assert msgs[1]["content"].endswith(text)


def test_unknown_paraphrase_raises():
    with pytest.raises((KeyError, IndexError)):
        prompts.instruction("CRED", 3)
    with pytest.raises(KeyError):
        prompts.instruction("REC", 1)
