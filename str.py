import json

hash = [
    {
        "error": "null",
        "result": {
            "as": 208120000000,
            "au": 174766666666.66666,
            "eu": 5179946666666.667,
            "sa": 245193333333.33334,
            "total": 7629893333333.334,
            "us": 1821866666666.6667
  }
}]

out = json.dumps(hash)


in1 = json.loads(out)
for s in in1:
    print(s)