from types import SimpleNamespace
import inspect

_callbacks = { 
    # even though the hook.Add function will automatically key:value and put it in here if it doesn't exist,
    # be nice to other developers and make sure you put it in here so they know it exists
    # thanks
    
    # bot hooks
    "on_bot_init": {},

    "on_create_game": {},
    "on_end_game": {},

    "on_run_pindle": {},
    "on_run_shenk": {},
    "on_run_trav": {},
    "on_run_nihlathak": {},
    "on_run_arcane": {},
    "on_run_diablo": {},
    "on_run_end": {},

    "on_pause": {},
    "on_resume": {},

    "on_item_keep": {},
    "on_run": {},
    "on_death": {},
    "on_chicken": {},
    "on_merc_death": {},
    "on_failed_run": {},

    "on_self_health_update": {},
    "on_merc_health_update": {},

    "bot_loop": {},


    # websockets / website hooks
    "recv_website_request": {},
}


def _add(callback_type, unique_identifier, callback):
    def cb(**kwargs):

        caller_kwargs = inspect.stack()[1][0].f_locals["kwargs"]
        callback_args = inspect.getfullargspec(callback).args

        new_kwargs = {}
        for arg in callback_args:
            if arg in caller_kwargs:
                new_kwargs[arg] = caller_kwargs[arg]
            else:
                new_kwargs[arg] = None
        return callback(**new_kwargs)

    if not _callbacks[callback_type]:
        _callbacks[callback_type] = {}
    _callbacks[callback_type][unique_identifier] = cb

def _remove(callback_type, unique_identifier):
    del _callbacks[callback_type][unique_identifier]

def _exists(callback_type, unique_identifier):
    return unique_identifier in _callbacks[callback_type]
    
def _call(callback_type, **kwargs):
    for callback in _callbacks[callback_type].values():
        callback(**kwargs)

hook = SimpleNamespace()
hook.Add = _add
hook.Remove = _remove
hook.Exists = _exists
hook.Call = _call
