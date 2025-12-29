set -e
TS="$(date +"%Y-%m-%d__%H%M%S")"
BASE="$HOME/Dokumente/Backups"
if [ ! -d "$HOME/Dokumente" ] && [ -d "$HOME/Documents" ]; then BASE="$HOME/Documents/Backups"; fi
OUT="$BASE/ai-shield/runtime/$TS"
mkdir -p "$OUT"
docker exec -i ai-shield-postgres pg_dump -U litellm -d litellm > "$OUT/postgres_litellm.sql"
docker exec -i ai-shield-postgres-langfuse pg_dump -U langfuse -d langfuse > "$OUT/postgres_langfuse.sql"
docker run --rm -v ai-shield_langfuse_clickhouse_data:/data -v "$OUT":/backup alpine:3.21 tar -czf /backup/clickhouse_data.tgz -C /data .
docker run --rm -v ai-shield_langfuse_minio_data:/data -v "$OUT":/backup alpine:3.21 tar -czf /backup/minio_data.tgz -C /data .
tar -czf "$OUT/control_plane_data.tgz" -C "$HOME/ai-shield/apps/control-plane" data
echo "$OUT"
