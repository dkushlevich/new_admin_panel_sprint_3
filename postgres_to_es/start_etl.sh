set -o errexit
set -o nounset


while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 0.1
done

python ./main.py
