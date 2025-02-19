import pytest
import sqlite3
import osm
from unittest.mock import patch


@pytest.fixture(scope="function")
def setup_db():
    """Creates a persistent in-memory SQLite DB for testing and returns the connection."""
    test_db_file = ":memory:"
    original_db_file = osm.DB_FILE

    # Create a shared in-memory database connection
    conn = sqlite3.connect(test_db_file)
    osm.DB_FILE = test_db_file  # Redirect osm to use in-memory DB
    osm.init_db(conn)  # Initialize the table

    yield conn  # Provide the connection to the test

    # Cleanup: close the in-memory DB
    conn.close()
    osm.DB_FILE = original_db_file  # Restore the original DB file


@pytest.mark.usefixtures("setup_db")
@patch("osm.send_alert")  # Ensure send_alert is properly mocked
@patch("osm.psutil.disk_usage")
@patch("osm.psutil.virtual_memory")
@patch("osm.psutil.cpu_percent")
def test_collect_metrics_high_usage(mock_cpu, mock_mem, mock_disk, mock_alert, setup_db):
    """Test that collect_metrics triggers an alert if thresholds are exceeded."""
    mock_cpu.return_value = osm.CPU_THRESHOLD + 95  # Ensure values exceed threshold
    mock_mem.return_value.percent = osm.RAM_THRESHOLD + 95
    mock_disk.return_value.percent = osm.DISK_THRESHOLD + 95

    osm.collect_metrics(setup_db)  # Use the shared DB connection

    # ✅ Now the alert should be triggered correctly
    mock_alert.assert_called_once()

    # Print the alert message for debugging
    alert_message = mock_alert.call_args[0][0]
    print(f"🚀 Alert Triggered: {alert_message}")


@pytest.mark.usefixtures("setup_db")
@patch("osm.psutil.disk_usage")
@patch("osm.psutil.virtual_memory")
@patch("osm.psutil.cpu_percent")
def test_collect_metrics_normal_usage(mock_cpu, mock_mem, mock_disk, setup_db):
    """Test that collect_metrics does NOT trigger an alert if usage is below thresholds."""
    mock_cpu.return_value = osm.CPU_THRESHOLD - 1
    mock_mem.return_value.percent = osm.RAM_THRESHOLD - 1
    mock_disk.return_value.percent = osm.DISK_THRESHOLD - 1

    with patch("osm.send_alert") as mock_alert:
        osm.collect_metrics(setup_db)  # Use the shared DB connection
        mock_alert.assert_not_called()


@pytest.mark.usefixtures("setup_db")
def test_db_insert(setup_db):
    """Ensure that collect_metrics inserts data into the usage_history table."""
    with patch("osm.psutil.cpu_percent", return_value=10), \
            patch("osm.psutil.virtual_memory") as mock_mem, \
            patch("osm.psutil.disk_usage") as mock_disk:
        mock_mem.return_value.percent = 20
        mock_disk.return_value.percent = 30

        osm.collect_metrics(setup_db)  # Use the shared DB connection

    # Use the shared connection to check inserted rows
    cursor = setup_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM usage_history;")
    count = cursor.fetchone()[0]

    assert count == 1, "There should be exactly 1 row in usage_history after collect_metrics."
