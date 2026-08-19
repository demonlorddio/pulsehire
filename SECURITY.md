# 🔒 Security Guidelines — PulseHire

> **⚠️ You have $50 in credits. Protect your keys like cash.**

---

## 🛡️ The Golden Rule

**NEVER put API keys, passwords, or secrets in code that gets pushed to GitHub.**

Even a "private" repo can leak. Even a `.env` file that was added "for one minute." Once it's in git history, it's compromised forever.

---

## ✅ How PulseHire Handles Secrets

| File | Purpose | Committed to Git? |
|---|---|---|
| `.env` | Your **real** secrets | ❌ **NEVER** (in `.gitignore`) |
| `.env.example` | **Template** with placeholders | ✅ Yes (safe — no real keys) |
| `.gitignore` | Tells Git to ignore `.env` | ✅ Yes |

---

## 🚨 If You Accidentally Leak a Key

1. **Rotate it immediately** — go to Bright Data → Settings → Regenerate API Key
2. **Remove from git history** — `git filter-branch` or BFG Repo Cleaner
3. **Force push** — `git push --force` (only safe if you're the only collaborator)
4. **Check usage** — review your account for unexpected activity

---

## 📋 Pre-Push Checklist (run before every `git push`)

- [ ] `git status` — confirm `.env` is **not** in the list
- [ ] No hardcoded keys in `.py` or `.js` files
- [ ] No API keys in commit messages
- [ ] No screenshots with keys visible

### Quick check command:
```bash
git status
# If you see .env listed as "to be committed" — STOP. Run:
git rm --cached .env
```

---

## 🔐 What Counts as a Secret?

- ✅ API keys (Bright Data, OpenAI, etc.)
- ✅ Database passwords
- ✅ OAuth client secrets
- ✅ JWT signing keys
- ✅ Webhook signing secrets
- ❌ Public endpoints (e.g., `https://api.example.com/v1`)
- ❌ Your own project's URLs (no auth)

---

## 💡 Best Practices

1. **Use environment variables** — `os.environ.get("BRIGHTDATA_API_KEY")`
2. **Different keys for dev/prod** — never reuse production keys
3. **Rotate keys regularly** — every 90 days minimum
4. **Limit key permissions** — use scoped keys when possible
5. **Monitor usage** — set up alerts for unusual activity

---

## 📞 If Something Goes Wrong

If you suspect a key has been compromised:
1. Rotate it **now**
2. Document the incident (date, key, suspected cause)
3. Notify hackathon organizers if it affects shared infra
4. Update this file with lessons learned

---

**Stay safe. Your $50 depends on it. 💰**
