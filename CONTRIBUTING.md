# 🚀 Contributing to Orbit Simple Monitor (OSM)

Hey there! 🎉 Thanks for considering contributing to **OSM**. Whether you're fixing a bug, adding a feature, or improving documentation, your help is **super appreciated!** 💙

---

## **🌱 Git Workflow & Branching Best Practices**

To keep the repository **clean** and **organized**, we follow this **Git workflow**:

### **1️⃣ Fork & Clone**
If you’re an external contributor:
1. **Fork** this repository.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/orbitturner/osm.git
   cd osm
   ```
3. **Set the upstream** (only the first time):
   ```bash
   git remote add upstream https://github.com/orbitturner/osm.git
   ```

---

### **2️⃣ Branching Strategy**
We use a **feature-based branching strategy** to keep `main` stable.

#### **🌲 Main branches:**
- `main` → **Stable production branch** (only releases & hotfixes).
- `develop` → **Active development branch** (all new features/bugfixes go here).

#### **🌿 Feature & Fix branches:**
When working on a new feature or bugfix, create a branch based on `develop`:

```bash
git checkout develop
git pull origin develop  # Always ensure it's up-to-date
git checkout -b feature/cool-new-feature  # Naming: feature/your-feature-name
```

✅ **Branch Naming Convention**:
| Type            | Naming Format               | Example                     |
|----------------|----------------------------|-----------------------------|
| Feature        | `feature/<short-name>`      | `feature/slack-integration` |
| Bugfix         | `fix/<short-name>`          | `fix/email-auth-error`      |
| Hotfix (urgent fix on main) | `hotfix/<short-name>` | `hotfix/fix-critical-bug` |
| Release        | `release/<version>`         | `release/v1.2.0`            |

---

### **3️⃣ Commit Messages**
Use **clear, structured** commit messages following this format:

```bash
git commit -m "fix(email): Handle SMTP authentication issue"
```

✅ **Commit Message Format**:
```
<type>(<scope>): <short description>
```
| Type    | Description                      | Example                      |
|---------|----------------------------------|------------------------------|
| `feat`  | New feature                      | `feat(dashboard): Add CPU graph` |
| `fix`   | Bug fix                          | `fix(logging): Fix missing logs` |
| `chore` | Maintenance / minor updates      | `chore(deps): Update dependencies` |
| `docs`  | Documentation changes            | `docs(README): Update usage instructions` |
| `test`  | Adding/modifying tests           | `test(alerts): Add Slack alert tests` |
| `refactor` | Code improvement (no new feature) | `refactor(db): Optimize query performance` |

---

### **4️⃣ Push & Create a Pull Request**
1. **Push your branch**:
   ```bash
   git push origin feature/cool-new-feature
   ```
2. **Create a Pull Request (PR)** to `develop` on GitHub.
3. **Follow the PR template** and describe your changes.
4. A maintainer will review & merge your PR. 🎉

---

### **5️⃣ Keeping Your Fork Up-to-Date**
If you forked the repo, keep your local copy updated:

```bash
git checkout develop
git pull upstream develop
git push origin develop
```

---

## **✅ Contribution Guidelines**
Before submitting your PR:

✅ Ensure **your code follows the linting rules**.  
✅ Write **meaningful commit messages**.  
✅ Add **tests if applicable**.  
✅ Squash unnecessary commits (`git rebase -i`).  
✅ **Respect the Git workflow** (always branch from `develop`).  

---

## **🚀 Need Help?**
If you have any questions, **open an issue** or ping us on **[Discussions](https://github.com/orbitturner/osm/discussions)**! 💬

Happy coding! 🎉🚀  
— The **OSM Team** 🛰  
