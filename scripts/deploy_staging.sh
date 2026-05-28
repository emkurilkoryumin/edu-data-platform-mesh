#!/usr/bin/env sh
set -eu

: "${STAGE_HOST:?STAGE_HOST is required}"
: "${STAGE_USER:=ubuntu}"
: "${STAGE_PATH:=/opt/edu-gallery-platform}"

rsync -az --delete \
  --exclude ".git" \
  --exclude ".env" \
  --exclude ".terraform" \
  --exclude "node_modules" \
  ./ "$STAGE_USER@$STAGE_HOST:$STAGE_PATH/"

ssh "$STAGE_USER@$STAGE_HOST" "cd $STAGE_PATH && cp -n .env.example .env && docker compose pull || true && docker compose up -d --build"
