def assert_contains(substring: str, full_string: str):
    assert substring in full_string, f"Expected '{substring}' to be in '{full_string}'"

def assert_is_subset(subset: list, full_set: list):
    for item in subset:
        assert item in full_set, f"Expected '{item}' to be in {full_set}"
