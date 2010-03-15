import sys
import pickle
import inspect
import traceback

_current_frame = None

_watched_expr = None
_watched_locals = None
_watched_globals = None

_value_id = None
_value_dump = None

def watch(expr):
    global _watched_expr, _watched_locals, _watched_globals
    frame = sys._getframe(1)
    _watched_expr = expr
    _watched_locals = frame.f_locals
    _watched_globals = frame.f_globals
    _record()
    sys.settrace(_instrument)

def _record():
    global _value_id, _value_dump
    try:
        obj = eval(_watched_expr, _watched_locals, _watched_globals)
        _value_id = id(obj)
        _value_dump = pickle.dumps(obj) # XXX: We need a better mechanism
    except NameError:
        _value_id = None
        _value_dump = None

def _instrument(frame, event, arg):
    global _current_frame
    old_value_id = _value_id
    old_value_dump = _value_dump
    #traceback.print_stack(frame)
    _record()
    if old_value_id is None and _value_id is None:
        pass
    elif old_value_id is None and _value_id is not None:
        print "Initialized by:"
        traceback.print_stack(_current_frame)
    else:
        id_eq = old_value_id == _value_id
        dump_eq = old_value_dump == _value_dump
        if id_eq and dump_eq:
            pass
        elif id_eq and not dump_eq:
            print "Mutated by:"
            traceback.print_stack(_current_frame)
        elif not id_eq and dump_eq:
            print "Replaced with equivalent object by:"
            traceback.print_stack(_current_frame)
        else:
            print "Replaced by:"
            traceback.print_stack(_current_frame)
    _current_frame = frame
    return _instrument
