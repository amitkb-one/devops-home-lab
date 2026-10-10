# DevOps Home Lab — Project Handbook

**Last updated:** 10 October 2026  
**Environment:** Apple Silicon Mac mini Pro, 48 GB RAM  
**GitHub:** https://github.com/amitkb-one/devops-home-lab  
**Local workspace:** `~/devops-lab`  
**Purpose:** A practical, version-controlled DevOps learning environment, progressing from developer tooling to containers, CI/CD, Kubernetes, infrastructure as code, observability and security.

> **Status convention:** **Confirmed** means the user explicitly reported success. **Walkthrough** means steps were provided, but completion was not explicitly confirmed. **Pending** means planned or not yet executed.

## 1. Executive summary

We set up a development environment on an Apple Silicon Mac mini, connected Git securely to GitHub, practiced repository and branching workflows, and started Docker training. Docker Desktop and the initial container exercise were explicitly confirmed as working. A custom FastAPI Docker image lab and an environment cleanup procedure have been provided; their execution and results still need confirmation.

### Milestone tracker

| Milestone | Status | Notes |
|---|---|---|
| Xcode Command Line Tools | Confirmed | Prerequisite for local development tools |
| Homebrew | Confirmed | macOS package manager |
| Git installed/configured | Confirmed | Homebrew Git; zsh PATH adjustment discussed |
| Visual Studio Code | Confirmed | Installed using Homebrew cask |
| GitHub SSH authentication | Confirmed | `ssh -T git@github.com` succeeded |
| GitHub repository push | Confirmed | User reported push works after remote reset |
| Feature branches and pull requests | Walkthrough | Exercise provided; individual PR completion not explicitly confirmed |
| Merge conflict exercise | Walkthrough | Exercise provided; resolution not explicitly confirmed |
| Docker Desktop and Nginx | Confirmed | User reported Lab 06A done |
| FastAPI custom Docker image | Walkthrough | Detailed Lab 06B provided; completion not explicitly confirmed |
| Docker/Git cleanup | Pending | Inventory and safe deletion instructions provided; no inventory output yet |
| Networking, volumes and Compose | Pending | Next learning phase |

## 2. Environment and tools

- **Machine:** Apple Silicon Mac mini Pro, 48 GB RAM.
- **Shell:** macOS Terminal with zsh.
- **Developer prerequisites:** Xcode Command Line Tools.
- **Package manager:** Homebrew.
- **Version control:** Git and GitHub over SSH.
- **Editor:** Visual Studio Code.
- **Containers:** Docker Desktop, Linux containers running through a lightweight VM on macOS.
- **Planned later:** PostgreSQL, Docker Compose, Kubernetes, GitHub Actions, Terraform, Ansible, observability stack and GitOps.

### Useful verification commands

```bash
xcode-select -p
brew --version
git --version
code --version
ssh -T git@github.com
docker --version
docker compose version
docker info
```

**Homebrew Git PATH note:** On Apple Silicon, Homebrew typically installs under `/opt/homebrew`. If macOS system Git is selected instead of Homebrew Git, inspect `which git`, `type -a git`, and your zsh PATH. Earlier setup involved adding `/opt/homebrew/opt/git/bin` to PATH.

## 3. Repository and Git setup

**Repository:** `git@github.com:amitkb-one/devops-home-lab.git`  
**Local repository:** `~/devops-lab`  
**Primary branch:** `main`

### Everyday Git workflow

```bash
cd ~/devops-lab
git switch main
git pull --ff-only
git switch -c feature/<descriptive-name>

# Make and test changes
git status
git diff
git add <files>
git diff --staged
git commit -m "Describe the change"
git push -u origin feature/<descriptive-name>

# Open a pull request on GitHub, review, and merge

git switch main
git pull --ff-only
git branch -d feature/<descriptive-name>
```

**Remote branch deletion** is optional and should only be done after confirming the pull request was merged:

```bash
git push origin --delete feature/<descriptive-name>
```

### Important concepts

- **Working tree:** Files being edited.
- **Staging area:** Changes selected for the next commit.
- **Commit:** A versioned snapshot.
- **Branch:** An independent line of development.
- **Remote:** A named reference to another repository, commonly `origin`.
- **Pull request:** A review and merge workflow hosted by GitHub.
- **Fetch:** Retrieves remote updates without merging into the current branch.
- **Pull:** Fetches and integrates remote updates.

### Git remote troubleshooting — issue resolved

**Observed:** `git push -u origin main` and `git ls-remote origin` failed with a message resembling `'origin' does not appear to be a git repository`, although `git remote -v` appeared to show the expected GitHub SSH URL.

**Key diagnostic:** An explicit remote URL worked:

```bash
git ls-remote git@github.com:amitkb-one/devops-home-lab.git
```

This indicated that SSH authentication and the GitHub repository were reachable, while the named remote configuration was problematic.

**Resolution used:** Remove and recreate the remote:

```bash
git remote remove origin
git remote add origin git@github.com:amitkb-one/devops-home-lab.git
git remote -v
git ls-remote origin
git push -u origin main
```

**Outcome:** User confirmed it works. Exact underlying configuration defect was not conclusively established; a malformed remote setting was suspected.

### Branching exercise — Lab 04

The practice exercise used `feature/shell-lab`, a Bash system-information script, a commit, push, pull request and merge. Script commands included `hostname`, `sw_vers`, `uname -m`, `whoami`, `pwd`, `df -h /`, `sysctl -n hw.memsize`, `git --version` and `brew --version`.

### Merge conflict exercise — Lab 05

The planned exercise used competing changes to the `## Current Progress` section of `README.md` on `feature/update-readme` and `feature/docker-roadmap`. It introduced conflict markers:

```text
<<<<<<< HEAD
Current branch's version
=======
Incoming version
>>>>>>> origin/main
```

Resolution procedure: edit the file to the intended combined result, remove conflict markers, `git add README.md`, and commit the merge. Inspect the graph with:

```bash
git log --oneline --graph --decorate --all
```

**Note:** The lesson was provided; successful execution of this particular exercise was not separately confirmed.

## 4. Docker fundamentals — Lab 06A

**Status:** Confirmed completed.

### Architecture

On macOS, Docker Desktop runs Linux containers in a lightweight Linux virtual machine. An **image** is a packaged template; a **container** is an instance created from that image. Port publishing connects host ports to container ports.

### Install and verify

```bash
brew install --cask docker-desktop
open -a Docker
docker --version
docker compose version
docker info
docker info --format '{{.Architecture}}'
```

### First container

```bash
docker run --rm hello-world
```

### Nginx exercise

```bash
docker run -d --name devops-nginx -p 8080:80 nginx:alpine
# Visit http://localhost:8080

docker ps
docker logs devops-nginx
docker stats --no-stream devops-nginx
docker inspect devops-nginx

docker stop devops-nginx
docker ps -a
docker start devops-nginx
```

**Concept:** `-p 8080:80` maps port 8080 on the Mac to port 80 inside the container.

**Cleanup:**

```bash
docker stop devops-nginx
docker rm devops-nginx
```

## 5. Custom FastAPI Docker image — Lab 06B

**Status:** Walkthrough provided; completion not explicitly confirmed.

### Intended location

`~/devops-lab/04-docker/fastapi-demo/`

### Application source — `main.py`

```python
from fastapi import FastAPI
import os
import platform
import socket

app = FastAPI(title="DevOps Home Lab API", version="1.0.0")

@app.get("/")
def home():
    return {
        "message": "Welcome to my DevOps Home Lab",
        "environment": os.getenv("APP_ENV", "development"),
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/system")
def system_info():
    return {
        "hostname": socket.gethostname(),
        "architecture": platform.machine(),
        "operating_system": platform.system()
    }
```

### Dependencies — `requirements.txt`

```text
fastapi>=0.115,<1
uvicorn>=0.30,<1
```

### Container build — `Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `.dockerignore`

```text
.git
.venv
__pycache__
*.pyc
.env
.DS_Store
```

### Build, run and test

```bash
cd ~/devops-lab/04-docker/fastapi-demo
docker build -t devops-fastapi:1.0 .
docker image ls

docker run -d \
  --name fastapi-lab \
  -p 8000:8000 \
  -e APP_ENV=development \
  devops-fastapi:1.0

curl http://localhost:8000/health
# Expected: {"status":"UP"}
```

Other endpoints: `/`, `/system`, and interactive OpenAPI documentation at `/docs`.

### Inspect the container

```bash
docker ps
docker logs fastapi-lab
docker exec fastapi-lab whoami
docker exec fastapi-lab python --version
docker exec fastapi-lab uname -m
docker stats --no-stream fastapi-lab
docker history devops-fastapi:1.0
docker image inspect devops-fastapi:1.0
```

### Two containers, one image

```bash
docker run -d --name fastapi-lab-2 -p 8001:8000 devops-fastapi:1.0
curl http://localhost:8001/health
```

**Lessons:** Image reuse, separate container instances, host port uniqueness, non-root execution, image layers, and build cache. `EXPOSE` documents the intended port; it does not publish it.

### Git delivery

Suggested branch: `feature/fastapi-docker`. Commit the `04-docker/fastapi-demo/` directory, push the branch, open a pull request, merge, then pull the updated `main`.

## 6. Environment hygiene — Lab 06B.1

**Status:** Inspection and cleanup procedure documented; actual inventory and deletion not yet verified.

### Principle

**Inspect → Identify → Stop → Remove → Verify.** Avoid indiscriminate deletion.

### Docker inventory

```bash
docker ps -a
docker image ls -a
docker volume ls
docker network ls
docker system df -v
```

### Targeted container cleanup (only if they exist and are no longer needed)

```bash
docker stop fastapi-lab fastapi-lab-2
docker rm fastapi-lab fastapi-lab-2

docker stop devops-nginx
docker rm devops-nginx
```

### Targeted image cleanup

```bash
# Optional, only if no longer required:
docker image rm hello-world:latest
docker image rm nginx:alpine
```

Retain `devops-fastapi:1.0` if continuing the FastAPI labs. Removing a container does not automatically remove its image.

### Common prune commands

| Command | Effect |
|---|---|
| `docker container prune` | Removes stopped containers |
| `docker image prune` | Removes dangling images |
| `docker network prune` | Removes unused custom networks |
| `docker builder prune` | Removes unused build cache |
| `docker system prune` | Removes stopped containers, unused networks, dangling images and build cache |

**Warning:** Do not run `docker system prune -a --volumes` casually. It can remove resources and persistent data that you intend to keep.

### Local listening servers

```bash
lsof -nP -iTCP -sTCP:LISTEN
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

Common lab ports: 8000/8001 (FastAPI), 8080 (Nginx), 5432 (PostgreSQL), 3000 (frontend), 9090 (Prometheus). These are conventions, not proof of which service is running.

### Git branch cleanup

```bash
cd ~/devops-lab
git status
git branch -vv
git branch -r
git fetch origin --prune
git switch main
git pull --ff-only
git branch --merged main
```

Delete **only verified completed branches**:

```bash
git branch -d feature/<branch-name>
# Optional remote deletion, after confirming merged:
git push origin --delete feature/<branch-name>
```

`git fetch --prune` removes stale *remote-tracking references locally*; it does not delete branches on GitHub. Squash-merged branches may not appear as merged in local history even if their PRs were completed.

### Suggested read-only audit

```bash
cd ~/devops-lab
printf '\n=== Containers ===\n'; docker ps -a
printf '\n=== Images ===\n'; docker image ls
printf '\n=== Docker storage ===\n'; docker system df
printf '\n=== Volumes ===\n'; docker volume ls
printf '\n=== Git branches ===\n'; git branch -a
printf '\n=== Git status ===\n'; git status
printf '\n=== Listening ports ===\n'; lsof -nP -iTCP -sTCP:LISTEN
```

## 7. Recommended repository layout

This is a **target structure**, not a claim that every file already exists:

```text
devops-lab/
├── README.md
├── docs/
│   ├── DEVOPS_HOME_LAB_HANDBOOK.md
│   ├── troubleshooting.md
│   └── learning-log.md
├── 01-shell/
│   └── system-info.sh
├── 04-docker/
│   └── fastapi-demo/
│       ├── main.py
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .dockerignore
├── maintenance/
│   └── (future read-only environment audit script)
└── (future Kubernetes, Terraform and CI/CD modules)
```

## 8. Troubleshooting quick reference

| Symptom | Initial checks |
|---|---|
| `git push` fails through `origin`, explicit URL works | `git remote -v`, `git ls-remote origin`, remote URL configuration |
| GitHub SSH authentication fails | `ssh -T git@github.com`, key loaded and GitHub SSH key registered |
| Wrong Git executable selected | `which git`, `type -a git`, PATH in `~/.zshrc` |
| Docker CLI cannot connect to daemon | Start Docker Desktop; inspect `docker info` |
| Container exits immediately | `docker ps -a`, `docker logs <name>` |
| Port already allocated | `docker ps`, `lsof -nP -iTCP:<port> -sTCP:LISTEN` |
| Image build fails | Inspect Dockerfile, build context, dependency installation output |
| Local branch behind remote | `git fetch origin`, `git status`, `git pull --ff-only` on `main` |
| Merge conflict | `git status`, resolve markers, `git add`, complete merge commit |

## 9. Next steps

1. **Confirm Lab 06B execution:** Verify FastAPI image, both containers, `/health` response, and merged pull request.
2. **Run environment inventory:** Capture Docker containers, images, volumes, disk use, Git branches, and listening ports.
3. **Perform selective cleanup:** Keep resources needed for upcoming labs; remove confirmed disposable resources.
4. **Commit this handbook:** Store under `docs/DEVOPS_HOME_LAB_HANDBOOK.md` and link from `README.md`.
5. **Lab 06C:** Docker networking, volumes, PostgreSQL and application/database connectivity.
6. **Lab 06D:** Docker Compose for a multi-service environment.
7. **Lab 06E:** Container registry, tagging and basic security.
8. **Next phases:** Kubernetes, GitHub Actions CI/CD, Terraform, Ansible, monitoring and GitOps.

## 10. Documentation operating rules

- Update the handbook after each completed lab.
- Record **date, objective, commands, expected output, actual outcome, and issues resolved**.
- Keep secrets, tokens, `.env` files and private keys out of Git.
- Prefer small feature branches and reviewed pull requests.
- Keep cleanup read-only by default; make destructive operations explicit.
- Distinguish planned steps from verified completion.
- Record significant architectural decisions and why they were made.

### Lab entry template

```markdown
## Lab XX — Title
- Date:
- Objective:
- Branch:
- Prerequisites:
- Commands and files:
- Expected result:
- Actual result:
- Troubleshooting:
- Cleanup performed:
- Git commit / PR:
- Status: Confirmed / In progress / Pending
- Next action:
```

## 11. Reference links

- Git documentation: https://git-scm.com/doc
- GitHub documentation: https://docs.github.com/
- Docker getting started: https://docs.docker.com/get-started/
- Docker CLI reference: https://docs.docker.com/reference/cli/docker/
- FastAPI documentation: https://fastapi.tiangolo.com/
