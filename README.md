## Running the Project with Docker

This project is containerized using Docker and Docker Compose for easy setup and deployment. Below are the instructions and details specific to this project:

### Project-Specific Docker Details
- **Python Version:** 3.11 (as specified in the Dockerfile: `python:3.11-slim`)
- **Dependencies:** All Python dependencies are listed in `requirements.txt` and installed into a virtual environment during the build process.
- **Entrypoint:** The application is started using Gunicorn with the command: `gunicorn wsgi:app --bind 0.0.0.0:5000`
- **User:** The container runs as a non-root user (`appuser`) for improved security.

### Environment Variables
- **No required environment variables** are specified in the Dockerfile or docker-compose.yml. If you need to add any, uncomment and use the `env_file` section in the compose file.

### Ports
- **Exposed Port:** The application is exposed on port **5000** (container) and mapped to port **5000** on the host.

### Build and Run Instructions
1. **Build and start the application:**
   ```sh
   docker compose up --build
   ```
   This will build the Docker image and start the service as defined in `docker-compose.yml`.

2. **Access the application:**
   - The app will be available at [http://localhost:5000](http://localhost:5000)

### Special Configuration
- No external services (databases, caches, etc.) are required or configured.
- No persistent volumes or custom networks are needed for this setup.
- If you need to add environment variables, create a `.env` file and uncomment the `env_file` line in `docker-compose.yml`.

---

_These instructions are specific to this project's Docker setup. For any additional configuration, refer to the project source files or update the Docker Compose file as needed._
