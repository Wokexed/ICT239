import secrets
import uuid

print(uuid.uuid4().hex)
print(secrets.token_hex(16))