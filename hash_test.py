import hashlib

api_key = "kpe_TestKey123456789012345678901234"
key_hash = hashlib.sha256(api_key.encode()).hexdigest()
print(f"API Key: {api_key}")
print(f"Hash: {key_hash}")
