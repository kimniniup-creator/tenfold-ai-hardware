"""Local, user-confirmed task-node delivery over the protocol-2 USB bridge.

This is intentionally a command-line companion, not a background daemon.  A
node never reaches USB until a person has read it and typed the confirmation
word at an interactive prompt.  The SQLite ledger remains the source of truth
when USB is unavailable.
"""
import argparse
import contextlib
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from serial_frames import JsonLines, open_device

ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
ACK_SUCCESS = {"applied", "duplicate"}
ACK_FAILURE = {"conflict", "reject", "storage_error", "capacity_full"}
DEFAULT_DATABASE = Path(".delivery") / "task_cli.sqlite3"


def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(kind):
    value = kind + "-" + uuid.uuid4().hex
    if not ID_RE.fullmatch(value):  # Defensive: the device protocol is strict.
        raise ValueError("generated an unsafe identifier")
    return value


def connect(database):
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS tasks (
          task_id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS nodes (
          node_id TEXT PRIMARY KEY,
          task_id TEXT NOT NULL REFERENCES tasks(task_id),
          node_text TEXT NOT NULL,
          created_at TEXT NOT NULL,
          confirmed_at TEXT,
          confirmed_text TEXT,
          synced_at TEXT,
          last_status TEXT
        );
        CREATE INDEX IF NOT EXISTS nodes_pending ON nodes(synced_at, confirmed_at);
        """
    )
    return conn


def create_task(conn, title, node_text):
    if not title.strip() or not node_text.strip():
        raise ValueError("任务标题和节点内容都不能为空")
    task_id, node_id, created = new_id("task"), new_id("node"), now_utc()
    with conn:
        conn.execute("INSERT INTO tasks(task_id,title,created_at) VALUES(?,?,?)", (task_id, title, created))
        conn.execute(
            "INSERT INTO nodes(node_id,task_id,node_text,created_at) VALUES(?,?,?,?)",
            (node_id, task_id, node_text, created),
        )
    return task_id, node_id


def add_node(conn, task_id, node_text):
    if not ID_RE.fullmatch(task_id) or not node_text.strip():
        raise ValueError("任务 ID 或节点内容无效")
    if conn.execute("SELECT 1 FROM tasks WHERE task_id=?", (task_id,)).fetchone() is None:
        raise ValueError("找不到该任务")
    node_id, created = new_id("node"), now_utc()
    with conn:
        conn.execute(
            "INSERT INTO nodes(node_id,task_id,node_text,created_at) VALUES(?,?,?,?)",
            (node_id, task_id, node_text, created),
        )
    return node_id


def get_node(conn, node_id):
    return conn.execute(
        """SELECT n.*, t.title FROM nodes n JOIN tasks t ON t.task_id=n.task_id
           WHERE n.node_id=?""",
        (node_id,),
    ).fetchone()


def state_label(row):
    if row["synced_at"]:
        return "已同步"
    if row["confirmed_at"]:
        return "待同步"
    return "未确认"


def display_node(row, output=print):
    output("任务：" + row["title"])
    output("节点：" + row["node_text"])
    output("任务 ID：" + row["task_id"])
    output("节点 ID：" + row["node_id"])
    output("状态：" + state_label(row))
    if row["last_status"] and not row["synced_at"]:
        output("上次同步结果：" + row["last_status"])


def confirm_node(conn, node_id, input_func=input, output=print):
    row = get_node(conn, node_id)
    if row is None:
        raise ValueError("找不到该节点")
    display_node(row, output)
    if row["confirmed_at"]:
        output("该节点已确认；如未同步，请执行 sync 重试。")
        return False
    answer = input_func("请核对以上任务和节点。输入“完成”以确认；其他输入均取消：").strip()
    if answer != "完成":
        output("已取消：未保存确认，未发送任何 USB 数据。")
        return False
    # The confirmation transaction completes before any caller can obtain USB.
    with conn:
        conn.execute(
            """UPDATE nodes SET confirmed_at=?, confirmed_text=?, last_status=?
               WHERE node_id=? AND confirmed_at IS NULL""",
            (now_utc(), row["node_text"], "待同步", node_id),
        )
    output("已保存本地确认，状态：待同步。请显式执行 sync 发送到设备。")
    return True


class DeliveryLock:
    """A tiny process-local lock file; held only during an explicit sync."""

    def __init__(self, database):
        self.path = str(Path(database).with_suffix(Path(database).suffix + ".lock"))
        self.handle = None

    def __enter__(self):
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.handle = open(self.path, "a+b")
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                if self.handle.tell() == 0 and os.path.getsize(self.path) == 0:
                    self.handle.write(b"0")
                    self.handle.flush()
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            self.handle.close()
            self.handle = None
            raise RuntimeError("已有另一个 task-cli sync 正在使用 USB") from exc
        return self

    def __exit__(self, *_):
        if self.handle is None:
            return
        try:
            if os.name == "nt":
                import msvcrt
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        finally:
            self.handle.close()
            self.handle = None


def pending_nodes(conn):
    return conn.execute(
        """SELECT n.*, t.title FROM nodes n JOIN tasks t ON t.task_id=n.task_id
           WHERE n.confirmed_at IS NOT NULL AND n.synced_at IS NULL
           ORDER BY n.confirmed_at, n.node_id"""
    ).fetchall()


def _write_node(port, row):
    message = {
        "type": "node_complete", "protocol": 2, "version": 1,
        "task_id": row["task_id"], "node_id": row["node_id"], "confirmed": True,
    }
    # Values are generated/validated locally; retain the invariant before USB.
    if not ID_RE.fullmatch(message["task_id"]) or not ID_RE.fullmatch(message["node_id"]):
        raise ValueError("unsafe task or node ID in ledger")
    port.write((json.dumps(message, separators=(",", ":")) + "\n").encode("ascii"))


def wait_for_ack(port, expected_node_id, timeout_seconds=.5):
    frames, deadline = JsonLines(512), time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        chunk = port.read(512)
        if not chunk:
            # Real serial reads normally block for their configured timeout; this
            # also avoids spinning if a transport implementation returns early.
            time.sleep(min(.01, max(0, deadline - time.monotonic())))
        for frame in frames.feed(chunk):
            if frame.get("type") != "node_ack" or frame.get("protocol") != 2:
                continue
            if frame.get("node_id") != expected_node_id:
                continue
            status = frame.get("status")
            if isinstance(status, str) and status in ACK_SUCCESS | ACK_FAILURE:
                return status
    return None


def sync_pending(conn, port, output=print, ack_timeout=.5):
    """Send already-confirmed rows once each; a missing ACK leaves them pending."""
    results = []
    for row in pending_nodes(conn):
        try:
            _write_node(port, row)
            status = wait_for_ack(port, row["node_id"], ack_timeout)
        except (OSError, IOError) as exc:
            with conn:
                conn.execute("UPDATE nodes SET last_status=? WHERE node_id=?", ("USB 断开：待同步", row["node_id"]))
            output("USB 断开；队列已保留，未同步节点仍待同步。")
            break
        if status in ACK_SUCCESS:
            with conn:
                conn.execute(
                    "UPDATE nodes SET synced_at=?, last_status=? WHERE node_id=?",
                    (now_utc(), "已同步（" + status + "）", row["node_id"]),
                )
            output("已同步：" + row["node_id"] + "（" + status + "）")
            results.append((row["node_id"], status))
        elif status:
            with conn:
                conn.execute("UPDATE nodes SET last_status=? WHERE node_id=?", ("设备拒绝：" + status, row["node_id"]))
            output("未同步：" + row["node_id"] + "（设备回复 " + status + "，保留待同步）")
            results.append((row["node_id"], status))
        else:
            with conn:
                conn.execute("UPDATE nodes SET last_status=? WHERE node_id=?", ("未收到匹配 ACK：待同步", row["node_id"]))
            output("未收到匹配 ACK：" + row["node_id"] + "，保留待同步并可用相同 ID 重试。")
            results.append((row["node_id"], None))
    return results


def command_sync(conn, database, port_name, output=print):
    rows = pending_nodes(conn)
    if not rows:
        output("没有待同步的已确认节点。")
        return 0
    # This is the sole code path that opens a serial device.
    with DeliveryLock(database):
        with contextlib.closing(open_device(port_name, timeout=.05, write_timeout=.2)) as port:
            sync_pending(conn, port, output)
    return 0


def command_list(conn, output=print):
    rows = conn.execute(
        """SELECT n.*, t.title FROM nodes n JOIN tasks t ON t.task_id=n.task_id
           ORDER BY n.created_at, n.node_id"""
    ).fetchall()
    if not rows:
        output("还没有本地任务节点。")
    for row in rows:
        output("[{}] {} / {}\n  {}\n  {}".format(state_label(row), row["title"], row["node_id"], row["node_text"], row["task_id"]))


def command_status(conn, output=print):
    row = conn.execute(
        """SELECT COUNT(*) AS all_nodes,
                  SUM(confirmed_at IS NOT NULL) AS confirmed_nodes,
                  SUM(synced_at IS NOT NULL) AS synced_nodes
           FROM nodes"""
    ).fetchone()
    total = row["all_nodes"]
    confirmed = row["confirmed_nodes"] or 0
    synced = row["synced_nodes"] or 0
    output("本地节点：{}；已确认：{}；已同步：{}；待同步：{}。".format(total, confirmed, synced, confirmed - synced))


def main(argv=None):
    parser = argparse.ArgumentParser(description="任务节点确认与 USB 同步（不会自动确认或后台发送）")
    parser.add_argument("--database", default=str(DEFAULT_DATABASE), help="本地 SQLite 账本路径")
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create", help="创建一个任务及首个节点")
    create.add_argument("--title", required=True)
    create.add_argument("--node", required=True)
    add = sub.add_parser("add-node", help="向已有任务添加节点")
    add.add_argument("task_id")
    add.add_argument("--node", required=True)
    show = sub.add_parser("show", help="只读显示节点")
    show.add_argument("node_id")
    sub.add_parser("list", help="只读列出本地节点")
    sub.add_parser("status", help="只读汇总本地确认与同步状态")
    confirm = sub.add_parser("confirm", help="交互确认一个节点；不会发送 USB")
    confirm.add_argument("node_id")
    sync = sub.add_parser("sync", help="显式发送所有待同步确认")
    sync.add_argument("--port", required=True, help="要打开的串口，例如 COM10")
    args = parser.parse_args(argv)
    try:
        conn = connect(args.database)
        try:
            if args.command == "create":
                task_id, node_id = create_task(conn, args.title, args.node)
                print("已创建任务：{}\n首个节点：{}\n状态：未确认".format(task_id, node_id))
            elif args.command == "add-node":
                print("已创建节点：{}\n状态：未确认".format(add_node(conn, args.task_id, args.node)))
            elif args.command == "show":
                row = get_node(conn, args.node_id)
                if row is None:
                    raise ValueError("找不到该节点")
                display_node(row)
            elif args.command == "list":
                command_list(conn)
            elif args.command == "status":
                command_status(conn)
            elif args.command == "confirm":
                confirm_node(conn, args.node_id)
            elif args.command == "sync":
                return command_sync(conn, args.database, args.port)
        finally:
            conn.close()
    except (ValueError, RuntimeError, OSError, sqlite3.Error) as exc:
        print("错误：" + str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
