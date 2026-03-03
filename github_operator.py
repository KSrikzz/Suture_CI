import os
from github import Github
from github.GithubException import GithubException
from dotenv import load_dotenv

class GitOperator:
    def __init__(self, token, repo_name):
        self.g = Github(token)
        self.repo = self.g.get_repo(repo_name)

    def create_fix_pr(self, branch_name, file_path, new_content, commit_message, pr_title, pr_body):
        try:
            source_branch = self.repo.default_branch
            source_branch_ref = self.repo.get_branch(source_branch)

            self.repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source_branch_ref.commit.sha)
            print(f"[*] Created new branch: {branch_name}")

            file = self.repo.get_contents(file_path, ref=source_branch)

            self.repo.update_file(
                path=file.path,
                message=commit_message,
                content=new_content,
                sha=file.sha,
                branch=branch_name
            )
            print(f"[*] Committed changes to: {file_path}")

            pr = self.repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=source_branch
            )
            print(f"[+] Success! Pull Request created at: {pr.html_url}")
            
            try:
                pr.add_to_labels("autofix", "ai-generated")
                print("[*] Labels 'autofix' and 'ai-generated' added to PR.")
            except Exception as e:
                print(f"[!] Could not add labels: {e}")
                
        except GithubException as e:
            print(f"[-] GitHub API Error: {e}")

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("GITHUB_TOKEN") 
    REPO_NAME = os.getenv("GITHUB_REPO")
    
    if not TOKEN or not REPO_NAME:
        print("[-] Error: Missing environment variables.")
        print("Please set both GITHUB_TOKEN and GITHUB_REPO before running.")
    else:
        agent = GitOperator(TOKEN, REPO_NAME)
        print(f"[*] GitOperator successfully initialized for {REPO_NAME}!")
        print("[*] Attempting to create a test PR...")
        
        branch = "suture-ai/test-fix-02"
        target_file = "target_file.txt" 
        new_code = "This file has been successfully healed by Suture_CI using environment variables.\n"
        message = "fix: automated resolution via env vars"
        title = "🤖 Suture_CI: Automated Repair (Env Var Test)"
        body = "### Root Cause Analysis\nSuccessfully tested environment variable configuration.\n\n*This PR was generated automatically by Suture_CI.*"

        agent.create_fix_pr(branch, target_file, new_code, message, title, body)