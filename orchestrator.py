import os
import ollama
from log_parser import LogParser
from github_operator import GitOperator
from dotenv import load_dotenv

class SutureBrain:
    def __init__(self):
        load_dotenv()
        self.parser = LogParser()
        self.git = GitOperator(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPO"))
        self.model = "qwen2.5-coder:7b" #

    def ask_ai_for_fix(self, logs, source_code):
        """The core reasoning step: Diagnoses and heals the code."""
        prompt = f"""
        [ROLE] You are SUTURE_CI, an autonomous self-healing agent.
        [CONTEXT] A build failed. Analyze these logs and the source code.
        
        ERROR LOGS:
        {logs}

        SOURCE CODE:
        {source_code}

        [INSTRUCTION]
        1. Identify the bug.
        2. Provide ONLY the complete, corrected code for the file.
        3. Do not include markdown blocks (```), explanations, or commentary.
        """
        response = ollama.generate(model=self.model, prompt=prompt)
        return response['response'].strip()

    def run_healing_cycle(self, raw_logs, target_file_path):
        error_blocks = self.parser.extract_error_context(raw_logs)
        if not error_blocks:
            print("[-] No errors detected. Nothing to heal.")
            return
        with open(target_file_path, "r") as f:
            original_code = f.read()

        print(f"[*] Brain is analyzing crash via {self.model}...")
        fixed_code = self.ask_ai_for_fix(error_blocks[0], original_code)

        print("[*] Hands are opening the Pull Request...")
        self.git.create_fix_pr(
            branch_name="suture/auto-fix-01",
            file_path=target_file_path,
            new_content=fixed_code,
            commit_message="fix: autonomous repair of detected crash",
            pr_title="🤖 Suture_CI: Automated Repair",
            pr_body="This PR was generated automatically by Suture_CI after detecting an error in the logs."
        )

if __name__ == "__main__":
    DUMMY_LOGS = "ERROR: Payment processing failed\nTraceback...\nConnectionError: Timeout"
    brain = SutureBrain()
    brain.run_healing_cycle(DUMMY_LOGS, "target_file.txt")