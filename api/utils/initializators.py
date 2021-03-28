# Load encrypted config
from secrets_management.manage import (
    decrypt_credentials,
    load_credentials,
    get_environment,
)
import multiprocessing

multiprocessing.set_start_method("spawn", True)


def ptvsd_debugger_init(port=5678, wait_seconds=3):
    if get_environment() == "development":
        import ptvsd

        print("running in debug mode")
        try:
            ptvsd.enable_attach(address=("0.0.0.0", port))
            ptvsd.wait_for_attach(wait_seconds)
        except Exception:
            print(f"ptvsd attach on port {port} aborted")
            pass


def debugpy_init(port=5678):
    if get_environment() == "development":
        import debugpy

        print("running in debug mode")
        try:
            debugpy.listen(("0.0.0.0", port))
            debugpy.wait_for_client()
        except Exception:
            print(f"debugpy attach on port {port} aborted")


def process_init():
    print(f"[init] Starting process for environment `{get_environment()}`")
    load_credentials(decrypt_credentials(which=["*.env"]))
    print("[init] Initializing middlewares...")
