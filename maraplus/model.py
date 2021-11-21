from marabunta import model as model_orig


class Version(model_orig.Version):
    """Extend class to add `add_install_addons` operation."""

    def add_install_addons(self, addons, mode=None):
        """Add addons for installation for version."""
        version_mode = self._get_version_mode(mode=mode)
        version_mode.add_install_addons(addons)

    def install_addons_operation(self, addons_state, mode=None):
        """Prepare install addons operation."""
        installed = set(
            a.name for a in addons_state
            if a.state in ('installed', 'to upgrade')
        )
        base_mode = self._get_version_mode()
        addons_list = base_mode.install_addons.copy()
        if mode:
            add_mode = self._get_version_mode(mode=mode)
            addons_list |= add_mode.install_addons
        to_install = addons_list - installed
        return InstallAddonsOperation(self.options, to_install)


class VersionMode(model_orig.VersionMode):
    """Extend class to add `add_install_addons` option."""

    def __init__(self, name=None):
        """Extend to include install_addons attribute."""
        super().__init__(name=name)
        self.install_addons = set()

    def add_install_addons(self, addons):
        """Add addons for installation for version mode."""
        self.install_addons.update(addons)


class InstallAddonsOperation(model_orig.UpgradeAddonsOperation):
    """Operation class to only install addons if needed."""

    def __init__(self, options, to_install):
        """Extend to only use install set and not upgrade."""
        # Empty to_upgrade to not break subclass functionality.
        super().__init__(options, to_install, set([]))
