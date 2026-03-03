import os
import time
import ollama
from log_parser import LogParser
from github_operator import GitOperator
from validator import Validator 
from dotenv import load_dotenv

class SutureBrain:
    def __init__(self):
        load_dotenv()
        self.parser = LogParser()
        self.git = GitOperator(os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPO"))
        self.model = "qwen2.5-coder:7b" 
        self.validator = Validator()

    def ask_ai_for_fix(self, logs, source_code, previous_error=None):
        feedback_context = ""
        if previous_error:
            feedback_context = f"\n[FEEDBACK] Your previous fix failed validation with this error: {previous_error}. Please correct it."

        prompt = f"""
        [ROLE] You are SUTURE_CI, an autonomous self-healing agent.
        [CONTEXT] A build failed. Analyze these logs and the source code.
        
        ERROR LOGS:
        {logs}

        SOURCE CODE:
        {source_code}
        {feedback_context}

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
            return        
        with open(target_file_path, "r") as f:
            original_code = f.read()

        attempts = 0
        max_attempts = 3
        current_fix = None
        last_validation_error = None

        while attempts < max_attempts:
            attempts += 1
            print(f"[*] Attempt {attempts}/{max_attempts}: Analyzing crash...")
            
            current_fix = self.ask_ai_for_fix(error_blocks[0], original_code, last_validation_error)

            temp_file = f"temp_{target_file_path}"
            with open(temp_file, "w") as f:
                f.write(current_fix)

            is_valid, error_msg = self.validator.check_syntax_with_feedback(temp_file)
            
            if is_valid:
                print(f"[+] Success on attempt {attempts}!")
                os.remove(temp_file)
                break
            else:
                print(f"[!] Validation failed. Retrying...")
                last_validation_error = error_msg
                os.remove(temp_file)
                if attempts == max_attempts:
                    print("[-] Failed to heal after max attempts. Aborting.")
                    return
        timestamp = int(time.time())
        unique_branch = f"suture/fix-{timestamp}"
        self.git.create_fix_pr(
            branch_name=unique_branch,
            file_path=target_file_path,
            new_content=current_fix,
            commit_message=f"fix: autonomous repair of detected crash(attempt {attempts})",
            pr_title=f"🤖 Suture_CI: Automated Repair ({timestamp})",
            pr_body=f"Suture_CI successfully healed the crash on attempt {attempts}."
        )