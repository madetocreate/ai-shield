set -e
curl -fsS "http://127.0.0.1:8080/health" | python3 -m json.tool
curl -fsS "https://127.0.0.1:8443/health" -k | python3 -m json.tool
curl -fsS "http://127.0.0.1:3000/api/public/health" | python3 -m json.tool || true
curl -fsS "http://127.0.0.1:3000/api/public/ready?failIfDatabaseUnavailable=true" | python3 -m json.tool || true
