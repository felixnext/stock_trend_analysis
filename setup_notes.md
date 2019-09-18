# System Setup Notes

## Virtual Environment Setup

This is just a small note for the setup process to integrate a virtual environment as kernel into the global jupyter installation.

1. Create the virtual environment: `virtualenv datascience`
2. Activate the environment and install everything required (e.g. `pip install -r requirements.txt`)
3. Install kernel lib: `pip install ipykernel`
4. Link kernel to global installation: `ipython kernel install --user --name=ds-stocks`
