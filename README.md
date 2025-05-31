# Prerequisites

python >= 3.10

# Install circus

```bash
pip install circus
```

# Activate venv

```bash
python -m venv venv
```

```bash
source venv/bin/activate
```

# Install deps

```bash
pip install -r requirements.txt
```

# Run circus

```bash
circusd --daemon circus.ini
```

# Check all jobs with circus

```bash
circusctl status
```

