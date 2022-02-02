Maraplus
########

Wrapper for :code:`marabunta` package, that adds some extra features:

* :code:`--db-password-file` argument to read file from file instead of direct input. It is mutually exclusive to :code:`--db-password`.
* :code:`install` option for :code:`addons` key can be used if only install is needed. :code:`upgrade` manages both install and upgrade of modules.
* :code:`--extra-mig-files` can be used to combine extra migration files with main one. This can be useful, when you want to reuse common setup with different projects.
* :code:`DEL->{some-option}` can be used to mark option deletion, when multiple YAML files are merged. This allows to be able to remove not needed options instead of just adding new.
