import logging
from knowledge.service.client_factory import get_default_client
from knowledge.extractors.extractor_registry import ExtractorRegistry
from knowledge.processing.parsers.parser_registry import ParserRegistry

logging.basicConfig(level=logging.INFO)

def run_self_test():
    print("Initializing Platform...")
    client = get_default_client()
    
    # 1. Start lifecycle
    if hasattr(client.service, "start"):
        client.service.start()
        
    print("Testing Registries...")
    parser_registry = ParserRegistry()
    assert parser_registry.get_parser("json") is not None
    
    extractor_registry = ExtractorRegistry()
    # extractor_registry is empty by default, just assert it loads
    assert isinstance(extractor_registry._extractors, dict)
    
    print("Testing Health...")
    health = client.service.health()
    assert health["status"] == "HEALTHY"
    
    print("Testing Graph Query...")
    res = client.search_resources("test")
    assert isinstance(res, list)
    
    # Shutdown
    if hasattr(client.service, "shutdown"):
        client.service.shutdown()
        
    print("Platform Self-Test completed successfully.")

if __name__ == "__main__":
    run_self_test()
