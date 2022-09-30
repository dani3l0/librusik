import os, base64
print(base64.urlsafe_b64encode(os.urandom(32)).decode())