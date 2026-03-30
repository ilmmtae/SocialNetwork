# Django Social Engine

A robust backend for a social platform designed to manage user interactions, content distribution, and seamless integration with external services.

## 🌟 Key Features
* **Social Core:** Advanced data modeling for followers, friendship systems, and group interactions.
* **REST API:** Fully featured API built with **Django Rest Framework (DRF)**.
* **Service Integration:** Dedicated endpoints for user data synchronization with a FastAPI-based authentication microservice.
* **Admin Dashboard:** Custom Django Admin interface for efficient content moderation and user management.
* **Automated Documentation:** Real-time API specifications using **drf-spectacular** (OpenAPI 3.0).

## 🛠 Tech Stack
* **Framework:** Django & Django Rest Framework (DRF)
* **Database:** PostgreSQL
* **Task Queue:** Celery (for background tasks like email notifications)
* **API Documentation:** Swagger UI / Redoc
* **Environment Management:** Python-dotenv for secure configuration

## 🚀 Getting Started

1. Configure your `.env` file based on `.env.example`.
2. Run the services using Docker:
   ```bash
   docker-compose up --build