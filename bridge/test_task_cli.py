import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import task_cli


class FakePort:
    def __init__(self, replies=(), fail_write=False, on_write=None):
        self.replies = list(replies)
        self.writes = []
        self.fail_write = fail_write
        self.on_write = on_write

    def write(self, data):
        if self.fail_write:
            raise OSError("disconnected")
        self.writes.append(data)
        if self.on_write:
            self.on_write()
        return len(data)

    def read(self, _size):
        return self.replies.pop(0) if self.replies else b""


class TaskCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.temp.name, "ledger.sqlite3")
        self.conn = task_cli.connect(self.db)
        self.task_id, self.node_id = task_cli.create_task(self.conn, "阅读论文", "读完这一节并写一句理解")

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def confirm(self, answer="完成"):
        return task_cli.confirm_node(self.conn, self.node_id, input_func=lambda _prompt: answer, output=lambda _text: None)

    def test_cancel_sends_nothing_and_does_not_confirm(self):
        self.assertFalse(self.confirm("取消"))
        row = task_cli.get_node(self.conn, self.node_id)
        self.assertIsNone(row["confirmed_at"])
        port = FakePort()
        self.assertEqual(task_cli.sync_pending(self.conn, port, output=lambda _text: None), [])
        self.assertEqual(port.writes, [])

    def test_confirmation_is_saved_before_any_usb_send(self):
        self.assertTrue(self.confirm())
        def inspect_durable_ledger():
            independent = task_cli.connect(self.db)
            try:
                row = task_cli.get_node(independent, self.node_id)
                self.assertIsNotNone(row["confirmed_at"])
                self.assertEqual(row["confirmed_text"], "读完这一节并写一句理解")
            finally:
                independent.close()

        port = FakePort(on_write=inspect_durable_ledger)
        task_cli.sync_pending(self.conn, port, output=lambda _text: None, ack_timeout=0)
        self.assertEqual(len(port.writes), 1)
        self.assertEqual(json.loads(port.writes[0]), {
            "type": "node_complete", "protocol": 2, "version": 1,
            "task_id": self.task_id, "node_id": self.node_id, "confirmed": True,
        })

    def test_lost_ack_retries_the_exact_same_ids_and_duplicate_syncs(self):
        self.confirm()
        first = FakePort()
        task_cli.sync_pending(self.conn, first, output=lambda _text: None, ack_timeout=0)
        self.assertIsNone(task_cli.get_node(self.conn, self.node_id)["synced_at"])
        duplicate = {"type": "node_ack", "protocol": 2, "node_id": self.node_id, "status": "duplicate"}
        second = FakePort([(json.dumps(duplicate) + "\n").encode()])
        task_cli.sync_pending(self.conn, second, output=lambda _text: None)
        self.assertEqual(json.loads(first.writes[0])["node_id"], json.loads(second.writes[0])["node_id"])
        self.assertEqual(json.loads(first.writes[0])["task_id"], json.loads(second.writes[0])["task_id"])
        self.assertIsNotNone(task_cli.get_node(self.conn, self.node_id)["synced_at"])

    def test_ack_with_wrong_id_is_ignored(self):
        self.confirm()
        wrong = {"type": "node_ack", "protocol": 2, "node_id": "node-wrong", "status": "applied"}
        port = FakePort([(json.dumps(wrong) + "\n").encode()])
        task_cli.sync_pending(self.conn, port, output=lambda _text: None, ack_timeout=0.01)
        row = task_cli.get_node(self.conn, self.node_id)
        self.assertIsNone(row["synced_at"])
        self.assertIn("未收到匹配 ACK", row["last_status"])

    def test_queue_is_preserved_when_disconnect_occurs(self):
        self.confirm()
        task_cli.sync_pending(self.conn, FakePort(fail_write=True), output=lambda _text: None)
        row = task_cli.get_node(self.conn, self.node_id)
        self.assertIsNone(row["synced_at"])
        self.assertEqual(row["last_status"], "USB 断开：待同步")

    def test_confirmed_is_displayed_as_pending_before_sync(self):
        self.confirm()
        output = []
        task_cli.display_node(task_cli.get_node(self.conn, self.node_id), output.append)
        self.assertIn("状态：待同步", output)


if __name__ == "__main__":
    unittest.main()
