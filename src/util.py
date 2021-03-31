import logging
import sublime

def get_logger(package, name):
    plugin_logger = logging.getLogger(package)
    plugin_logger.propagate = False
    if not plugin_logger.handlers:
        plugin_logger_handler = logging.StreamHandler()
        plugin_logger_formatter = logging.Formatter("[{name}] {levelname}: {message}", style='{')
        plugin_logger_handler.setFormatter(plugin_logger_formatter)
        plugin_logger.addHandler(plugin_logger_handler)
    plugin_logger.setLevel(logging.WARNING)
    return logging.getLogger(name)


def merge_dictionaries(base, override, keys=None):
    '''Recursively merges the two given dictionaries. A new dictionary is returned.

    All elements of the "override" dictionary are superimposed onto the "base" dictionary,
    regardless if the same key exists on the base dictionary.

    If a list-like of keys is provided, only those keys from the override are 
    superimposed onto the base dictionary. All base dictionary keys are always returned.'''
    if keys is None:
        keys = override.keys()
    result = dict(base)
    for key in keys:
        o_val = override[key]
        if isinstance(o_val, dict) and key in base:
            result[key] = merge_dictionaries(result[key], o_val)
        else:
            result[key] = o_val
    return result


def get_merged_context_configs(context_key=None):
    settings = sublime.load_settings("tabnav.sublime-settings")
    configs = settings.get("contexts", {})
    user_configs = settings.get("user_contexts", {})
    if context_key is not None:
        if context_key not in user_configs:
            return configs
        else:
            context_keys = [context_key]
    else:
        context_keys = user_configs.keys()
    return merge_dictionaries(configs, user_configs)


def score_tabnav_selectors(view, point, selector, except_selector):
    '''Score's the given selector and except_selector at the given point to determine if the current point should be captured by the context.

    If selector is None, returns None.
    If selector is not None, and except_selector is None, returns the selector's score.
    If the selector's score is greater than the except_selector's score, returns the selector's score.
    If the except_selector's score is greater than the selector's score, returns -1, which
      indicates that these selectors had a match, but the point isn't in a table. (This is to avoid
      falling back to the auto_csv context.)
    '''
    if selector is None:
        return None
    score = view.score_selector(point, selector)
    if except_selector is None:
        return score
    except_score = view.score_selector(point, except_selector)
    if except_score > score:
        return -1
    return score


def point_from_region_func(cell_direction):
    if cell_direction > 0:
        return sublime.Region.end
    else:
        return sublime.Region.begin
