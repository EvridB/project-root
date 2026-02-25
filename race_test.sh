#!/bin/bash

URL_BASE="http://localhost:8000"
REQUEST_ID=9  # Заявка в статусе 'assigned', назначена на master1
COOKIE_FILE="/tmp/cookie_master1.txt"
RESULT1="/tmp/result1.txt"
RESULT2="/tmp/result2.txt"

# Логинимся как master1 один раз
echo "📝 Логинимся как master1..."
curl -s -c $COOKIE_FILE -X POST $URL_BASE/auth/login -H "Content-Type: application/json" -d '{"name":"master1"}' > /dev/null

# Проверим статус заявки
echo "📋 Проверяем заявку $REQUEST_ID..."
CURRENT_STATUS=$(curl -s -X GET $URL_BASE/requests/ -H "Cookie: user_id=1" | python3 -c "import sys, json; data = json.load(sys.stdin); req = next((r for r in data if r['id'] == $REQUEST_ID), None); print(req['status'] if req else 'not_found')")
echo "   Текущий статус: $CURRENT_STATUS"

if [[ "$CURRENT_STATUS" != "assigned" ]]; then
  echo "⚠️  Заявка не в статусе 'assigned', нужно установить её заново!"
  # Пытаемся переустановить
  echo "   Переводим заявку обратно в 'assigned'..."
  curl -s -X PATCH "$URL_BASE/requests/$REQUEST_ID/cancel" \
    -H "Cookie: user_id=1" > /dev/null 2>&1
  # Создаём новую заявку
  NEW_REQ=$(curl -s -X POST $URL_BASE/requests/ \
    -H "Cookie: user_id=1" \
    -H "Content-Type: application/json" \
    -d '{"clientName":"Гонка","phone":"+79001111111","address":"ул.Тестовая","problemText":"Гонка"}' | \
    python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
  curl -s -X PATCH "$URL_BASE/requests/$NEW_REQ/assign?master_id=2" \
    -H "Cookie: user_id=1" > /dev/null 2>&1
  REQUEST_ID=$NEW_REQ
  echo "   Новая заявка: $REQUEST_ID"
fi

# Функция запроса, сохраняет HTTP код в файл
do_request() {
  curl -s -w "%{http_code}" -b $COOKIE_FILE -X PATCH $URL_BASE/requests/$REQUEST_ID/take -o /dev/null > $1
}

echo "🏃 Запуск двух параллельных запросов от ОДНОГО мастера на захват заявки $REQUEST_ID..."
# Запускаем параллельно (оба от master1)
do_request $RESULT1 &
pid1=$!
do_request $RESULT2 &
pid2=$!
wait $pid1
wait $pid2

code1=$(cat $RESULT1)
code2=$(cat $RESULT2)
rm -f $RESULT1 $RESULT2

echo ""
echo "📊 Результаты:"
echo "   Запрос 1: HTTP $code1"
echo "   Запрос 2: HTTP $code2"
echo ""

# Ожидаем один 200, другой 409
if [[ "$code1" == "200" && "$code2" == "409" ]] || [[ "$code1" == "409" && "$code2" == "200" ]]; then
  echo "✅ Тест гонки ПРОЙДЕН!"
  echo "   ✓ Один запрос успешно захватил заявку (200)"
  echo "   ✓ Второй запрос получил конфликт, заявка уже взята (409)"
else
  echo "❌ Тест гонки НЕ ПРОЙДЕН"
  echo "   ✗ Ожидалось: одна 200 и одна 409"
  echo "   ✗ Получено: $code1 и $code2"
fi