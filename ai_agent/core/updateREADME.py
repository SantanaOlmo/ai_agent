from github import Github, Auth
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO", "SantanaOlmo/webAI")  # Puedes definir repo en .env
FILE_PATH = "README.md"

def push_readme_local_to_github():
    if not TOKEN:
        raise ValueError("No se encontró GITHUB_TOKEN en .env")
    g = Github(auth=Auth.Token(TOKEN))
    repo = g.get_repo(REPO)

    readme_remote = repo.get_contents(FILE_PATH)
    readme_local = Path(FILE_PATH).read_text(encoding="utf-8")

    repo.update_file(
        path=FILE_PATH,
        message="Updated README.md automáticamente",
        content=readme_local,
        sha=readme_remote.sha
    )
    print("✅ README.md subido a GitHub correctamente.")
