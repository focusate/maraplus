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

VERSION_LIST_PATHS = [
    ['operations', 'pre'],
    ['operations', 'post'],
    ['addons', 'install'],
    ['addons', 'upgrade'],
]


# TODO: move this to footil.
def _get_from_dict(data: dict, keys: list) -> any:
    """Retrieve value from nested dict."""
    return functools.reduce(operator.getitem, keys, data)


def _find_data_by_key(datas: list, key: str, val: any) -> dict:
    for data in datas:
        if data[key] == val:
            return data


class YamlParser(parser_orig.YamlParser):
    """Parser that can additionally parse install addons option."""

    @property
    def _version_list_paths(self):
        return VERSION_LIST_PATHS

    @classmethod
    def parser_from_buffer(cls, fp, *extra_fps):
        """Extend to merge extra yaml."""
        parser = super().parser_from_buffer(fp)
        if extra_fps:
            parser._merge_yaml(extra_fps)
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
        return super().parse_from_file(filename)

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
        self._clean_dupes_in_list_keys()
        if os.environ.get('MARABUNTA_LOG_YAML'):
            print_decorated(f"YAML\n\n{yaml.dump(self.parsed)}")

    def _merge_dict(self, keys, extras):
        try:
            main_dict = _get_from_dict(self.parsed, keys)
        except KeyError:
            return
        for extra in extras:
            try:
                extra_dict = _get_from_dict(extra, keys)
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

    def _clean_dupes_in_list_keys(self):
        # Using expected list keys to clean up values.
        for version in self.parsed['migration']['versions']:
            for keys_path in self._version_list_paths:
                try:
                    vals_list = _get_from_dict(version, keys_path)
                    # Removing duplicates by preserving order.
                    list_no_dupes = list(dict.fromkeys(vals_list))
                    # Reusing same list, to have reference to related
                    # dictionary.
                    vals_list.clear()
                    vals_list.extend(list_no_dupes)
                except KeyError:
                    continue
