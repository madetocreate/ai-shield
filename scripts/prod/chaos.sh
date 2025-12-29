set -e
docker stop ai-shield-langfuse || true
sleep 2
curl -fsS "http://127.0.0.1:8080/health" | python3 -m json.tool
docker start ai-shield-langfuse || true
