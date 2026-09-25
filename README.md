# ai-up-rag

A Retrieval-Augmented Generation (RAG) architecture using Odoo as the backend and OpenAI as the LLM for Universidad Panamericana.

# 🚀 AI UP RAG

## 📌 Instructions to run the microservices stack locally (Ubuntu)

## 🎆 Setup

0. If you are working on Windows, we recommend using WSL.
1. Install Docker and ensure it is running properly. You can use Docker Desktop.
2. Clone this repository and update the prompt in the file `odoo/custom-addons/ai_up_messaging/models/open_ai_llm.py`.

This prompt is used to define the personality of the LLM when answering chat queries.

3. Duplicate the file `.env.example` in the `setup` folder and rename it to `.env`.

4. Add your OpenAI API key to the `.env` file:

```bash
OPENAI_API_KEY=your_api_key_here
```

5. Duplicate the file `example.odoo.conf` in the `setup/config` folder and rename it to `odoo.conf`.

6. Install `make`. All the commands to start, stop and inspect the stack are defined in the `Makefile`.

```bash
sudo apt-get update
sudo apt-get install make
```

   Check that it was installed correctly:

```bash
make --version
```

## ⚙️ Configuration

1. From the root of the repository, start the containers:

```bash
make dev
```

   This command builds the Odoo image (based on `odoo:18.0` plus the Python dependencies in `setup/requirements.txt` and a CPU-only version of PyTorch) and starts three containers:

   | Container | Description | URL |
   |-----------|-------------|-----|
   | `ai_up_odoo` | Odoo 18 with the custom add-ons | http://localhost:8069 |
   | `ai_up_odoo_db` | PostgreSQL 17 with the `pgvector` extension | internal only |
   | `ai_up_odoo_pgadmin` | pgAdmin, to query the database | http://localhost:5050 |

   The first build can take several minutes because it downloads PyTorch. `make dev` runs in the foreground and shows the logs; keep that terminal open and use a new one for the next commands. To stop the stack press `Ctrl+C`.

   Other useful commands:

   | Command | Description |
   |---------|-------------|
   | `make dev-logs` | Show the latest container logs |
   | `make dev-restart` | Restart only the Odoo container (use it after changing Python code in the add-ons) |

2. Open http://localhost:8069/ in your browser. The first time, Odoo shows the database creation form. Fill it in as follows:

   - **Master Password**: the value of `admin_passwd` in `setup/config/odoo.conf` (`12345678` by default).
   - **Database Name**: any name, for example `ai_up`.
   - **Email** and **Password**: the credentials of the Odoo administrator user. You will use them to log in.
   - **Language**: `English (US)`.
   - **Country**: `Mexico`.
   - Leave **Demo data** unchecked.

   Click **Create database** and wait until Odoo finishes (it can take a minute). Then log in with the email and password you just defined.

   ![odoo inicio](docs/odooConfDatos.png)

   ![odoo login](docs/odooLogin.png)

   ![odoo home](docs/odooInicio.png)

3. Activate Developer Mode. The custom add-ons are not visible in the Apps catalog until Developer Mode is enabled.

   Go to **Settings**, scroll to the bottom of the page and click **Activate the developer mode**. The page reloads and a bug icon appears in the top bar.

   ![odoo aps](docs/odooIrSettings.png)

   ![odoo dev](docs/odooDeveloperMode.png)

4. Install the custom add-ons.

   4.1 Go to **Apps** and click **Update Apps List** in the top menu, then confirm with **Update**. This makes Odoo read the add-ons mounted from `odoo/custom-addons`.

   ![odoo install1](docs/odooIrApps.png)
   ![odoo install2](docs/odooUpdateAppsList.png)

   4.2 In the search bar, remove the default **Apps** filter (click the `x` on the filter). The custom modules are not marked as applications, so they are hidden while that filter is active.

   ![odoo install3](docs/odooRemoveFilterApps.png)

   4.3 Search for `ai_up`. The six AI UP modules should appear.

   ![odoo install4](docs/odooSearchAi_Up.png)

   4.4 Click **Activate** on each module, **one at a time and in this order**. Some modules depend on others, so the order matters:

   | # | Module | What it does |
   |---|--------|--------------|
   | 1 | AI UP Vectorizer | Base module that defines vectorizer providers and the logic to keep embeddings in sync |
   | 2 | AI UP Vectorizer Pg Vector | Adds the `pgvector` provider (HuggingFace embeddings stored in PostgreSQL) |
   | 3 | AI UP Advertisements | Adds advertisements and interested parties, the knowledge base of the chatbot |
   | 4 | AI UP Advertisements Vectorizer | Generates embeddings every time an advertisement is created, edited or deleted |
   | 5 | AI up Message History | Stores the conversation history of each user |
   | 6 | AI UP Messaging | Exposes the API and generates the answers with OpenAI |

   ![odoo install5](docs/OdooInstallModuls.png)

5. Check the vectorizer provider. Go to the **AI UP Vectorizer** menu and open **Providers**. When module 4 is installed it creates the provider **Advertisement pgvector** automatically. Open it and check that:

   - **Code** is `PG Vector`.
   - **Use Same DB for pg_vector** is checked, so the vectors are stored in the same database as Odoo.

   The advertisements are linked to this provider through its slug `advertisement-pg-vector`. Do not change or delete the slug, or advertisements will stop being vectorized.

   ![odoo vec1](docs/odooIrAiVectorizer.png)
   ![odoo vec2](docs/odooSelectVectorizer.png)

6. Create interested parties. Every advertisement needs at least one interested party (the audience it is meant for, for example `Students` or `Teachers`).

   Go to **AI UP Advertisement** > **Configuration** > **Interested Parties**, click **New**, type a name and save.

   ![odoo IT1](docs/odooIrAdvertisement.png)
   ![odoo IT2](docs/odooCreateIterestedParties.png)

   ![odoo IT3](docs/odooSaveInterestedParties.png)

7. Create an advertisement. Advertisements are the documents the chatbot uses to answer questions.

   Go to **AI UP Advertisement** > **Advertisements** and click **New**. Fill in:

   - **Title**: a short title.
   - **Description**: the full content. This is the text the chatbot will search in, so be clear and detailed.
   - **Interested Parties**: select at least one.

   When you save, the advertisement is converted into an embedding and stored in `pgvector`. **The first time you save an advertisement it can take several minutes**, because the embeddings model (`sentence-transformers/all-mpnet-base-v2`) is downloaded from HuggingFace. The model is cached in a Docker volume, so later saves are fast. You can follow the download with `make dev-logs`.

   ![odoo adv1](docs/odooIrAdvertisement.png)

   ![odoo adv2](docs/odooNewAdvertisement.png)

   ![odoo adv3](docs/odooSaveAdvertisement.png)

   ![odoo adv4](docs/odooAdvertisementCreated.png)

8. Query the RAG system. Send a `POST` request to http://localhost:8069/api/v1/whatsapp/answers with a JSON body containing:

   - `from_phone`: the user's phone number. It identifies the conversation, so requests with the same number share history.
   - `message`: the user's question.

```json
{
  "from_phone": "3310222500",
  "message": "cual es la estrategia de la universidad panamericana"
}
```

   You can use Postman or `curl`:

```bash
curl -X POST http://localhost:8069/api/v1/whatsapp/answers \
  -H "Content-Type: application/json" \
  -d '{"from_phone": "3310222500", "message": "cual es la estrategia de la universidad panamericana"}'
```

   The response contains the generated answer:

```json
{
  "status": 200,
  "data": ["..."]
}
```

   If the body is invalid (for example, `message` is missing), the API returns status `400` with the validation errors.

  ![postma](docs/postman.png)

## 🔍 Querying Data

1. Open pgAdmin at http://localhost:5050/ and log in with `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD` from `setup/.env`.

   ![pgadmin1](docs/pgadminLogin.png)

2. Register the database server. Right-click **Servers** > **Register** > **Server...**:

   - **General** tab > **Name**: any name, for example `ai-up`.
   - **Connection** tab:
     - **Host name/address**: `ai_up_odoo_db` (the name of the database container, not `localhost`).
     - **Port**: `5432`.
     - **Username**: the value of `POSTGRES_USER` in `setup/.env`.
     - **Password**: the value of `POSTGRES_PASSWORD` in `setup/.env`.

   Click **Save**.

   ![pgadmin2](docs/pgadminAddServer.png)
   ![pgadmin2](docs/pgadminServerData1.png)
   ![pgadmin2](docs/pgadminServerData2.png)

3. Query the data. Expand the server, select the database you created in Odoo, and open **Tools** > **Query Tool**.

   The conversations are stored in the `mail_message` table:

```sql
SELECT id, create_date, email_from, author_id, body
FROM mail_message
WHERE model = 'ai_up.message.history'
ORDER BY id DESC;
```

   Messages with `author_id = 1` are answers from the chatbot. The rest are messages from users.

   The embeddings are stored in the `langchain_pg_embedding` table, grouped by collection in `langchain_pg_collection`.

   ![pgadmin2](docs/pgadminSQL.png)

## ☁️ Server deployment

There are two ways to deploy on a server with HTTPS:

- **nginx-proxy + Let's Encrypt** on a virtual machine (AWS EC2): see [docs/deploy-aws.md](docs/deploy-aws.md).
- **Dokploy**: see [docs/deploy-dokploy.md](docs/deploy-dokploy.md).
