"""ДЕКОРИЯ: durable intake and a private inbox behind an HTTPS reverse proxy."""
from base64 import b64decode
from datetime import datetime, timedelta, timezone
from email.parser import BytesParser
from email.policy import default
from hashlib import sha256
from hmac import compare_digest, digest
from html import escape
from pathlib import Path
from urllib.parse import quote, urlsplit
from wsgiref.simple_server import make_server
import argparse
import filetype
import json
import os
import re
import sqlite3

MIB = 1024 * 1024
SOURCES = {"project_v10", "quiz_v10"}
CONTEXT = {"details", "business", "zone", "occasion", "style", "format", "date", "example"}
TRACK = {"utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"}
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\Z")
OPTIONS = {
    "object": {"Кафе и ресторан", "Салон и услуги", "Бутик и шоурум", "Офис, отель, ТЦ", "Другое — опишу в конце"},
    "zones": {"Вход", "Витрина", "Зал", "Несколько зон", "Пока не знаю — нужен совет"},
    "mood": {"Тёплая классика", "Лёд и серебро", "Русский орнамент", "Мягкая пастель", "Не знаю — подберите за меня"},
    "install_window": {"До 1 декабря", "1–15 декабря", "16–25 декабря", "Пока не знаю"},
}


class BadRequest(ValueError):
    pass


class Inbox:
    def __init__(self):
        self.db = Path(os.environ["DEKORIYA_INBOX_DB"]).expanduser().resolve()
        self.origin = os.environ["DEKORIYA_SITE_ORIGIN"]
        self.password = os.environ["DEKORIYA_INBOX_PASSWORD"]
        self.version = os.environ["DEKORIYA_CONSENT_VERSION"]
        self.policy_url = os.environ["DEKORIYA_POLICY_URL"]
        self.consent_url = os.environ["DEKORIYA_CONSENT_URL"]
        consent_text = Path(os.environ["DEKORIYA_CONSENT_FILE"]).read_text(encoding="utf-8").strip()
        if len(self.password) < 24 or not consent_text:
            raise RuntimeError("Set a strong inbox password and approved consent text.")
        origin = urlsplit(self.origin)
        if origin.path or origin.query or origin.fragment or not origin.hostname or origin.username:
            raise RuntimeError("Configure the exact origin with scheme and host, without a path.")
        if origin.scheme != "https" and not (origin.scheme == "http" and origin.hostname in {"localhost", "127.0.0.1"}):
            raise RuntimeError("Public origin must use HTTPS.")
        for address in (self.policy_url, self.consent_url):
            url = urlsplit(address)
            if url.scheme != "https" or not url.hostname or url.username or url.fragment:
                raise RuntimeError("Configure approved HTTPS document URLs.")
        if self.policy_url == self.consent_url:
            raise RuntimeError("Configure distinct links for policy and consent.")
        self.document = {"version": self.version, "text": consent_text, "policy_url": self.policy_url, "consent_url": self.consent_url}
        self.db.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.db.touch(mode=0o600, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS lead (
                    id TEXT PRIMARY KEY, at TEXT NOT NULL, payload TEXT NOT NULL,
                    doc TEXT NOT NULL, hash TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS photo (
                    lead_id TEXT REFERENCES lead(id) ON DELETE CASCADE,
                    number INTEGER, filename TEXT NOT NULL, content BLOB NOT NULL,
                    PRIMARY KEY (lead_id, number)
                );
                CREATE TABLE IF NOT EXISTS rate (key TEXT NOT NULL, at TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS rate_key ON rate(key,at);
            """)

    def connect(self):
        db = sqlite3.connect(self.db, isolation_level=None, timeout=12)
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA secure_delete=ON")
        return db

    def limited(self, peer):
        now = datetime.now(timezone.utc)
        window = (now - timedelta(minutes=10)).isoformat()
        marker = digest(self.password.encode(), peer.encode(), "sha256").hex()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM rate WHERE at < ?", (window,))
            count = db.execute("SELECT COUNT(*) FROM rate WHERE key=?", (marker,)).fetchone()[0]
            if count >= 16:
                db.rollback()
                return True
            db.execute("INSERT INTO rate VALUES (?,?)", (marker, now.isoformat()))
            db.commit()
        return False

    def receive(self, env):
        if env.get("HTTP_ORIGIN") != self.origin:
            return "403 Forbidden", {"ok":False}
        if self.limited(env.get("REMOTE_ADDR") or "unknown"):
            return "429 Too Many Requests", {"ok":False}
        try:
            data, photos = parse_request(env, self.version)
        except (BadRequest, ValueError, KeyError, TypeError, UnicodeError, RecursionError):
            return "400 Bad Request", {"ok":False}

        lead_id = data.pop("id")
        at = datetime.now(timezone.utc).isoformat()
        record = json.dumps(data, ensure_ascii=False, sort_keys=True)
        checksum = sha256(record.encode())
        for filename, blob in photos:
            checksum.update(filename.encode())
            checksum.update(sha256(blob).digest())
        fingerprint = checksum.hexdigest()
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT hash FROM lead WHERE id=?", (lead_id,)).fetchone()
            if existing:
                db.rollback()
                if not compare_digest(existing[0], fingerprint):
                    return "409 Conflict", {"ok":False}
            else:
                db.execute("INSERT INTO lead VALUES (?,?,?,?,?)",
                           (lead_id, at, record, json.dumps(self.document, ensure_ascii=False), fingerprint))
                db.executemany("INSERT INTO photo VALUES (?,?,?,?)",
                               [(lead_id, i, name, content) for i, (name, content) in enumerate(photos, 1)])
                db.commit()
        return "200 OK", {"ok":True, "id":lead_id}

    def authenticated(self, env):
        auth = env.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Basic ") or len(auth) > 512:
            return False
        try:
            token = b64decode(auth[6:], validate=True)
        except ValueError:
            return False
        return compare_digest(token, ("olesya:" + self.password).encode())

    def admin(self, path):
        match = re.fullmatch(r"/inbox/([0-9a-f-]{36})/photo/([1-5])", path)
        with self.connect() as db:
            if match:
                entry = db.execute("SELECT filename,content FROM photo WHERE lead_id=? AND number=?", match.groups()).fetchone()
                if not entry:
                    return "404 Not Found", "text/plain", b"", []
                header = [("Content-Disposition", "attachment; filename*=UTF-8''" + quote(entry[0],safe=""))]
                return "200 OK", "application/octet-stream", entry[1], header
            if path != "/inbox":
                return "404 Not Found", "text/plain", b"", []
            rows = db.execute("SELECT id,at,payload,doc FROM lead ORDER BY at DESC LIMIT 300").fetchall()
            cards = []
            for lead_id, at, payload, consent in rows:
                files = db.execute("SELECT number,filename FROM photo WHERE lead_id=? ORDER BY number", (lead_id,)).fetchall()
                links = "".join(f'<li><a href="inbox/{lead_id}/photo/{number}">{escape(name)}</a></li>' for number, name in files)
                lead_data = escape(json.dumps(json.loads(payload), ensure_ascii=False, indent=2))
                evidence = escape(json.dumps(json.loads(consent), ensure_ascii=False, indent=2))
                cards.append(f'<article><h2>{escape(at)}</h2><pre>{lead_data}</pre><ul>{links}</ul><details><summary>Согласие</summary><pre>{evidence}</pre></details></article>')
        body = '''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Заявки ДЕКОРИИ</title>
<style>body{font:16px system-ui;max-width:860px;margin:auto;padding:22px;background:#f6f0e5;color:#281c20}article{background:#fff;padding:16px;margin-block:18px}pre{white-space:pre-wrap;overflow-wrap:anywhere}h2{font-size:16px}</style><h1>Заявки ДЕКОРИИ</h1>''' + ("".join(cards) or "<p>Заявок пока нет.</p>") + "</html>"
        return "200 OK", "text/html; charset=UTF-8", body.encode(), [("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'")]

    def __call__(self, env, start_response):
        path = env.get("PATH_INFO", "")
        method = env.get("REQUEST_METHOD", "")
        headers = [("Cache-Control","no-store"),("X-Content-Type-Options","nosniff"),("X-Robots-Tag","noindex")]
        status = "404 Not Found"
        content_type = "application/json; charset=UTF-8"
        body = b'{"ok":false}'
        if path == "/lead":
            headers.append(("Vary", "Origin"))
            if env.get("HTTP_ORIGIN") == self.origin:
                headers.extend([("Access-Control-Allow-Origin", self.origin), ("Access-Control-Allow-Methods", "POST, OPTIONS")])
            if method == "POST":
                status, result = self.receive(env)
                body = json.dumps(result).encode()
            elif method == "OPTIONS" and env.get("HTTP_ORIGIN") == self.origin:
                status, body = "204 No Content", b""
            else:
                status = "405 Method Not Allowed"
        elif path == "/healthz" and method == "GET":
            status, body = "200 OK", b'{"ok":true}'
        elif path.startswith("/inbox") and method == "GET":
            if self.authenticated(env):
                status, content_type, body, extra = self.admin(path)
                headers.extend(extra)
            else:
                status = "401 Unauthorized"
                headers.append(("WWW-Authenticate", 'Basic realm="DEKORIYA"'))
        headers.extend([("Content-Type",content_type),("Content-Length",str(len(body)))])
        start_response(status,headers)
        return [body]

    def purge(self, before):
        with self.connect() as db:
            return db.execute("DELETE FROM lead WHERE at < ?", (before,)).rowcount


def bounded(value, size, required=False):
    if not isinstance(value,str) or len(value) > size or (required and not value.strip()):
        raise BadRequest()
    return value.strip()


def subset(raw, keys, max_length):
    if not isinstance(raw, dict):
        raise BadRequest()
    return {key: bounded(value, max_length) for key,value in raw.items() if key in keys}


def parse_request(env, version):
    content_type = env.get("CONTENT_TYPE","")
    size = int(env.get("CONTENT_LENGTH") or 0)
    if not content_type.startswith("multipart/form-data;") or "\n" in content_type or "\r" in content_type:
        raise BadRequest()
    if size < 1 or size > 51*MIB:
        raise BadRequest()
    raw = env["wsgi.input"].read(size)
    message = BytesParser(policy=default).parsebytes(b"Content-Type: " + content_type.encode("ascii") + b"\r\n\r\n" + raw)
    if not message.is_multipart() or message.defects:
        raise BadRequest()
    lead = None
    photos = []
    for part in message.iter_parts():
        name = part.get_param("name",header="content-disposition")
        blob = part.get_payload(decode=True)
        if not isinstance(blob,bytes):
            raise BadRequest()
        if name == "lead" and lead is None and len(blob) <= 12_000:
            lead = json.loads(blob.decode())
        elif name == "photos" and 0 < len(blob) <= 10*MIB and len(photos) < 5:
            ext = filetype.guess_extension(blob)
            if ext not in {"jpg","png","webp"}:
                raise BadRequest()
            photos.append((f"photo-{len(photos)+1}.{ext}",blob))
        else:
            raise BadRequest()
    if not isinstance(lead,dict) or lead.get("honeypot") or lead.get("source") not in SOURCES:
        raise BadRequest()
    agreement = lead.get("consent")
    quiz = lead["source"] == "quiz_v10"
    if not isinstance(agreement,dict) or agreement.get("given") is not True or agreement.get("version") != version:
        raise BadRequest()
    lead_id = bounded(lead.get("id"),36,True)
    phone = bounded(lead.get("phone"),12,True)
    if not UUID.fullmatch(lead_id) or not re.fullmatch(r"\+7[0-9]{10}",phone):
        raise BadRequest()
    data = {"id":lead_id, "source":lead["source"],"channel":"call",
            "name":bounded(lead.get("name"),80,quiz), "phone":phone,
            "object":bounded(lead.get("object"),1000,quiz),
            "context":subset(lead.get("context",{}),CONTEXT,1000),
            "tracking":subset(lead.get("tracking",{}),TRACK,120)}
    if not quiz and photos:
        raise BadRequest()
    if quiz:
        zones = lead.get("zones")
        if not isinstance(zones,list) or not 1 <= len(zones) <= 4 or any(z not in OPTIONS["zones"] for z in zones):
            raise BadRequest()
        if len(zones) > 1 and "Пока не знаю — нужен совет" in zones:
            raise BadRequest()
        for key in ("object","mood","install_window"):
            value = lead.get(key)
            if value not in OPTIONS[key]:
                raise BadRequest()
            data[key] = value
        data["zones"] = list(dict.fromkeys(zones))
        data["photos_later"] = lead.get("photos_later") is True
        if data["photos_later"] and photos:
            raise BadRequest()
    return data, photos


def create_app():
    return Inbox()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8781)
    parser.add_argument("--purge-before", help="UTC ISO timestamp; permanently deletes older leads and their images.")
    args = parser.parse_args()
    app = create_app()
    if args.purge_before:
        cutoff = datetime.fromisoformat(args.purge_before)
        if cutoff.tzinfo is None:
            parser.error("Timestamp needs an explicit time zone.")
        print(app.purge(cutoff.astimezone(timezone.utc).isoformat()))
    else:
        with make_server("127.0.0.1", args.port, app) as server:
            server.serve_forever()
