# app.py
import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
    Response,
)
from utils.ai_generator import ai_generate_login_cases
from utils.excel_utils import get_excel_path, next_tc_id, append_row, read_rows

app = Flask(__name__)
app.secret_key = "dev-secret"  # TODO: đổi sang biến môi trường khi deploy


# ------------------ ROUTES ------------------


@app.route("/", methods=["GET"])
def index():
    excel_path = get_excel_path()
    tc_suggestion = next_tc_id(excel_path)
    return render_template("form.html", tc=tc_suggestion)


@app.route("/favicon.ico")
def favicon():
    # tránh 404 khi browser tự gọi favicon
    return Response(status=204)


@app.route("/submit", methods=["POST"])
def submit():
    excel_path = get_excel_path()

    tc = (request.form.get("tc") or "").strip()
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    expected = (request.form.get("expected") or "").strip()
    note = (request.form.get("note") or "").strip()

    # validate cơ bản
    if not tc:
        flash("Thiếu Test Case ID", "error")
        return redirect(url_for("index"))
    if not username:
        flash("Thiếu Username/Email", "error")
        return redirect(url_for("index"))
    if expected not in {"Pass", "Fail", "Validation error"}:
        flash("Expected Result không hợp lệ.", "error")
        return redirect(url_for("index"))

    append_row(excel_path, [tc, username, password, expected, note])
    flash(f"💾 Đã lưu {tc}!", "success")
    return redirect(url_for("index"))


@app.route("/ai_generate", methods=["POST"])
def ai_generate():
    excel_path = get_excel_path()
    print(">>> Excel path:", excel_path)  # LOG

    # Lấy tham số
    try:
        n = int(request.form.get("n", "5"))
    except ValueError:
        n = 5
    hints = (request.form.get("hints") or "").strip()

    # Gọi AI
    try:
        ai_cases = ai_generate_login_cases(n=n, hints=hints)
    except Exception as e:
        print(" AI error:", e)  # LOG
        flash(f" AI sinh dữ liệu thất bại: {e}", "error")
        return redirect(url_for("index"))

    print(f">>> AI trả về {len(ai_cases)} case:", ai_cases)  # LOG

    if not ai_cases:
        flash(
            " AI không sinh được test case nào (có thể do JSON sai hoặc thiếu API key).",
            "error",
        )
        return redirect(url_for("index"))

    # Gán TCID & ghi Excel
    start_tc = next_tc_id(excel_path)  # VD "TC07"
    print(">>> next_tc_id:", start_tc)  # LOG
    start_num = int(start_tc[2:]) if start_tc.upper().startswith("TC") else 1

    saved = 0
    for i, c in enumerate(ai_cases):
        tcid = f"TC{start_num + i:02d}"
        row = [tcid, c["username"], c["password"], c["expected"], c["note"]]
        try:
            append_row(excel_path, row)
            print(">>> appended:", row)  # LOG
            saved += 1
        except Exception as e:
            print(" append_row error:", e)  # LOG
            flash(f" Lỗi khi ghi Excel ở {tcid}: {e}", "error")

    if saved == 0:
        flash(" Không ghi được dòng nào vào Excel.", "error")
        return redirect(url_for("index"))

    flash(f" AI đã sinh & lưu {saved} test case vào Excel.", "success")
    return redirect(url_for("table_view"))


@app.route("/table", methods=["GET"])
def table_view():
    excel_path = get_excel_path()
    headers = ["Test Case", "Username/Email", "Password", "Expected Result", "Note"]
    rows = read_rows(excel_path)
    return render_template("table.html", headers=headers, rows=rows)


@app.route("/list", methods=["GET"])
def list_data():
    excel_path = get_excel_path()
    rows = read_rows(excel_path)
    return {
        "headers": [
            "Test Case",
            "Username/Email",
            "Password",
            "Expected Result",
            "Note",
        ],
        "data": rows,
    }


@app.route("/download", methods=["GET"])
def download():
    path = get_excel_path()
    return send_file(path, as_attachment=True, download_name=os.path.basename(path))


# ------------------ MAIN ------------------
if __name__ == "__main__":
    # truy cập tại: http://127.0.0.1:5000/
    app.run(debug=True)
