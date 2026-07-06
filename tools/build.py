#!/usr/bin/env python3
"""資格別学習アプリのビルドスクリプト。

使い方:
    python3 tools/build.py <cert_id>        # 例: python3 tools/build.py csa
    python3 tools/build.py --all            # certs/ 配下すべてビルド

入力:  certs/<cert_id>/config.json, notes/*.md, questions.js
出力:  app/<output_single>  (完全単一ファイル・オフライン動作)

このスクリプトと template/app_template.html があれば、
LLMや手作業でコンテンツ(config/notes/questions)を用意するだけで
新しい資格のアプリを再現できる。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "template" / "app_template.html"


def js_escape(text: str) -> str:
    """MarkdownをJSテンプレートリテラルに埋め込むためのエスケープ。"""
    return text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def build(cert_id: str) -> Path:
    cert_dir = ROOT / "certs" / cert_id
    config = json.loads((cert_dir / "config.json").read_text())

    # NOTES オブジェクトの中身を組み立て
    notes_parts = []
    for d in config["domains"]:
        md = (cert_dir / "notes" / d["note"]).read_text()
        notes_parts.append(f'  {d["id"]}: `{js_escape(md)}`,')
    notes_js = "\n".join(notes_parts)

    # STUDY_DOMAINS 配列
    sd_parts = [
        f'  {{ id: {d["id"]}, label: "{d["label"]}", weight: {d["weight"]} }},'
        for d in config["domains"]
    ]
    study_domains_js = "\n".join(sd_parts)

    questions_js = (cert_dir / "questions.js").read_text()

    html = TEMPLATE.read_text()
    for key, value in [
        ("{{APP_TITLE}}", config["app_title"]),
        ("{{APP_SUBTITLE}}", config["app_subtitle"]),
        ("{{VERSION_BADGE}}", config["version_badge"]),
        ("{{STORAGE_PREFIX}}", config["storage_prefix"]),
        ("{{NOTES_JS}}", notes_js),
        ("{{STUDY_DOMAINS_JS}}", study_domains_js),
        ("{{QUESTIONS_JS}}", questions_js),
    ]:
        if key not in html:
            raise SystemExit(f"テンプレートにプレースホルダがありません: {key}")
        html = html.replace(key, value)

    out = ROOT / "app" / config["output_single"]
    out.write_text(html)
    print(f"built: {out} ({len(html):,} bytes)")
    return out


def validate_questions(cert_id: str) -> None:
    """questions.js の簡易バリデーション(ID重複・answer範囲)。node不要版。"""
    import re

    src = (ROOT / "certs" / cert_id / "questions.js").read_text()
    ids = re.findall(r"\bid:\s*(\d+)", src)
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"重複ID: {sorted(dupes)}")
    print(f"questions: {len(ids)} 問 / ID重複なし")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    if sys.argv[1] == "--all":
        for d in sorted((ROOT / "certs").iterdir()):
            if (d / "config.json").exists():
                validate_questions(d.name)
                build(d.name)
    else:
        validate_questions(sys.argv[1])
        build(sys.argv[1])
