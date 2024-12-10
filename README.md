# Invoice Creator Web Application

## Description
This is a simple web application to create and manage invoices. It allows users to:
- Create new invoices with company and customer details.
- Upload a logo for the company.
- View and download invoices.

## Requirements
- Python 3.9+
- Flask
- SQLite

## Setup Instructions

1. Clone the repository:
git clone https://github.com/your-repo/invoice-creator.git cd invoice-creator

2. Install the dependencies:
pip install -r requirements.txt

3. Run the application:
python app/main.py



4. The app will be accessible at `http://127.0.0.1:5000`.

## Docker Setup
To run the application in a Docker container:

1. Build the Docker image:
docker build -t invoice-creator .

2. Run the Docker container:
docker run -p 5000:5000 invoice-creator


docker network create invoice-network
docker run -d --name app --network invoice-network -p 5000:5000 invoice-creator

docker run -d --name app --network invoice-network -p 5000:5000 -v $(pwd)/data:/app/data invoice-creator



The application will be available at `http://localhost:5000`.
