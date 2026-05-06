import sys
import os
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NDA_DIR  = os.path.join(BASE_DIR, 'nda')

# ── 1. Load NDA app FIRST so its "models", "routes", "services" imports
#       don't conflict with the root app's identically-named modules.
sys.path.insert(0, NDA_DIR)

def _load_module(reg_name, filepath):
    spec = importlib.util.spec_from_file_location(reg_name, filepath)
    mod  = importlib.util.module_from_spec(spec)
    sys.modules[reg_name] = mod
    spec.loader.exec_module(mod)
    return mod

_nda_mod = _load_module('_nda_application', os.path.join(NDA_DIR, 'app.py'))
nda_app  = _nda_mod.app

# ── 2. Move NDA-loaded modules out of the generic cache so the root app
#       gets its own fresh copies when it imports "models", "routes", etc.
_ROOTS = ('models', 'routes', 'services')
for _k in list(sys.modules.keys()):
    if _k in _ROOTS or any(_k.startswith(r + '.') for r in _ROOTS):
        sys.modules['_nda_' + _k] = sys.modules.pop(_k)

if NDA_DIR in sys.path:
    sys.path.remove(NDA_DIR)

# ── 3. Now load the Proposal Builder (root) app normally.
sys.path.insert(0, BASE_DIR)
from app import app as proposal_app  # noqa: E402

# ── 4. Mount: /nda → NDA Generator AI, everything else → Proposal Builder.
#       Werkzeug sets SCRIPT_NAME="/nda" on each NDA request, so Flask's
#       url_for() inside the NDA app automatically produces /nda/... URLs.
from werkzeug.middleware.dispatcher import DispatcherMiddleware  # noqa: E402
from werkzeug.serving import run_simple                          # noqa: E402

application = DispatcherMiddleware(proposal_app, {'/nda': nda_app})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    run_simple('0.0.0.0', port, application, use_reloader=False, use_debugger=False)
