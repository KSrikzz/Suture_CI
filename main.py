from monitor.watcher import DockerWatcher

if __name__ == "__main__":
    agent = DockerWatcher()
    agent.start_monitoring()