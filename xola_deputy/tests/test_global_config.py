from xola_deputy.global_config import compare_mapping

def test_compare_mapping():
    assert compare_mapping("Asylum","title")
    assert compare_mapping("5b649f7ec581e1c1738b463f","experience")
    assert compare_mapping("1","area")
    assert compare_mapping("111111","experience") == False
