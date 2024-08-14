import logging
import yaml
from pathlib import Path
from yaml.loader import SafeLoader

_logger = logging.getLogger(__name__)

def contains_key(path_arr, current_dict):
    """
    checks if the nested dict contains the key (use dots as separator)
    """
    key = path_arr.pop(0)
    if not key in current_dict:
        return False

    sub = current_dict[key]

    return contains_key(path_arr, sub)

def get_dict_path(path, current_dict, default_value = None):
    """
    get a value in the nested dict using a path (use dots as separator)
    """
    path_arr = path.split('.')
    return _get_from_nested_dict(path_arr, current_dict, default_value)

def set_dict_path(current_dict, path, value):
    """
    set a value in the nested dict using a path (use dots as separator)
    """
    path_arr = path.split('.')
    return _set_from_nested_dict(path_arr, current_dict, value)

def _get_from_nested_dict(path_arr, current_dict, default_value):
    """
    get a value in a nested dict using a path array (array of keys)
    """
    key = path_arr.pop(0)
    if not key in current_dict:
        return default_value

    sub = current_dict[key]

    if len (path_arr) == 0:
        return sub

    return _get_from_nested_dict(path_arr, sub, default_value)


def _set_from_nested_dict(path_arr, current_dict, value):
    """
    set a value to a nested dict using a path array (array of keys)
    """
    key = path_arr.pop(0)

    if len (path_arr) == 0:
        current_dict[key] = value
        return

    if not key in current_dict:
        newdict = {}
        current_dict[key] = newdict
        _set_from_nested_dict(path_arr, newdict, value)
    else:
        _set_from_nested_dict(path_arr,  current_dict[key], value)

def get_leaf_nodes(nested_dict):
    """ find all the leaves from a nested dict. return an array of tuples (path (string array), value)"""
    leafs = []
    path = []
    _collect_leaf_nodes(nested_dict, path, leafs)

    new_list = []

    for leaf in leafs:
        new_list.append(('.'.join(leaf[0]), leaf[1]))

    return new_list

def _collect_leaf_nodes(node, path, leafs):
    """ collect all leaves, recursively """
    if node is not None:
        if isinstance(node, dict):
            for key in node.keys():
                child_node = node[key]
                sub_path = path.copy()
                sub_path.append(key)
                _collect_leaf_nodes(child_node, sub_path, leafs)
        else:
            leafs.append((path, node))

class NestedDict:
    """ a nested dictonnary with tools to yaml load/save, access with adresses using dot as separator ex : services.ssp.hostname """
    def __init__(self, dictionnary = None):
        self.dict = dictionnary
        if self.dict is None:
            self.dict = {}


    def get_value(self, path: str, default_value = None):
        """
        get a value from teh nested dict. returns default_value if not found
        """
        path_arr = path.split('.')
        return _get_from_nested_dict(path_arr, self.dict, default_value)


    def has_key(self, adress: str) -> bool:
        """
        check if the key exists, return a boolean
        """
        path_arr = adress.split('.')
        return contains_key(path_arr, self.dict)


    # set a value at the adress.
    # if already exists it is overloaded
    def set_value(self, adress : str, value):
        """
        set a value at the adress.
        if already exists it is overloaded
        """

        path_arr = adress.split('.')
        _set_from_nested_dict(path_arr, self.dict, value)


    def add_value(self, adress, value, unique = False):
        """
        search an array at the adress and append the value
        if the array does not exists it is created
        if it is not an array an exceptio is raised

        if unique is True, checks if the value if not already in the list
        """
        arr = self.get_value(adress, [])

        if not isinstance(arr, list):
            raise Exception(adress + ' is not an array ! ')

        if unique:
            for old_value in arr:
                if old_value == value:
                    return

        arr.append(value)
        self.set_value(adress, arr)

    def load(self, yaml_path):
        """
        load nested dict from yaml
        """
        with open(yaml_path, 'r', encoding='UTF-8') as stream:
            self.dict = yaml.load(stream, Loader=yaml.SafeLoader)
            if self.dict is None:
                self.dict = {}

    def overload_values(self, yaml_path):
        """
        overload each value with the one found in the yaml
        """

        if self.dict is None:
            self.dict = {}

        if not Path(yaml_path).is_file():
            _logger.warning(f"{yaml_path} not found")
            return False

        with open(yaml_path, 'r', encoding='UTF-8') as stream:
            overload_dict = yaml.load(stream, Loader=SafeLoader)

        leaf_nodes = get_leaf_nodes(overload_dict)
        for leaf in leaf_nodes:
            set_dict_path(self.dict, leaf[0], leaf[1])

        return True

    def save(self, yaml_path):
        """
        save nested dict to yaml
        """
        with open(yaml_path, 'w', encoding='UTF-8') as stream:
            yaml.dump(self.dict, stream=stream, sort_keys=True)


    ###### old functions (for retrocompatibility)
    def getValue(self, path: str, default_value = None):
        """
        deprecated, please use get_value
        """

        _logger.warning("NestedDict.getValue is deprecated, please use get_value")

        return self.get_value(path, default_value)

    # check if the adress exists
    def hasKey(self, adress: str) -> bool:
        """
        deprecated, please use has_key
        """
        path_arr = adress.split('.')

        _logger.warning("NestedDict.hasKey is deprecated, please use has_key")

        return contains_key(path_arr, self.dict)

    # set a value at the adress.
    # if already exists it is overloaded
    def setValue(self, adress: str, value):
        """
        deprecated, please use set_value
        """

        _logger.warning("NestedDict.setValue is deprecated, please use has_key")
        self.set_value(adress, value)

    def addValue(self, adress, value, unique = False):
        """
        deprecated, please use add_value
        """
        _logger.warning("NestedDict.addValue is deprecated, please use has_key")
        self.add_value(adress, value, unique)
