import docker
import os
import sys
from orchestrator import SutureBrain
from dotenv import load_dotenv

class DockerWatcher:
    def __init__(self):
        load_dotenv()
        self.client = docker.from_env()
        self.brain = SutureBrain()

    def start_monitoring(self):
        print("[*] Suture_CI Watcher active. Monitoring all container exits...")

        try:
            for event in self.client.events(decode=True):
                if event.get('Action') in ['die', 'oom']:
                    actor = event.get('Actor', {})
                    attrs = actor.get('Attributes', {})
                    
                    container_name = attrs.get('name', 'unknown')
                    exit_code = int(attrs.get('exitCode', 0))

                    if exit_code != 0:
                        print(f"\n[!] CRASH DETECTED: {container_name} (Code: {exit_code})")
                        
                        container_id = event['id']
                        container = self.client.containers.get(container_id)

                        raw_logs = container.logs().decode('utf-8')
                        print("[*] Extracting error context and sending to Brain...")

                        self.brain.run_healing_cycle(raw_logs, "app.py")
        except KeyboardInterrupt:
            print("\n[*] Stopping Watcher...")
            sys.exit(0)

if __name__ == "__main__":
    watcher = DockerWatcher()
    watcher.start_monitoring()