from tests.eval.test_benchmark import TEST_CASES, Case, score


def test_declared_set_has_all_cases_and_failure_is_not_a_refusal():
    assert len(TEST_CASES) == 25
    assert not score(Case("unsupported", "unsupported"), None, "timeout")
    assert not score(Case("unsupported", "unsupported"), {"message": {"citations": []}})
    assert score(
        Case("unsupported", "unsupported"),
        {"message": {"citations": [], "status": "refused", "content": "No relevant evidence"}},
    )


def test_essay_word_target_is_part_of_acceptance():
    response = {
        "message": {
            "status": "complete",
            "content": "too short",
            "citations": [{"id": "real-source", "title": "Episode", "url": "https://example.com"}],
        }
    }
    assert not score(Case("essay", "ship30"), response)


def test_html_wrapper_does_not_make_plain_text_a_valid_artifact():
    from packages.agent.artifacts import sanitize_html

    response = {
        "message": {
            "status": "complete",
            "citations": [{"id": "source", "title": "Episode", "url": "https://example.com"}],
        },
        "artifact": {"id": "artifact", "type": "html", "content": sanitize_html("Just text [S1]")},
    }
    assert not score(Case("Create an HTML brief", "artifact"), response)
    response["artifact"]["content"] = sanitize_html("<h1>A brief</h1><p>Advice [S1]</p>")
    assert score(Case("Create an HTML brief", "artifact"), response)
