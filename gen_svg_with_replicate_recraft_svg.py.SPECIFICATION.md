Make python3 script that is generating provided `n` amount of generations,
generated files basename is by default as specified


* -n default 1
* -S|--sleep default default 0
* -t|--token by default uses environment variable " `$REPLICATE_API_TOKEN` "
* -v|--verbose | inform about progress to stderr, more -v more verbose , e.g. -vvvv
* if there is filename conflict it will look for smallest number that appended to basename is available filename e.g. for 'foo.svg' may find 'foo14.svg' as first available one
* And parameter is Prompt provided by user

How to use API 

```
curl -s -X POST \               
  -H "Authorization: Bearer $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Prefer: wait" \
  -d $'{
    "input": {
      "size": "1024x1024",
      "style": "any",
      "prompt": "Prompt provided by user"
    }
  }' \
  https://api.replicate.com/v1/models/recraft-ai/recraft-v3-svg/predictions
```

As we see example output contains URL were image is provided for download:

```
{"id":"predictionID","model":"recraft-ai/recraft-v3-svg","version":"dp-e085e5b4bcf8789583ccc10b8d61a486","input":{"prompt":"Prompt provided by user","size":"1024x1024","style":"any"},"logs":"","output":"https://replicate.delivery/czjl/jsleirjsieljjfldkE9scseTA/tmpiot8_mdk.svg","data_removed":false,"error":null,"status":"processing","created_at":"2024-12-21T08:30:53.869Z","urls":{"cancel":"https://api.replicate.com/v1/predictions/predictionID/cancel","get":"https://api.replicate.com/v1/predictions/predictionID","stream":"https://stream.replicate.com/v1/files/fddq-qk88e2yzudcgh2o2carijnuonsnjszttxyxuzvyxsl5qibvbga2nq"}}
```
