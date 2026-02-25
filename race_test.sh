#!/bin/bash

URL="http://localhost:8000/requests/2/take"
COOKIE_FILE1="/tmp/cookie_master1.txt"
COOKIE_FILE2="/tmp/cookie_master2.txt"
RESULT1="/tmp/result1.txt"
RESULT2="/tmp/result2.txt"

# Логинимся как master1 и master2
echo "Logging in as master1..."
curl -s -c $COOKIE_FILE1 -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"name":"master1"}' > /dev/null
echo "Logging in as master2..."
curl -s -c $COOKIE_FILE2 -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"name":"master2"}' > /dev/null

# Функция запроса, сохраняет HTTP код в файл
do_request() {
  curl -s -w "%{http_code}" -b $1 -X PATCH $URL -o /dev/null > $2
}

echo "Запуск конкурентных запросов..."
# Запускаем параллельно
do_request $COOKIE_FILE1 $RESULT1 &
pid1=$!
do_request $COOKIE_FILE2 $RESULT2 &
pid2=$!
wait $pid1
wait $pid2

code1=$(cat $RESULT1)
code2=$(cat $RESULT2)
rm -f $RESULT1 $RESULT2

echo "Код ответа 1: $code1"
echo "Код ответа 2: $code2"

# Ожидаем один 200, другой 409
if [[ "$code1" == "200" && "$code2" == "409" ]] || [[ "$code1" == "409" && "$code2" == "200" ]]; then
  echo "✅ Тест гонки пройден"
else
  echo "❌ Тест гонки не пройден (коды: $code1, $code2)"
fi