# HangOver

**HangOver: AI-Powered Code Analysis for Git Repositories**  
This project, built with Django, provides an AI-powered platform for analyzing Git repositories (or specific branches/files within them). It leverages AI models to answer questions about the codebase.

---

## Features

- **Repository Integration:** Connect your GitHub repositories to analyze their codebase.  
- **Branch Selection:** Analyze specific branches within a repository.  
- **AI-Powered Analysis:** Ask questions about your code and receive AI-generated answers. Currently supports Gemini.  
- **File Selection:** Select specific files or folders for analysis to focus the AI's attention.  
- **User Authentication:** Secure user accounts to manage access to repositories.  
- **Result Persistence:** Store and retrieve previous analysis results.  
- **Clear UI:** Easy-to-use interface for managing repositories and viewing analysis results.  

---

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing.

### Prerequisites

- **Docker:** Make sure you have Docker and Docker Compose installed.  
- **Python 3.12:** This project requires Python 3.12. You can use a virtual environment or Docker (recommended).  
- **`.env.main` files:** The project uses environment variables. Refer to the `.env.example` file for required variables and create `.env.dev` and `.env.prod` files according to your needs.  
  - `GITHUB__TOKEN`: Your GitHub Personal Access Token (PAT). Generate one with appropriate permissions.  
  - `GEMINI__API_KEY`: Your Google Gemini API Key.  
  - `GEMINI__MODEL`: The name of the Gemini model you want to use.  
  - `DJANGO__SECRET_KEY`: A secret key for your Django project. Generate a strong random key.  
  - `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`: PostgreSQL database credentials.  

---

### Installation

1. **Clone the repository:**
   ```bash
       git clone <repository_url>
       cd hangover
   ```

2. **Create and fill the .env.main with your info**
3. **Change the .env.dev and .env.prod (if needed)**
4. **Run with Make**
    ```bash
      make run-prod
    ```
5. **Running the Application**
* Once the containers are running, the Django development server will be accessible at http://localhost:8000.

---
### Technologies Used

1) Python: Programming language
2) Django: Web framework
3) Celery: Distributed task queue
4) Redis: In-memory data structure store
5) PostgreSQL: Database
6) Docker & Docker Compose: Containerization
7) Google Gemini: AI model (you can replace this with other models as needed)
8) GitHub API: For repository access


### Project structure
```
hangover/
├── BaseApp/          # Django project
│   ├── ...
├── apps/             # Django applications
│   ├── Core/         # Core models and views
│   │   ├── ...
│   ├── Loginer/      # User authentication
│   │   ├── ...
│   └── Repository/   # Repository analysis logic
│       ├── ...
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── pyproject.toml
├── Makefile
├── .env.dev
├── .env.prod
├── .env.main
├── start.sh
└── requirements.txt
```
