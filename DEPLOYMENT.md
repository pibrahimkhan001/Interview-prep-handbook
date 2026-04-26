# Deployment guide

How to push this site to GitHub and serve it on GitHub Pages so you can read it online from any device.

**Target repo:** `https://github.com/pibrahimkhan001/interview-prep-handbook`
**Site URL after deploy:** `https://pibrahimkhan001.github.io/interview-prep-handbook/`

---

## One-time setup

You only need to do these once on each machine where you'll push from.

### 1. Install Git

If `git --version` works in your terminal, skip ahead. Otherwise:

- **Windows:** download Git for Windows from https://git-scm.com/download/win and run the installer (defaults are fine).
- **macOS:** `brew install git` or install Xcode Command Line Tools.
- **Linux:** `sudo apt install git` (Debian/Ubuntu) or your distro's equivalent.

### 2. Configure your git identity

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

Use the email associated with your GitHub account so commits show up under your profile.

### 3. Set up GitHub authentication

GitHub no longer accepts passwords for git operations. Pick one:

**Option A — Personal Access Token (simplest)**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it something like "Local laptop"
4. Set expiration (90 days is reasonable; you'll regenerate later)
5. Tick the **`repo`** scope (top checkbox under "Select scopes")
6. Click "Generate token" at the bottom
7. **Copy the token immediately** — you won't see it again
8. When git asks for a password during `git push`, paste the token instead of your GitHub password

Windows tip: install Git Credential Manager (bundled with Git for Windows) and it'll cache the token so you only paste it once.

**Option B — SSH keys**
See https://docs.github.com/en/authentication/connecting-to-github-with-ssh — slightly more setup but no token expiration.

---

## Pushing this project to GitHub

Run these commands once, in the project folder, on your local machine.

### Step 1 — Extract the zip and open a terminal in the folder

Extract `interview-prep-guide.zip` somewhere convenient (e.g., `C:\Projects\interview-prep-guide`).

Open Terminal/PowerShell/Git Bash and `cd` into that folder:

```bash
cd C:\Projects\interview-prep-guide
```

### Step 2 — Initialize git and commit

```bash
git init
git branch -M main
git add .
git commit -m "Initial commit: interview prep handbook (28 chapters, ~57% complete)"
```

### Step 3 — Connect to your GitHub repo

```bash
git remote add origin https://github.com/pibrahimkhan001/interview-prep-handbook.git
```

If your repo already has files (like a default README), pull them first to merge:

```bash
git pull origin main --allow-unrelated-histories
```

If a merge conflict comes up on the README, just keep your local one (open the file, remove the `<<<<<<<` markers) and:

```bash
git add README.md
git commit -m "Merge remote README"
```

### Step 4 — Push

```bash
git push -u origin main
```

If prompted for credentials, your username is `pibrahimkhan001` and the password is your **Personal Access Token** from Option A above.

You should see "everything up-to-date" or a list of files being uploaded. Visit `https://github.com/pibrahimkhan001/interview-prep-handbook` to confirm the files are there.

---

## Enabling GitHub Pages

This makes your site readable in a browser at `https://pibrahimkhan001.github.io/interview-prep-handbook/`.

1. Go to your repo on GitHub: `https://github.com/pibrahimkhan001/interview-prep-handbook`
2. Click **Settings** (top right of the repo page)
3. In the left sidebar, click **Pages**
4. Under "Build and deployment":
   - **Source:** "Deploy from a branch"
   - **Branch:** `main` and `/ (root)`
5. Click **Save**
6. Wait 1-2 minutes; a banner will appear at the top of the Pages settings showing your live URL

Your site is now live at `https://pibrahimkhan001.github.io/interview-prep-handbook/` and accessible from any device, including your phone.

---

## Pushing future updates

After Claude generates more content (React, Databases, etc.) and you re-extract a fresh zip, you have two options:

### Option A — Replace and push (simpler)

```bash
cd C:\Projects\interview-prep-guide

# Copy the new files over the old ones (Windows; use 'rsync' on macOS/Linux)
xcopy /E /Y "C:\path\to\new\interview-prep-guide\*" .

# Add and commit
git add .
git commit -m "Add ReactJS chapters (Phase 4 complete)"
git push
```

### Option B — Pull, edit, push (if you make local changes)

If you make changes locally and want to keep them, work directly in your local folder. Just `git add`, `git commit`, `git push` after each change set.

---

## Common issues

**"refusing to merge unrelated histories"**
You created the GitHub repo with a README/license, and your local repo has different files. Run:
```bash
git pull origin main --allow-unrelated-histories
```

**"Permission denied (publickey)" on push**
You're using SSH but no key is set up. Either set up SSH keys or switch to HTTPS:
```bash
git remote set-url origin https://github.com/pibrahimkhan001/interview-prep-handbook.git
```

**Site is live but CSS isn't loading**
Hard refresh (Ctrl+Shift+R / Cmd+Shift+R). If it's still broken, open browser DevTools (F12) → Network tab and check whether `assets/styles.css` returns 200. If it's 404, the path is wrong somewhere.

**404 on chapter pages**
Make sure the `chapters/` folder was committed: `git ls-files chapters/ | head`. If empty, something excluded it. Check `.gitignore` doesn't include `chapters/`.

**Pages says "Your site is published" but shows 404**
GitHub Pages takes 1-2 minutes to build the first time. Wait, then hard-refresh.

---

## Optional: custom domain

If you own a domain (e.g., `prep.ibrahim.dev`), you can point it at this site:

1. Add a `CNAME` file at the project root containing just your domain (e.g., `prep.ibrahim.dev`)
2. In your DNS provider, add a CNAME record pointing your subdomain to `pibrahimkhan001.github.io`
3. In repo Settings → Pages, enter your custom domain and tick "Enforce HTTPS"

DNS takes up to 24h to propagate; HTTPS provisioning takes another few minutes after that.
