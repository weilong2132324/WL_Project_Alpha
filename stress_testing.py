import redis
import threading
import time 
import random
import string 

REDIS_HOST = "localhost"
REDIS_PORT = 6379
NUM_THREADS = 100
REQUESTS_PER_THREAD = 1000

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def stress_worker(thread_id):
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    for i in range(REQUESTS_PER_THREAD): 
        try:
            key = f"thread:{thread_id}:key:{i}"
            value = generate_random_string(10)

            client.set(key, value)
            client.get(key)
            client.delete(key)
            
        except Exception as e:
            print(f"Error: {e}")
        
    client.close()

def main():
    print(f"Starting stress test: {NUM_THREADS} threads, {REQUESTS_PER_THREAD} requests each")
    print(f"Total requests: {NUM_THREADS * REQUESTS_PER_THREAD * 3}")  # 3 ops per iteration
    
    start = time.time()
    
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=stress_worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    elapsed = time.time() - start
    total_ops = NUM_THREADS * REQUESTS_PER_THREAD * 3
    print(f"\nCompleted in {elapsed:.2f} seconds")
    print(f"Operations/second: {total_ops/elapsed:.0f}")

if __name__ == "__main__":
    main()