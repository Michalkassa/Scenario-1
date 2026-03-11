# Tech Stack

* Python
* Tkinter (GUI framework)
* Pygame / Playsound (audio playback)
* Requests (weather API integration)
* Matplotlib (hydration graphs)
* uv (Python package manager)

---
        
# Installing uv

MindfulDesk uses **uv** to manage dependencies and run the project.

### macOS / Linux

```
curl -Ls https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)

```
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:

```
uv --version
```

---

# Running the Project

Clone the repository and move into the project folder:

```
git clone <repository-url>

```

Create a virtual environment:

```
uv venv
```

Install dependencies:

```
uv sync
```

Add dependencies:

```
uv add <dependency>
```

Run the application:

```
uv run python main.py
```
