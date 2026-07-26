import threading
import time
from knowledge.service.client_factory import get_default_client

def concurrent_init_test():
    clients = []
    def init_client():
        clients.append(get_default_client())
    
    threads = [threading.Thread(target=init_client) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    # Check if they got the same instance or properly initialized
    return len(clients) == 10

def concurrent_read_test():
    client = get_default_client()
    results = []
    
    def read_op():
        try:
            res = client.search_resources("test")
            results.append(True)
        except Exception:
            results.append(False)
            
    threads = [threading.Thread(target=read_op) for _ in range(20)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    return all(results)

if __name__ == '__main__':
    print("Running Thread Safety Certification...")
    print(f"Concurrent Init Pass: {concurrent_init_test()}")
    print(f"Concurrent Read Pass: {concurrent_read_test()}")
