set -e
IN="$1"
if [ -z "$IN" ]; then echo "usage: restore.sh /path/to/backupdir"; exit 1; fi
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.override.ai-shield.yml -f docker-compose.override.langfuse-v3.yml -f docker-compose.override.pin.yml -f docker-compose.override.prod-hardening.yml -f docker-compose.override.tls.yml down
cat "$IN/postgres_litellm.sql" | docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.override.ai-shield.yml -f docker-compose.override.langfuse-v3.yml -f docker-compose.override.pin.yml -f docker-compose.override.prod-hardening.yml -f docker-compose.override.tls.yml up -d postgres
sleep 3
cat "$IN/postgres_litellm.sql" | docker exec -i ai-shield-postgres psql -U litellm -d litellm
cat "$IN/postgres_langfuse.sql" | docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.override.ai-shield.yml -f docker-compose.override.langfuse-v3.yml -f docker-compose.override.pin.yml -f docker-compose.override.prod-hardening.yml -f docker-compose.override.tls.yml up -d postgres-langfuse
sleep 3
cat "$IN/postgres_langfuse.sql" | docker exec -i ai-shield-postgres-langfuse psql -U langfuse -d langfuse
docker run --rm -v ai-shield_langfuse_clickhouse_data:/data -v "$IN":/backup alpine:3.21 sh -lc "rm -rf /data/* && tar -xzf /backup/clickhouse_data.tgz -C /data"
docker run --rm -v ai-shield_langfuse_minio_data:/data -v "$IN":/backup alpine:3.21 sh -lc "rm -rf /data/* && tar -xzf /backup/minio_data.tgz -C /data"
rm -rf "$HOME/ai-shield/apps/control-plane/data"
mkdir -p "$HOME/ai-shield/apps/control-plane/data"
tar -xzf "$IN/control_plane_data.tgz" -C "$HOME/ai-shield/apps/control-plane"
docker compose -f docker-compose.yml -f docker-compose.override.yml -f docker-compose.override.ai-shield.yml -f docker-compose.override.langfuse-v3.yml -f docker-compose.override.pin.yml -f docker-compose.override.prod-hardening.yml -f docker-compose.override.tls.yml up -d --build
