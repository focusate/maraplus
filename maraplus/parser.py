import re
import functools
import operator
import os
from contextlib import ExitStack
import yaml
import mergedeep
from marabunta import parser as parser_orig
from marabunta.output import print_decorated
from marabunta.exception import ParseError

ADDITIVE_STRAT = mergedeep.Strategy.ADDITIVE

# TODO: Should use tuples here to make sure data is immutable.
VERSION_LIST_PATHS = [
    ['operations', 'pre'],
    ['operations', 'post'],
    ['addons', 'install'],
    ['addons', 'upgrade'],
]
KEY_INSTALL_PATHS = 'install_paths'
# Possible places for install_path argument.
VERSION_INSTALL_PATHS = [
    ['addons', KEY_INSTALL_PATHS],
    # Asterisk means, expand to all modes (keys in modes dict)
    ['modes', '*', 'addons', KEY_INSTALL_PATHS],
]

DEL_OPT_RE = r'DEL->{(.*)}'
ENV_OPT_RE = r'(\$([A-Z0-9]+(?:_[A-Z0-9]+)*))'


def get_from_nested_dict(data: dict, keys: list) -> any:
    """Retrieve value from nested dict."""
    return functools.reduce(operator.getitem, keys, data)


def pop_from_nested_dict(data: dict, keys: list):
    """Pop element at the end of nested dict using keys list as a path."""
    if len(keys) == 1:
        return data.pop(keys[0])
    key = keys[-1]
    inner_dct = get_from_nested_dict(data, keys[:-1])
    return inner_dct.pop(key)


def unpack_keys_from_nested_dict(data: dict, keys_chain: list):
    """Unpack keys lists when any key is asterisk.

    Asterisk means, we have key chains for each key in place of asterisk

    E.g.
        - data={'a': {'b1': {'c': 1}, 'b2': {'c': 2}}}
        - keys_chain=['a', '*', 'c]
        Results in these key chains:
        [
            ['a', 'b1', 'c'],
            ['a', 'b2', 'c'],
        ]

    """
    unpacked = [[]]
    for idx, key in enumerate(keys_chain):
        if key == '*':
            new_unpacked = []
            for path_keys in unpacked:
                prev_keys = path_keys[:idx]
                asterisk_keys = get_from_nested_dict(data, prev_keys).keys()
                new_unpacked.extend(
                    prev_keys + [k] for k in asterisk_keys
                )
            unpacked = new_unpacked
        else:
            for keys in unpacked:
                keys.append(key)
    return unpacked


def _find_data_by_key(datas: list, key: str, val: any) -> dict:
    for data in datas:
        if data[key] == val:
            return data


def _render_env_placeholders(opt):
    new_opt = opt
    for placeholder, env_key in re.findall(ENV_OPT_RE, opt):
        if env_key in os.environ:
            env_val = os.environ[env_key]
            new_opt = new_opt.replace(placeholder, env_val)
    return new_opt


class YamlParser(parser_orig.YamlParser):
    """Parser that can additionally parse install addons option."""

    def __init__(self, parsed):
        self.postprocess_parsed(parsed)
        super().__init__(parsed)

    @property
    def _version_list_paths(self):
        return VERSION_LIST_PATHS

    def postprocess_parsed(self, parsed):
        # Handle install_path arg.
        self._parse_install_paths(parsed)

    def _parse_install_paths(self, parsed):
        versions = parsed['migration']['versions']
        for version in versions:
            unpacked_keys = []
            for vpaths in VERSION_INSTALL_PATHS:
                # It is expected that some paths might not be defined
                # in parsed file.
                try:
                    unpacked_keys.extend(unpack_keys_from_nested_dict(version, vpaths))
                except KeyError:
                    continue
            for keys in unpacked_keys:
                try:
                    paths = pop_from_nested_dict(version, keys)
                except KeyError:
                    continue
                # Parent dict is expected to be addons dict.
                addons_cfg = get_from_nested_dict(version, keys[:-1])
                for path in paths:
                    self._parse_install_path(addons_cfg, path)

    def _parse_install_path(self, addons_cfg: dict, path: str):
        with open(path, 'r') as f:
            modules_dct = yaml.safe_load(f)
            try:
                modules = modules_dct['install']
            except Exception as e:
                raise ParseError(f"install_path file expects 'install' key. Error: {e}")
            if not isinstance(modules, list):
                raise ParseError("'install_paths' key must be a list")
        addons_cfg.setdefault('install', [])
        install = addons_cfg['install']
        for module in modules:
            if module not in install:
                install.append(module)

    @classmethod
    def parser_from_buffer(cls, fp, *extra_fps):
        """Extend to merge extra yaml."""
        parser = super().parser_from_buffer(fp)
        if extra_fps:
            parser._merge_yaml(extra_fps)
        # Must be updated after all yaml are merged (if any) to make
        # sure we are updating up to date dict.
        parser._render_environ_vars()
        return parser

    @classmethod
    def parse_from_file(cls, filename, *extra_filenames):
        """Construct YamlParser from a filename."""
        if extra_filenames:
            filenames = (filename,) + extra_filenames
            with ExitStack() as stack:
                fps = [stack.enter_context(open(fname)) for fname in filenames]
                fp, extra_fps = fps[0], fps[1:]
                return cls.parser_from_buffer(fp, *extra_fps)
        parser = super().parse_from_file(filename)
        parser._render_environ_vars()
        return parser

    def check_dict_expected_keys(self, expected_keys, current, dict_name):
        """Extend to include 'install' key for addons dict."""
        if dict_name == 'addons':
            expected_keys.add('install')
        return super().check_dict_expected_keys(
            expected_keys, current, dict_name
        )

    def _parse_addons(self, version, addons, mode=None):
        super()._parse_addons(version, addons, mode=mode)
        install = addons.get('install') or []
        if install:
            if not isinstance(install, list):
                raise ParseError(
                    "'install' key must be a list", parser_orig.YAML_EXAMPLE
                )
            version.add_install_addons(install, mode=mode)

    def _merge_yaml(self, fps):
        extras = [yaml.safe_load(fp) for fp in fps]
        self._merge_dict(['migration', 'options'], extras)
        self._merge_versions(extras)
        self._update_options(self._opt_clean_dupes)
        self._update_options(self._opt_delete_marked)
        if os.environ.get('MARABUNTA_LOG_YAML'):
            print_decorated(f"YAML\n\n{yaml.dump(self.parsed)}")

    def _merge_dict(self, keys, extras):
        try:
            main_dict = get_from_nested_dict(self.parsed, keys)
        except KeyError:
            return
        for extra in extras:
            try:
                extra_dict = get_from_nested_dict(extra, keys)
                mergedeep.merge(main_dict, extra_dict, strategy=ADDITIVE_STRAT)
            except KeyError:
                continue

    def _merge_versions(self, extras):
        for extra in extras:
            try:
                for version_update in extra['migration']['versions']:
                    self._merge_version(version_update)
            # If extra yaml dict has no version, there is nothing
            # to update, so we skip it.
            except KeyError:
                continue

    def _merge_version(self, version_new: dict):
        # Determine if main dict has this version or we need to add it
        # as new.
        versions = self.parsed['migration']['versions']
        version_old = _find_data_by_key(
            versions,
            'version',
            version_new['version']
        )
        if version_old:
            mergedeep.merge(version_old, version_new, strategy=ADDITIVE_STRAT)
        else:
            versions.append(version_new)

    # Options update utilities after YAMLs are merged.

    def _update_options(self, update_method):
        def update_data(data):
            for keys_path in self._version_list_paths:
                try:
                    vals_list = get_from_nested_dict(data, keys_path)
                    update_method(data, keys_path, vals_list)
                except KeyError:
                    continue
        for version in self.parsed['migration']['versions']:
            update_data(version)
            for mode in version.get('modes', {}).values():
                update_data(mode)

    def _opt_clean_dupes(self, version, keys_path, vals_list):
        # Removing duplicates by preserving order.
        list_no_dupes = list(dict.fromkeys(vals_list))
        # Reusing same list, to have reference to related
        # dictionary.
        vals_list.clear()
        vals_list.extend(list_no_dupes)

    def _opt_delete_marked(self, version, keys_path, vals_list):
        marks = []
        to_delete = []
        for opt in vals_list:
            match = re.match(DEL_OPT_RE, opt)
            if match:
                marks.append(opt)
                to_delete.append(match.groups()[0])
        # Marks themselves are here to just mark what to delete. These
        # must be removed as maraplus would not recognize it.
        for to_del in marks + to_delete:
            vals_list.remove(to_del)

    def _render_environ_vars(self):
        # TODO: render automatically in whole data, not just specific
        # places!
        options = self.parsed.get('migration', {}).get('options', {})
        if options and options.get('install_command'):
            cmd = options['install_command']
            options['install_command'] = _render_env_placeholders(cmd)
        self._update_options(self._opt_render_environ_vars)

    def _opt_render_environ_vars(self, version, keys_path, vals_list):
        for idx, opt in enumerate(vals_list):
            vals_list[idx] = _render_env_placeholders(opt)
