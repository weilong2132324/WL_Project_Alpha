"""
ZooKeeper-based distributed lock with fencing tokens.
Requires: pip install kazoo
"""
from kazoo.client import KazooClient
from kazoo.exceptions import KazooException
import threading
import time

class ZKDistributedLock:
    def __init__(self, zk_hosts: str, resource: str, base_path: str = "/locks"):
        self.zk = KazooClient(hosts=zk_hosts)
        self.resource = resource
        self.base_path = base_path
        self.lock_path = f"{self.base_path}/{self.resource}"
        self.znode_path = None
        self.fencing_token = None
        self._lock = threading.Lock()

    def start(self):
        self.zk.start()
        # Ensure the base path exists
        self.zk.ensure_path(self.lock_path)

    def acquire(self, timeout: float = 10.0) -> bool:
        """Acquire the distributed lock and get a fencing token."""
        with self._lock:
            self.start()
            # Create an ephemeral sequential znode
            node = self.zk.create(f"{self.lock_path}/lock-", b"", ephemeral=True, sequence=True)
            self.znode_path = node
            # Extract fencing token (sequence number)
            self.fencing_token = int(node.split("-")[-1])
            # Wait until this node is the lowest (i.e., lock owner)
            deadline = time.time() + timeout
            while time.time() < deadline:
                children = self.zk.get_children(self.lock_path)
                children_full = [f"{self.lock_path}/" + c for c in children]
                children_full.sort()
                if children_full[0] == self.znode_path:
                    return True
                time.sleep(0.1)
            # Timeout: release node
            self.release()
            return False

    def release(self):
        with self._lock:
            if self.znode_path and self.zk.exists(self.znode_path):
                try:
                    self.zk.delete(self.znode_path)
                except KazooException:
                    pass
            self.znode_path = None
            self.fencing_token = None
            self.zk.stop()

    def __enter__(self):
        if not self.acquire():
            raise TimeoutError("Failed to acquire ZooKeeper distributed lock")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

# Example usage:
if __name__ == "__main__":
    lock = ZKDistributedLock(zk_hosts="127.0.0.1:2181", resource="my-resource")
    with lock:
        print("Lock acquired with fencing token:", lock.fencing_token)
        # critical section
        time.sleep(2)
    print("Lock released.")
