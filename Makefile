# =======================================================
# EduCatalog V3 — Makefile
# -------------------------------------------------------
# wrap คำสั่ง docker compose ให้พิมพ์สั้น + ใส่ --env-file อัตโนมัติ
# (กฎ A5 — config อยู่ที่ backend/.env เสมอ)
#
# วิธีใช้:
#   make up        → start ทุก service
#   make down      → stop ทุก service
#   make ps        → ดูสถานะ + healthcheck
#   make logs      → tail log ทุก service
#   make logs-backend → tail เฉพาะ backend
#   make clean     → ลบ container + volume (ล้างข้อมูล)
#   make rebuild   → build image ใหม่หมดและ start
# =======================================================


# -------------------------------------------------------
# ENV: ใช้ตัวเดียวกันทุกคำสั่ง — กันลืม flag
# -------------------------------------------------------
COMPOSE = docker compose --env-file ./backend/.env
PROJECT = educatalog_v3


# -------------------------------------------------------
# Lifecycle
# -------------------------------------------------------
.PHONY: up down restart stop start

up:           ## start ทุก service (build ถ้ายังไม่มี image)
	$(COMPOSE) up -d

down:         ## stop + ลบ container (volume ยังอยู่)
	$(COMPOSE) down

restart:      ## restart ทุก service
	$(COMPOSE) restart

stop:         ## stop ทุก service (container ยังอยู่)
	$(COMPOSE) stop

start:        ## start container ที่หยุดอยู่
	$(COMPOSE) start


# -------------------------------------------------------
# Build
# -------------------------------------------------------
.PHONY: build rebuild pull

build:        ## build image ที่ยังไม่ขึ้น
	$(COMPOSE) build

rebuild:      ## build image ใหม่หมด (ไม่ใช้ cache) แล้ว up
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d

pull:         ## pull image ทุกตัวจาก registry (postgres, redis, ฯลฯ)
	$(COMPOSE) pull


# -------------------------------------------------------
# Inspection
# -------------------------------------------------------
.PHONY: ps logs logs-backend logs-frontend logs-celery logs-db status

ps:           ## ดูสถานะ container + healthcheck
	$(COMPOSE) ps

status: ps    ## alias ของ ps

logs:         ## tail log ทุก service (Ctrl+C ออก)
	$(COMPOSE) logs -f --tail=100

logs-backend: ## tail log ของ backend
	$(COMPOSE) logs -f --tail=200 backend

logs-frontend: ## tail log ของ frontend
	$(COMPOSE) logs -f --tail=200 frontend

logs-celery:  ## tail log ของ celery_worker + celery_beat
	$(COMPOSE) logs -f --tail=200 celery_worker celery_beat

logs-db:      ## tail log ของ postgres
	$(COMPOSE) logs -f --tail=200 postgres


# -------------------------------------------------------
# Shell access
# -------------------------------------------------------
.PHONY: shell-backend shell-frontend shell-db shell-redis

shell-backend:  ## เข้า bash ใน backend container
	$(COMPOSE) exec backend bash

shell-frontend: ## เข้า sh ใน frontend container
	$(COMPOSE) exec frontend sh

shell-db:       ## เข้า psql ใน postgres (อ่าน user/db จาก .env)
	$(COMPOSE) exec postgres psql -U $$(grep ^POSTGRES_USER backend/.env | cut -d= -f2) -d $$(grep ^POSTGRES_DB backend/.env | cut -d= -f2)

shell-redis:    ## เข้า redis-cli (auth ผ่าน .env)
	$(COMPOSE) exec redis sh -c 'redis-cli -a $$REDIS_PASSWORD'


# -------------------------------------------------------
# Database (Alembic)
# -------------------------------------------------------
.PHONY: migrate migration-create migrate-down

migrate:           ## รัน migration ขึ้น head ล่าสุด
	$(COMPOSE) exec backend alembic upgrade head

migration-create:  ## สร้าง migration ใหม่จาก models (ใช้: make migration-create m="add users table")
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(m)"

migrate-down:      ## downgrade migration 1 step
	$(COMPOSE) exec backend alembic downgrade -1


# -------------------------------------------------------
# Testing (กฎ E)
# -------------------------------------------------------
.PHONY: test test-cov test-e2e

test:         ## รัน pytest ในcontainer backend
	$(COMPOSE) exec backend pytest -v

test-cov:     ## รัน pytest + coverage report (กฎ E2 ≥ 70%)
	$(COMPOSE) exec backend pytest --cov=. --cov-report=term-missing

test-e2e:     ## รัน Playwright E2E (กฎ E3)
	$(COMPOSE) exec frontend npm run test:e2e


# -------------------------------------------------------
# Clean-up
# -------------------------------------------------------
.PHONY: clean clean-all prune

clean:        ## ลบ container + volume (ล้างข้อมูล database/cache)
	$(COMPOSE) down -v

clean-all:    ## ลบ container + volume + image (เริ่มใหม่หมด)
	$(COMPOSE) down -v --rmi local

prune:        ## ล้าง docker cache ทั้งระบบ (ใช้เมื่อ disk เต็ม)
	docker system prune -af
	docker builder prune -af


# -------------------------------------------------------
# Validation
# -------------------------------------------------------
.PHONY: config validate

config:       ## render docker-compose.yml ที่ resolved แล้ว
	$(COMPOSE) config

validate:     ## ตรวจ syntax docker-compose.yml
	$(COMPOSE) config --quiet && echo "OK: docker-compose.yml is valid"


# -------------------------------------------------------
# Help (default target)
# -------------------------------------------------------
.PHONY: help
.DEFAULT_GOAL := help

help:         ## แสดงรายการคำสั่งทั้งหมด
	@echo "EduCatalog V3 — Available Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
