# 🚀 How to develop on local

## 🎆 Setup

1. Install docker.
2. Install Make to use Makefiles commands.
3. Duplicate the file `.env.example`, in `setup` folder, and rename it to `.env`.
4. Duplicate the file `example.odoo.conf`, in `setup/config` folder, and rename it to `odoo.conf`.
5. Run `make dev` to start the containers.
6. Create a new database, with language `en_US` and timezone `America/Mexico_City`.
7. Enjoy!

## 🧹 Clean environment

1. Run `make clean` to stop and remove the containers.
2. To remove the volumes (database, cache), remove the folder `setup/_data`.
