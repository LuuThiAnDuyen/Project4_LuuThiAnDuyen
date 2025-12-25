from __future__ import annotations
import os
from typing import List, Tuple, Optional
import pyodbc
from dotenv import load_dotenv
load_dotenv()

def get_sqlserver_conn():
    """
    Cách 1: Windows Authentication (Trusted Connection)
    - phù hợp khi bạn đăng nhập Windows và SQL Server cho phép integrated security

    Cách 2: SQL Authentication
    - dùng USER/PASSWORD

    Khuyến nghị: cấu hình qua ENV để không hardcode.
    """

    server = os.getenv("SQLSERVER_HOST", "LTADUYEN")  # ví dụ: DESKTOP-ABC\SQLEXPRESS
    database = os.getenv("SQLSERVER_DB", "master")

    # ====== Option A: Windows Auth ======
    use_windows_auth = os.getenv("SQLSERVER_WINDOWS_AUTH", "1") == "1"
    driver = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")

    if use_windows_auth:
        conn_str = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
        )
        return pyodbc.connect(conn_str)

    # ====== Option B: SQL Auth ======
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


def load_login_cases_from_db(active_only: bool = True) -> List[Tuple[str, str, str, str, str, str, str]]:
    """
    Return list tuples đúng format test_login của bạn:
    (tcid, email, password, expected_message, actual_result, screenshot, video)
    """
    where = "WHERE IsActive = 1" if active_only else ""
    sql = f"""
    SELECT TestCaseID, Email, Password, ExpectedMessage, Result, Screenshot, Video
    FROM dbo.login_test_data
    {where}
    ORDER BY TestCaseID
    """

    with get_sqlserver_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

    out: List[Tuple[str, str, str, str, str, str, str]] = []
    for r in rows:
        tcid = str(r[0] or "").strip()
        email = str(r[1] or "")
        password = str(r[2] or "")
        expected = str(r[3] or "")
        result = str(r[4] or "")
        screenshot = str(r[5] or "")
        video = str(r[6] or "")
        if tcid:
            out.append((tcid, email, password, expected, result, screenshot, video))
    return out


def write_login_result_to_db(tcid: str, result: str, screenshot: str = "", video: str = "") -> None:
    sql = """
    UPDATE dbo.login_test_data
    SET Result = ?, Screenshot = ?, Video = ?, UpdatedAt = SYSDATETIME()
    WHERE TestCaseID = ?
    """
    with get_sqlserver_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql, (result, screenshot, video, tcid))
        conn.commit()
