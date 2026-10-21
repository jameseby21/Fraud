# Public code and local encrypted storage

The public repository contains application code, public evidence, and synthetic tests. Private vault files live outside every Git worktree. They are not part of the public dataset, web server, download routes, browser storage, or Git history. Ignore patterns are an accidental-inclusion precaution, not an access-control boundary.

## Vault format and key handling

The optional `vault.py` uses cryptography 50.0.2 with AES-256-GCM authenticated encryption. A fresh 16-byte salt and 12-byte nonce are generated for every write. The authenticated header fixes the format version, cipher, and Argon2id parameters. Unsupported or attacker-modified cost parameters are rejected before key derivation.

Argon2id derives a 32-byte key with three iterations, four lanes, and 64 MiB memory. Passphrases must be at least 16 characters; length alone does not establish strength. Use a long, unique passphrase stored separately in a password manager. Keys and passphrases are not stored beside ciphertext, accepted as CLI arguments, or written to logs. Unlock prompts require an interactive terminal.

See the library's [Argon2id documentation](https://cryptography.io/en/50.0.2/hazmat/primitives/key-derivation-functions/) and [authenticated-encryption documentation](https://cryptography.io/en/50.0.2/hazmat/primitives/aead/), and [OWASP cryptographic-storage guidance](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html).

## Storage boundary

Vault paths inside this repository or another detected Git worktree are rejected, including ignored directories such as `data/private`. The default location is an application-data directory outside the checkout. Symlink vault files are rejected. Keep the directory outside synchronized public folders and independently review its backup destination.

On Windows, the directory/file DACL is replaced with access for the current user and LocalSystem, with inheritance protected. On POSIX, directory and file modes are 0700 and 0600. Permission enforcement fails closed if unavailable. It does not resist an administrator taking ownership or code executing as the same user.

Updates use an exclusive lock, an expected-revision check, encrypted temporary bytes, fsync, and atomic replacement. Wrong-key and failed-replacement tests check that prior ciphertext is unchanged. A failed initialization removes its newly created placeholder without deleting an existing vault. A lock left after a crash must be investigated before manual removal; there is no automatic stale-lock bypass.

## Setup and use

The public dashboard remains dependency-free. The vault dependency is optional and hash-pinned:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-vault.txt
.\.venv\Scripts\python.exe vault.py init
.\.venv\Scripts\python.exe vault.py summary
.\.venv\Scripts\python.exe vault.py rotate
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Use `--path` only for an external `.fvault` file in a dedicated directory. The core checkpoint provides creation, a count/revision summary, and passphrase rotation. A higher-level record workflow can use the tested storage API; the browser server does not expose an unlock operation. Tests without the optional dependency explicitly skip vault tests, so they are not sufficient to verify storage changes.

Never use test passphrases for a real vault. There is no password recovery. Keep encrypted backups separately, check that they can be unlocked, and retain the appropriate passphrase. Rotation changes the current file's key; older backups still use their old keys. Atomic replacement reduces partial-write risk but is not a complete disaster-recovery strategy.

## Threat model and limits

This design addresses confidentiality of a locked stolen/copied vault, authenticated tamper detection, accidental storage in Git, and unintended access by other ordinary local accounts. It assumes a trusted operating system, trusted installed dependencies, and a trustworthy interactive terminal.

It does not protect against a compromised session, keylogger, administrator, malicious code running as the same user, or plaintext captured from memory, swap, crash dumps, screen recording, or explicit user exports. Python cannot promise reliable zeroization of every string or key copy. File names, sizes, timestamps, and access patterns remain observable. A previously valid encrypted snapshot can be rolled back; this format has no external anti-rollback authority.

This is not a multiuser service, certified cryptographic module, or independently audited vault product. Public source makes implementation review possible; it does not establish security by itself. Do not represent test results as a certification or endorsement.

## Public contribution boundary

Publish only public data and clearly synthetic fixtures. Do not commit private vaults, keys, private records, or personal context. Credentials require dedicated scanning and GitHub-side protection; [GitHub secret scanning](https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning) detects recognized credential types but cannot identify every sensitive statement. Review the actual staged diff before every push.
