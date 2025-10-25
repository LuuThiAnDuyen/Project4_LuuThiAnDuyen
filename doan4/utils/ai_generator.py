# utils/ai_generator.py
import os, json, re
from typing import List, Dict
from pydantic import BaseModel, Field, validator

# ====== Cấu hình provider ======
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # openai | ollama (tùy chọn)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

ALLOWED_EXPECTED = {"Pass", "Fail", "Validation error"}


class LoginCase(BaseModel):
    username: str = Field(default="")
    password: str = Field(default="")
    expected: str
    note: str = Field(default="")

    @validator("expected")
    def _expected_ok(cls, v):
        v = (v or "").strip()
        if v not in ALLOWED_EXPECTED:
            raise ValueError(f"expected must be one of {ALLOWED_EXPECTED}")
        return v


SYSTEM_MSG = (
    "Bạn là trình sinh dữ liệu kiểm thử. "
    "Hãy xuất ra JSON hợp lệ DUY NHẤT có dạng: "
    '{"cases":[{"Username/Email":"","Password":"","Expected Result":"","Note":""}, ...]}. '
    "Không thêm giải thích hay markdown, không có ```."
)

PROMPT_TEMPLATE = """Sinh {n} test case đăng nhập theo JSON schema:
{{
  "cases": [
    {{
      "Username/Email": "string (email hợp lệ hoặc không hợp lệ hoặc rỗng)",
      "Password": "string (có thể rỗng)",
      "Expected Result": "Pass | Fail | Validation error",
      "Note": "mô tả ngắn gọn bằng tiếng Việt"
    }}
  ]
}}
Yêu cầu:
- Phân bổ cân bằng giữa Pass/Fail/Validation error.
- Pass: email hợp lệ + password không rỗng.
- Validation error: thiếu email hoặc thiếu password hoặc email sai định dạng.
- Fail: thông tin có vẻ hợp lệ nhưng sai (VD: email đúng, pass sai).
- Không dùng dữ liệu thật; không lộ thông tin nhạy cảm; tránh trùng lặp.
{hints}
"""


def _strip_fences(s: str) -> str:
    return re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", s, flags=re.S).strip()


def _call_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content or ""


def _call_ollama(prompt: str) -> str:
    import ollama  # pip install ollama

    out = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.2},
    )
    return out["message"]["content"]


def ai_generate_login_cases(n: int = 5, hints: str = "") -> List[Dict]:
    prompt = PROMPT_TEMPLATE.format(n=n, hints=hints or "")
    if AI_PROVIDER == "openai":
        raw = _call_openai(prompt)
    elif AI_PROVIDER == "ollama":
        raw = _call_ollama(prompt)
    else:
        raise RuntimeError("AI_PROVIDER không hỗ trợ. Dùng 'openai' hoặc 'ollama'.")

    raw = _strip_fences(raw)
    data = json.loads(raw)  # nếu lỗi -> raise để bắt ở controller
    cases = []
    for obj in data.get("cases", []):
        case = LoginCase(
            username=obj.get("Username/Email", "") or "",
            password=obj.get("Password", "") or "",
            expected=(obj.get("Expected Result") or "").strip(),
            note=obj.get("Note", "") or "",
        )
        cases.append(case.dict())
    return cases
