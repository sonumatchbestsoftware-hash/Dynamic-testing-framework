**Setup (Windows PowerShell)**

- **Purpose**: Steps to install Python, create a virtual environment, and install project dependencies.

- **Quick automated script** (recommended if you have `winget`):

  - Open PowerShell as Administrator.
  - Run:

    ```powershell
    powershell -ExecutionPolicy Bypass -File .\setup_env.ps1
    ```

- **Manual steps**:

  - Install Python 3.8+ from https://www.python.org/downloads/
  - Open PowerShell in project root and run:

    ```powershell
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

- **Run tests**:

  ```powershell
  python run_tests.py
  ```

If you run into permission issues when activating scripts, you can temporarily allow running local scripts in PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Revert with:

```powershell
Set-ExecutionPolicy -ExecutionPolicy Restricted -Scope CurrentUser
```