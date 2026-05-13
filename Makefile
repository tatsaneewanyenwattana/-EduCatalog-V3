# EduCatalog V3 — Makefile ที่ root เพื่อคำสั่งซ้ำๆ เหมือนกันทุกเครื่อง (ไม่ผูกกับ IDE)
# Windows: GNU Make (เช่น winget install ezwinports.make) + PowerShell — `make help` และดึง REDIS_PASSWORD ใช้ scripts/*.ps1
# ระวัง: target ที่ใช้ `if [` (เช่น migration, push) ต้องมี sh/bash ใน PATH หรือตั้ง SHELL เป็น Git Bash — ไม่ใช่ cmd

.DEFAULT_GOAL := help

# ดึงรหัส Redis จาก backend/.env เพราะ redis-cli บน host ต้องส่ง -a เอง Make ไม่อ่าน .env ให้
ifeq ($(OS),Windows_NT)
REDIS_PASSWORD := $(shell powershell -NoProfile -ExecutionPolicy Bypass -File "$(CURDIR)/scripts/read-redis-password-from-env.ps1")
else
REDIS_PASSWORD := $(shell grep -E '^REDIS_PASSWORD=' backend/.env 2>/dev/null | cut -d '=' -f2- | tr -d '\015')
endif

# -------------------------------------------------------
# Docker — lifecycle ของ stack (docker-compose.yml อยู่ที่ root)
# -------------------------------------------------------
up: ## Docker: ขึ้นทุก service โหมด detached (-d)
	@echo "[Docker] กำลัง docker compose up -d ..."
	@docker compose up -d

down: ## Docker: หยุดและลบ container (volume เก็บตามที่ compose กำหนด)
	@echo "[Docker] กำลัง docker compose down ..."
	@docker compose down

restart: ## Docker: restart ทุก service พร้อมกัน — เร็วกว่า down+up เมื่อแค่อยากโหลด config ภายใน
	@echo "[Docker] กำลัง docker compose restart ..."
	@docker compose restart

build: ## Docker: build image ตาม Dockerfile ใน compose (ยังไม่สั่ง down)
	@echo "[Docker] กำลัง docker compose build ..."
	@docker compose build

rebuild: ## Docker: down + build ไม่ใช้ cache + up — ใช้เมื่อแก้ Dockerfile แล้วต้องชั้นเก่าหลุด
	@echo "[Docker] rebuild --no-cache แล้ว up -d ..."
	@docker compose down && docker compose build --no-cache && docker compose up -d

logs: ## Docker: ติดตาม log ทุก service (foreground)
	@echo "[Docker] เปิด compose logs -f (Ctrl+C ออก)"
	@docker compose logs -f

ps: ## Docker: สถานะ container + healthy (ตรวจเร็วก่อน migrate/seed)
	@echo "[Docker] docker compose ps"
	@docker compose ps

# -------------------------------------------------------
# Database — Alembic จาก container backend (WORKDIR /app = backend/)
# -------------------------------------------------------
migrate: ## DB: เลื่อน migration ไปหัว head — deploy ครั้งใหม่ควรเรียกหลัง image ใหม่ขึ้น
	@echo "[DB] alembic upgrade head ภายใน container backend ..."
	@docker compose exec backend alembic upgrade head

rollback: ## DB: ถอย migration หนึ่งรุ่น — ระวังข้อมูลเมื่อ downgrade มี drop column
	@echo "[DB] alembic downgrade -1 ..."
	@docker compose exec backend alembic downgrade -1

migration: ## DB: สร้างไฟล์ revision จากโมเดล (ต้องใส่ MSG=คำอธิบาย) เช่น make migration MSG="add x"
	@if [ -z "$(MSG)" ]; then echo "กำหนด MSG=... เช่น make migration MSG=add_users_table"; exit 1; fi
	@echo "[DB] alembic revision --autogenerate -m \"$(MSG)\" ..."
	@docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

history: ## DB: ดูลำดับ revision — ตรงกับทีมก่อน rollback
	@echo "[DB] alembic history"
	@docker compose exec backend alembic history

db: ## DB: เข้า psql แบบโต้ตอบ — ใช้สำรวจตารางหลัง seed (ออกด้วย \q)
	@echo "[DB] เข้า psql — user/db educatalog (ออกจาก psql พิมพ์ \\q)"
	@docker compose exec postgres psql -U educatalog -d educatalog

# -------------------------------------------------------
# Seed — master ทุก ENV; mock เฉพาะ development (สคริปต์บล็อกเอง)
# -------------------------------------------------------
seed: ## Seed: หมวด + feature_flags + admin (รันได้ prod)
	@echo "[Seed] seed_master.py ใน container backend ..."
	@docker compose exec backend python scripts/seed_master.py

seed-mock: ## Seed: mock agencies/users/datasets — หยุดเองถ้า ENV ไม่ใช่ development
	@echo "[Seed] seed_mock.py (development เท่านั้น) ..."
	@docker compose exec backend python scripts/seed_mock.py

seed-all: ## Seed: รัน master แล้วต่อด้วย mock — ควรเรียงลำดับให้มีหมวดก่อน dataset
	@echo "[Seed] make seed แล้ว make seed-mock ..."
	@$(MAKE) seed && $(MAKE) seed-mock

# -------------------------------------------------------
# Backend — เครื่องมือคุณภาพใน container (ถ้ามีใน image)
# -------------------------------------------------------
test: ## Backend: pytest พร้อม coverage — CI ควรเหมือนคำสั่งนี้
	@echo "[Backend] pytest -v พร้อม cov ..."
	@docker compose exec backend pytest -v --cov=. --cov-report=term-missing

test-fast: ## Backend: pytest หยุดรอบแรกที่ fail (-x) สำหรับวนไว้ใน dev
	@echo "[Backend] pytest -v -x ..."
	@docker compose exec backend pytest -v -x

lint: ## Backend: ruff check — ต้องมี ruff ใน environment ของ backend (ถ้ายังไม่มีให้เพิ่มใน requirements)
	@echo "[Backend] ruff check . ..."
	@docker compose exec backend ruff check .

format: ## Backend: black formatter — พฤติกรรมเดียวกันกับผู้เขียนคนถัดไป
	@echo "[Backend] black . ..."
	@docker compose exec backend black .

# -------------------------------------------------------
# Frontend — npm จาก container frontend
# -------------------------------------------------------
fe-install: ## Frontend: npm install เมื่อเปลี่ยน package.json
	@echo "[Frontend] npm install ใน container ..."
	@docker compose exec frontend npm install

fe-test: ## Frontend: npm run test — ใน package.json ชี้ไป typecheck จนกว่าจะมี unit test จริง
	@echo "[Frontend] npm run test ..."
	@docker compose exec frontend npm run test

e2e: ## Frontend: Playwright E2E — ควรให้ backend+frontend พร้อมก่อน
	@echo "[Frontend] Playwright tests ..."
	@docker compose exec frontend npx playwright test

# -------------------------------------------------------
# Redis — ต้องส่งรหัสตรงกับ backend/.env (ตัวแปร REDIS_PASSWORD จาก grep ด้านบน)
# -------------------------------------------------------
redis: ## Redis: เข้า redis-cli (ออกด้วย exit) — พาสจาก backend/.env
	@echo "[Redis] redis-cli พร้อม -a (**ห้ามถ่าย log พาสใน production**) ..."
	@docker compose exec redis redis-cli -a "$(REDIS_PASSWORD)"

flush: ## Redis: FLUSHALL — ห้ามในข้อมูลจริงโดยไม่ backup; เคลียร์ cache dev
	@echo "[Redis] FLUSHALL (ล้างทุก DB ที่ instance นี้) ..."
	@docker compose exec redis redis-cli -a "$(REDIS_PASSWORD)" FLUSHALL

# -------------------------------------------------------
# Logs แยก service — จำกัด tail 50 บรรทัดเพื่อไม่เทอร์มินัลล้น
# -------------------------------------------------------
log-backend: ## Log: ตาม backend (Ctrl+C ออก)
	@echo "[Log] backend -f tail=50"
	@docker compose logs backend -f --tail=50

log-frontend: ## Log: ตาม frontend
	@echo "[Log] frontend -f tail=50"
	@docker compose logs frontend -f --tail=50

log-worker: ## Log: ตาม celery_worker
	@echo "[Log] celery_worker -f tail=50"
	@docker compose logs celery_worker -f --tail=50

log-db: ## Log: ตาม postgres
	@echo "[Log] postgres -f tail=50"
	@docker compose logs postgres -f --tail=50

# -------------------------------------------------------
# Ngrok — ให้ควบคุมจากเครื่องโฮสต์ (ต้องลง ngrok และ auth แล้ว; port ตรงกับ nginx compose)
# -------------------------------------------------------
ngrok: ## Ngrok: เปิด HTTPS ชั่วคราวไป port 80 ที่ nginx proxy (เหมือนนโยบายใน .cursorrules)
	@echo "[Ngrok] ngrok http 80 — อย่ายิงเข้าฐานข้อมูล production และปิดเมื่อเลิก demo"
	@ngrok http 80

# -------------------------------------------------------
# Git — ครอบเป็น make เพื่อกันพิมพ์ยาวผิด (ต้องกำหนด MSG=ข้อความ commit)
# -------------------------------------------------------
push: ## Git: add . + commit + push main (ระบุ MSG="ข้อความ") — ควรอยู่บน branch ที่ตั้งใจ merge
	@if [ -z "$(MSG)" ]; then echo "กำหนด MSG เช่น make push MSG=\"fix typo\""; exit 1; fi
	@echo "[Git] git add . && commit \"$(MSG)\" && push origin main ..."
	git add .
	git commit -m "$(MSG)"
	git push origin main

help: ## แสดงคำสั่งทั้งหมดพร้อมคำอธิบายภาษาไทย (จาก ## ในแต่ละเป้าหมาย)
	@echo ""
	@echo "EduCatalog V3 — เรียกจาก root ของ repo (ไฟล์นี้อยู่ข้าง docker-compose.yml)"
	@echo "--- Docker ---"
	@echo "  up down restart build rebuild logs ps"
	@echo "--- Database ---"
	@echo "  migrate rollback migration history db  |  migration ต้อง: make migration MSG=คำอธิบาย"
	@echo "--- Seed ---"
	@echo "  seed seed-mock seed-all"
	@echo "--- Backend ---"
	@echo "  test test-fast lint format"
	@echo "--- Frontend ---"
	@echo "  fe-install fe-test e2e"
	@echo "--- Redis ---"
	@echo "  redis flush  — REDIS_PASSWORD อ่านจาก backend/.env ตอนประกาศใน Makefile"
	@echo "--- Logs ---"
	@echo "  log-backend log-frontend log-worker log-db"
	@echo "--- Ngrok ---"
	@echo "  ngrok"
	@echo "--- Git ---"
	@echo "  push MSG=ข้อความ_commit"
	@echo ""
	@echo "--- เป้าหมาย + คำอธิบาย (อ่านจาก ## ใน Makefile) ---"
ifneq ($(OS),Windows_NT)
	@awk '/^[a-zA-Z0-9_.-]+:.*## / { line=$$0; sub(/^[^:]+:[^#]*## */, "", line); t=$$0; sub(/:.*$$/, "", t); gsub(/^ +| +$$/, "", t); printf "  %-16s — %s\n", t, line }' Makefile
else
	@powershell -NoProfile -ExecutionPolicy Bypass -File "$(CURDIR)/scripts/make-help.ps1"
endif

# เชื่อมทุกเป้าหมายให้เป็น phony เพื่อไม่ชนไฟล์ชื่อชุดคำสั่งกับของจริงในโฟลเดอร์
.PHONY: up down restart build rebuild logs ps migrate rollback migration history db seed seed-mock seed-all test test-fast lint format fe-install fe-test e2e redis flush log-backend log-frontend log-worker log-db ngrok push help
