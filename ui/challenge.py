import hashlib, base64, os

# this would be dodgy if it was going to be longlived, but we want a single ephemeral
# secret for the duration of the script run
secret = os.urandom(32)

# auth0 has feelings about websafe base64, so need to hand implement
def magicb64(x):
    return base64.b64encode(x).replace(b'+', b'-').replace(b'/', b'_').replace(b'=', b'')

def generate():
    verifier = magicb64(secret)
    hasher = hashlib.sha256()
    hasher.update(verifier)
    challenge = magicb64(hasher.digest())
    return {"verifier": verifier, "challenge": challenge}

