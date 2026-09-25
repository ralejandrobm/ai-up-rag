# 🚢 Deploy with Dokploy

This guide deploys AI UP RAG on a server managed by [Dokploy](https://dokploy.com). Dokploy builds the image from this repository, runs the containers with `setup/docker-compose.dokploy.yml`, and publishes the domains with HTTPS through its own Traefik proxy and Let's Encrypt.

| Compose file | Used for | Domains and HTTPS |
|--------------|----------|-------------------|
| `setup/docker-compose.yml` | Local development (`make dev`) | None |
| `setup/docker-compose.server.yml` + `setup/docker-compose.proxy.yml` | Server with nginx-proxy (`make proxy` + `make prod`), see [deploy-aws.md](deploy-aws.md) | nginx-proxy + Let's Encrypt |
| `setup/docker-compose.dokploy.yml` | Dokploy (this guide) | Configured in the Dokploy UI (Traefik) |

Differences between the Dokploy compose and the other two:

- It does not publish ports and it has no `VIRTUAL_HOST`/`LETSENCRYPT_*` variables. The domains are configured in Dokploy.
- It does not set `container_name`. Dokploy names the containers.
- `odoo.conf` is not read from the repository. It is mounted from `../../files/odoo.conf`, a file you create in Dokploy (step 4).
- The volumes have their own names (`odoo-ai-bot-up-*`), so they don't collide with the local volumes.
- The database has a healthcheck (`pg_isready`).

> **Placeholders:** this guide uses `odoo.example.com`, `pgadmin.example.com` and `admin@example.com`. Replace them with your own domains and email.

## 1. Prepare the server

You need a Linux server (Ubuntu 24.04 recommended) with:

- **RAM:** 16 GiB recommended, 8 GiB minimum. The Odoo container reserves 4 GiB and can use up to 8 GiB, because it loads PyTorch and the embeddings model.
- **Disk:** 30 GiB or more.
- **Open ports:** `22` (SSH), `80` and `443` (Traefik), and `3000` (Dokploy panel, only while you configure it; you can close it later if you assign a domain to the panel).

If you use AWS, follow steps 1 and 2 of [deploy-aws.md](deploy-aws.md) to create the EC2 instance, the Elastic IP and the DNS records, and add port `3000` to the security group.

Install Dokploy (this also installs Docker):

```bash
curl -sSL https://dokploy.com/install.sh | sh
```

Open `http://<SERVER_IP>:3000` and create the administrator account.

Do not run nginx-proxy (`make proxy`) on the same server. Dokploy's Traefik already uses ports 80 and 443.

## 2. Configure the DNS

Create two `A` records pointing to the server IP:

| Type | Name | Value |
|------|------|-------|
| A | `odoo.example.com` | `<SERVER_IP>` |
| A | `pgadmin.example.com` | `<SERVER_IP>` |

If you use Cloudflare, keep the proxy **disabled** (gray cloud) until the certificates are issued.

## 3. Create the Compose service

1. In Dokploy, create a **Project** (for example `ai-up`).
2. Inside the project, click **Create Service** > **Compose**, and choose the type **Docker Compose** (not *Stack*: Docker Swarm stacks do not support `build`).
3. In the **General** tab, configure the source:
   - **Provider:** GitHub (or Git, with the repository URL).
   - **Repository** and **Branch:** this repository and `main`.
   - **Compose Path:** `./setup/docker-compose.dokploy.yml`
4. Save.

## 4. Create the `odoo.conf` file

The compose mounts `odoo.conf` from the Dokploy files folder, outside the repository. Dokploy clones the repository into `code/` and keeps the file mounts in `files/`, so the path `../../files/odoo.conf` (relative to `code/setup/`) points to that file.

Go to the **Advanced** tab > **Mounts** > **Add Mount**, choose **File Mount**, and set:

- **File path:** `odoo.conf`
- **Content:** based on `setup/config/example.odoo.conf`, with a strong `admin_passwd`:

```ini
[options]
addons_path =  /mnt/custom-addons,/mnt/third-party-addons
data_dir = /var/lib/odoo
admin_passwd = CHANGE_ME_STRONG_PASSWORD
limit_time_cpu = 5000
proxy_mode = 1
limit_time_real = 12000
db_maxconn=1000

# Sin límite de memoria por worker (0 = sin límite)
limit_memory_hard = 0
limit_memory_soft = 0
```

Keep `proxy_mode = 1`. Odoo needs it to work correctly behind Traefik.

## 5. Configure the environment variables

In the **Environment** tab, paste the content of `setup/.example.env` with your values. Dokploy writes these variables to the `.env` file that the compose reads with `env_file: .env`.

```env
# PGADMIN
PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=CHANGE_ME

# POSTGRESS
POSTGRES_DB=postgres
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_USER=odoo

# odoo
HOST=ai_up_odoo_db
USER=odoo
PASSWORD=CHANGE_ME

# AI Models
SAFETENSORS_FAST_GPU=0
OPENAI_API_KEY=your_api_key_here

# HuggingFace
HF_HUB_DISABLE_XET=1
```

`POSTGRES_PASSWORD` and `PASSWORD` must have the same value. `HOST` must stay as `ai_up_odoo_db`, the name of the database service.

## 6. Configure the domains

In the **Domains** tab, add one domain per public service:

| Service | Host | Path | Container Port | HTTPS | Certificate |
|---------|------|------|----------------|-------|-------------|
| `ai_up_odoo` | `odoo.example.com` | `/` | `8069` | On | Let's Encrypt |
| `pgadmin` | `pgadmin.example.com` | `/` | `80` | On | Let's Encrypt |

The **Container Port** is the port inside the container, not a port of the server. Do not add a domain for `ai_up_odoo_db`: the database must only be reachable inside the compose network.

## 7. Deploy

Click **Deploy**. Follow the progress in the **Deployments** tab. The first build takes several minutes because it downloads PyTorch.

When it finishes, open the **Logs** tab, select the `ai_up_odoo` service, and wait until you see `HTTP service (werkzeug) running`. Then open https://odoo.example.com.

If you use Cloudflare, you can re-enable its proxy (orange cloud) once the site loads with HTTPS.

## 8. Configure Odoo

Follow steps 2 to 7 of the **Configuration** section in the [README](../README.md), using `https://odoo.example.com` instead of `http://localhost:8069`:

1. Create the database, using the `admin_passwd` from the `odoo.conf` of step 4 as the **Master Password**.
2. Activate Developer Mode.
3. Update the Apps list and activate the `ai_up` modules in order: AI UP Vectorizer, AI UP Vectorizer Pg Vector, AI UP Advertisements, AI UP Advertisements Vectorizer, AI up Message History, AI UP Messaging.
4. Check the **Advertisement pgvector** provider.
5. Create interested parties and advertisements. The first advertisement takes several minutes because the embeddings model is downloaded. Follow it in the **Logs** tab.

## 9. Test the API

```bash
curl -X POST https://odoo.example.com/api/v1/whatsapp/answers \
  -H "Content-Type: application/json" \
  -d '{"from_phone": "3310222500", "message": "cual es la estrategia de la universidad panamericana"}'
```

## 10. Query the database with pgAdmin

Open https://pgadmin.example.com and log in with `PGADMIN_DEFAULT_EMAIL` and `PGADMIN_DEFAULT_PASSWORD`. Register the server with **Host name/address** `ai_up_odoo_db`, port `5432`, and the `POSTGRES_USER` / `POSTGRES_PASSWORD` from the environment variables. See the **Querying Data** section of the [README](../README.md) for example queries.

## 11. Update the application

- **Manually:** click **Deploy** again. Dokploy pulls the branch, rebuilds the image and recreates the containers.
- **Automatically:** enable **Autodeploy** in the **General** tab (GitHub provider), or copy the webhook URL from the **Deployments** tab to your repository, so every push to `main` deploys.

If the changes modify an Odoo add-on, upgrade the module afterwards: **Apps** > search the module > **Upgrade**.

The data is stored in the `odoo-ai-bot-up-*` volumes, so it is kept between deployments. Do not delete the volumes from Dokploy unless you want to lose the database.

The `make` commands of the repository (`make dev`, `make prod`, etc.) are not used with Dokploy. Everything is managed from the Dokploy panel.

## 🧯 Troubleshooting

| Problem | Cause and solution |
|---------|--------------------|
| **`odoo.conf` not found, or Odoo starts with the default configuration** | The file mount is missing or has a different name. Check that step 4 created `odoo.conf`, and redeploy. |
| **Odoo cannot connect to the database** | Check `HOST`, `USER` and `PASSWORD` in the Environment tab, and check that `PASSWORD` matches `POSTGRES_PASSWORD`. |
| **404 or the domain does not respond** | Check the domain in the Domains tab: correct service and **Container Port** (`8069` for Odoo, `80` for pgAdmin). Redeploy after changing domains. |
| **The certificate is not issued** | Check that the DNS points to the server, that ports 80 and 443 are open, and that the Cloudflare proxy is disabled. |
| **The build fails or Odoo restarts when saving an advertisement** | The server does not have enough memory. Use a server with more RAM (see step 1). |
