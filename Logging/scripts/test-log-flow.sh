# scripts/test-log-flow.sh
#!/bin/bash

set -e

echo "🔁 Restarting containers..."
docker compose down
sleep 2
docker compose up -d --build

echo "📡 Waiting for Elasticsearch to be healthy..."
until curl -s http://localhost:9200/_cat/health | grep -q 'green\|yellow'; do
  echo "⏳ Waiting for Elasticsearch..."
  sleep 2
done

echo "🚀 Running test container that outputs logs..."
docker run --rm busybox sh -c "echo '🔥 Hello from test container'; sleep 1"

echo "⏱ Waiting for logs to be processed..."
sleep 5

echo "🔍 Querying Elasticsearch for test log..."
curl -s 'http://localhost:9200/container-logs/_search?q=log:Hello&pretty' | grep '🔥 Hello'

echo "✅ Test complete. If you see the log line above, the system is working correctly!"
