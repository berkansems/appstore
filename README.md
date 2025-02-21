This project is a web application built using Django and Django Rest Framework (DRF). It provides functionality for managing apps and orders, with a focus on verifying apps before they can be purchased.

### Features:
- **App Management**: Allows users to manage apps with verification statuses.
- **Order Management**: Users can create and manage orders for verified apps.
- **Swagger API Docs**: Integrated Swagger UI to view and interact with the API.
- **CI/CD**: GitHub Actions set up for Continuous Integration and Continuous Deployment.

## Requirements

Before getting started, make sure you have the following installed:
- Docker
- Docker Compose

## Setup and Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/berkansems/appstore.git

2. **Build and Run with Docker Compose**

   ```bash
   docker-compose up --build


3. **Access the API Documentation**

   ```bash
   http://localhost/api/docs/

4. **Run tests**

   ```bash
   docker-compose run --rm appstore sh -c "python manage.py test"

## CI/CD with GitHub Actions
The project uses GitHub Actions for Continuous Integration and Deployment (CI/CD). Upon pushing to the repository, the CI/CD pipeline is triggered, which includes the following steps:
- Running tests
- Building Docker images
- Running linting using **flake8** to check for coding style violations

You can view the GitHub Actions logs in the **Actions** tab of the repository.


