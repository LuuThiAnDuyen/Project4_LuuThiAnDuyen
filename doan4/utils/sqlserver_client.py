from __future__ import annotations
import os
from typing import List, Tuple
import pyodbc
from dotenv import load_dotenv

load_dotenv()


# =========================
# CONNECTION
# =========================
def get_sqlserver_conn():
    server = os.getenv("SQLSERVER_HOST", "LTADUYEN")
    database = os.getenv("SQLSERVER_DB", "master")
    driver = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")

    use_windows_auth = os.getenv("SQLSERVER_WINDOWS_AUTH", "1") == "1"

    if use_windows_auth:
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
        )
    else:
        user = os.getenv("SQLSERVER_USER", "sa")
        password = os.getenv("SQLSERVER_PASSWORD", "your_password")
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            "TrustServerCertificate=yes;"
        )

    return pyodbc.connect(conn_str)


# =========================
# DATA LOADER (READ)
# =========================
def load_login_cases(active_only: bool = True) -> List[Tuple[str, str, str, str]]:
    """
    Return:
    (tcid, email, password, expected_message)
    """
    where = "WHERE IsActive = 1" if active_only else ""

    sql = f"""
        SELECT TestCaseID, Email, Password, ExpectedMessage
        FROM dbo.login_test_data
        {where}
        ORDER BY TestCaseID
    """

    with get_sqlserver_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

    cases = []
    for r in rows:
        tcid = str(r.TestCaseID or "").strip()
        email = str(r.Email or "")
        password = str(r.Password or "")
        expected = str(r.ExpectedMessage or "")
        if tcid:
            cases.append((tcid, email, password, expected))

    return cases


# =========================
# RESULT WRITER (WRITE)
# =========================
def write_login_result(
    tcid: str, result: str, screenshot: str = "", video: str = ""
) -> None:
    """
    Update result, screenshot, video, updatedAt by TestCaseID
    """

    sql = """
        UPDATE dbo.login_test_data
        SET
            Result = ?,
            Screenshot = ?,
            Video = ?,
            UpdatedAt = SYSDATETIME()
        WHERE TestCaseID = ?
    """

    with get_sqlserver_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, (result, screenshot, video, tcid))
        conn.commit()
