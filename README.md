# ai-up-rag

RAG architecture using Odoo as the backend for Universidad Panamericana

# 🚀 AI UP RAG

## 📌 Instructions to run the microservices stack locally (Ubuntu)

## 🎆 Setup

0. If you are working on Windows, we recommend using WSL.
1. Install Docker and ensure it is running properly. You can use Docker Desktop.
2. Clone this repository.
3. Duplicate the file `.env.example` in the `setup` folder and rename it to `.env`.
4. Duplicate the file `example.odoo.conf` in the `setup/config` folder and rename it to `odoo.conf`.
5. Install `make`:

```bash
sudo apt-get update
sudo apt-get install make
```

6. Run the following command to build the necessary Docker images:

```bash
make build
```

## 🌴 Test

1. Run the following command to start the containers:

```bash
make dev
```
2. Access the application at http://localhost:8000/

