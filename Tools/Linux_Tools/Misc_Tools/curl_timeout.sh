max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
  curl -m 10 https://reqbin.com/echo/get/json

  if [ $? -eq 0 ]; then
    echo "Request was successful"
    break
  else
    echo "Request failed with exit code $?. Retrying..."
    retry_count=$((retry_count + 1))
    sleep 2 # Wait for 2 seconds before retrying
  fi
done

if [ $retry_count -eq $max_retries ]; then
  echo "Request failed after $max_retries retries. Exiting."
fi