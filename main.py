# main.py
from watcher import DockerWatcher

if __name__ == "__main__":
    print("""
    =========================================
    SUTURE_CI: Autonomous Self-Healing Agent
    =========================================
    Status: ACTIVE
    Mode: Local LLM (Ollama)
    Target: Docker Environment
    """)
    
    agent = DockerWatcher()
    agent.start_monitoring()