from main import REPORTS


def test_supported_report_exports_are_registered():
    assert set(REPORTS) == {"room-utilization", "lecturer-workload", "conflicts"}


def test_report_queries_filter_by_semester():
    assert all(":semester_id" in statement for statement in REPORTS.values())
