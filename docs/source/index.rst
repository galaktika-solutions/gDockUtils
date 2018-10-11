==========
gDockUtils
==========

Utilities to help "dockerize" things.

------------

.........
``gprun``
.........

::

  usage: gprun [-h] [-u USERSPEC] [-s STOPSIGNAL] command [...]

  Runs the specified command using different user/group. On SIGTERM and SIGINT,
  sends the specified signal to the process.

  positional arguments:
    command               the command to run

  optional arguments:
    -h, --help            show this help message and exit
    -u USERSPEC, --userspec USERSPEC
                          user/group to switch to in the form
                          (uid|username)[:(gid|groupname)]
    -s STOPSIGNAL, --stopsignal STOPSIGNAL
                          the name of the signal to send to the process

.. autofunction:: gdockutils.gprun.gprun

------------

.......
``ask``
.......

::

  usage: ask [-h] [-p PROMPT] [-d DEFAULT] [-m | -y] [options [options ...]]

  Asks the user to select one (or more) from a list of options.

  positional arguments:
    options               the options to choose from

  optional arguments:
    -h, --help            show this help message and exit
    -p PROMPT, --prompt PROMPT
                          print a description to the user
    -d DEFAULT, --default DEFAULT
                          the default selection to use
    -m, --multiple        multiple choice
    -y, --yesno           yes/no question

.. autofunction:: gdockutils.ui.ask
