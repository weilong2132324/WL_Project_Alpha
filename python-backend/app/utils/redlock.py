"""Simple Redlock implementation (synchronous) for the python-backend.

This implements the algorithm from the Redis Redlock specification:
https://redis.io/docs/reference/patterns/distributed-locks/

Usage example:
    from app.utils.redlock import Redlock
    clients = [redis.Redis(host='redis1', port=6379), ...]
    rl = Redlock(clients)
    lock = rl.lock("my-resource", ttl=8000)  # ttl in milliseconds
    if lock.locked:
        try:
            # critical section
            pass
        finally:
            lock.unlock()

This implementation uses the redis-py client already present in requirements.
"""

from __future__ import annotations

import time
import uuid
import random
from typing import List, Optional

import redis



class Lock:
    def __init__(self, resource: str, token: str, validity: int, clients: List[redis.Redis], fencing_token: Optional[int] = None):
        self.resource = resource
        self.token = token
        self.validity = validity  # milliseconds
        self.clients = clients
        self.locked = True
        self.fencing_token = fencing_token  # Monotonically increasing fencing token

    def unlock(self) -> bool:
        """Release the lock on all instances using an atomic check-and-del Lua script.

        Returns True if at least one instance released the lock.
        """
        if not self.locked:
            return False

        lua = (
            "if redis.call('get',KEYS[1]) == ARGV[1] then "
            "return redis.call('del',KEYS[1]) else return 0 end"
        )
        
        released = 0
        for c in self.clients:
            try:
                res = c.eval(lua, 1, self.resource, self.token)
                if isinstance(res, int) and res > 0:
                    released += 1
            except Exception:
                # ignore failures during unlock
                pass

        self.locked = False
        return released > 0


class Redlock:
    def __init__(self, clients: List[redis.Redis]):
        if not clients:
            raise ValueError("At least one redis client is required")
        self.clients = clients
        self.quorum = len(clients) // 2 + 1

    def _set_lock_instance(self, client: redis.Redis, resource: str, token: str, ttl: int) -> bool:
        # ttl in milliseconds; redis-py expects px for milliseconds
        try:
            # Using set with nx and px for atomic set-if-not-exists with expiry
            return client.set(resource, token, nx=True, px=ttl)
        except Exception:
            return False

    def lock(self, resource: str, ttl: int = 10000, retry_count: int = 3, retry_delay: float = 0.2) -> Lock:
        """Attempt to acquire a distributed lock.

        Args:
            resource: lock key
            ttl: lock expiry in milliseconds
            retry_count: number of attempts
            retry_delay: base delay between retries in seconds (jitter applied)

        Returns a Lock object with `.locked` == True when acquired; otherwise a Lock with `.locked` False.
        """
        for attempt in range(retry_count):
            token = uuid.uuid4().hex
            start = int(time.time() * 1000)
            success_count = 0
            for client in self.clients:
                if self._set_lock_instance(client, resource, token, ttl):
                    success_count += 1

            elapsed = int(time.time() * 1000) - start
            validity = ttl - elapsed

            if success_count >= self.quorum and validity > 0:
                # Issue fencing token using INCR on a dedicated key (use first client)
                fencing_token = None
                try:
                    # Fencing key: resource + ":fencing"
                    fencing_key = f"{resource}:fencing"
                    fencing_token = self.clients[0].incr(fencing_key)
                except Exception:
                    pass
                return Lock(resource, token, validity, self.clients, fencing_token)

            # failed to acquire majority, clean up any locks we set
            lua = (
                "if redis.call('get',KEYS[1]) == ARGV[1] then "
                "return redis.call('del',KEYS[1]) else return 0 end"
            )
            for client in self.clients:
                try:
                    client.eval(lua, 1, resource, token)
                except Exception:
                    pass

            # wait before retry with jitter
            time.sleep(retry_delay + random.uniform(0, retry_delay))

        # return unlocked lock object
        return Lock(resource, "", 0, self.clients, None)


__all__ = ["Redlock", "Lock"]
