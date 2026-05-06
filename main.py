import sys
import os
import importlib.util

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
NDA_DIR     = os.path.join(BASE_DIR, 'nda')
ONLINEID_DIR = os.path.join(BASE_DIR, 'onlineid')


def _load_module(reg_name, filepath):
    spec = importlib.util.spec_from_file_location(reg_name, filepath)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[reg_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _evict_generic_modules(prefix):
    """Rename any generic module names (models, utils, config…) to a prefixed
    version so the next app gets fresh copies when it imports them."""
    ROOTS = ('models', 'routes', 'services', 'utils', 'config')
    for _k in list(sys.modules.keys()):
        if _k in ROOTS or any(_k.startswith(r + '.') for r in ROOTS):
            sys.modules[prefix + _k] = sys.modules.pop(_k)


# ── 1. Load NDA app FIRST ────────────────────────────────────────────────
sys.path.insert(0, NDA_DIR)
_nda_mod = _load_module('_nda_application', os.path.join(NDA_DIR, 'app.py'))
nda_app  = _nda_mod.app
_evict_generic_modules('_nda_')
if NDA_DIR in sys.path:
    sys.path.remove(NDA_DIR)

# ── 2. Load Online ID Validator app ──────────────────────────────────────
sys.path.insert(0, ONLINEID_DIR)
_onlineid_mod = _load_module('_onlineid_application', os.path.join(ONLINEID_DIR, 'app.py'))
onlineid_app  = _onlineid_mod.app
_evict_generic_modules('_onlineid_')
if ONLINEID_DIR in sys.path:
    sys.path.remove(ONLINEID_DIR)

# ── 3. Load the Proposal Builder (root) app normally ─────────────────────
sys.path.insert(0, BASE_DIR)
from app import app as proposal_app  # noqa: E402

# ── 4. Mount all apps under a single server ───────────────────────────────
#   /           → Proposal Builder
#   /nda        → NDA Generator AI
#   /onlineid   → Online ID Validator
from werkzeug.middleware.dispatcher import DispatcherMiddleware  # noqa: E402
from werkzeug.serving import run_simple                          # noqa: E402

application = DispatcherMiddleware(proposal_app, {
    '/nda':      nda_app,
    '/onlineid': onlineid_app,
})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    run_simple('0.0.0.0', port, application, use_reloader=False, use_debugger=False)
