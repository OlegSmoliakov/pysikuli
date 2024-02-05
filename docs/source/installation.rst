===============
Installation
===============
On Windows use:

.. code-block:: console

   (.venv) $ pip install pysikuli

.. code-block:: console

   python -m pip install pysikuli

On MacOS and Linux use:

.. code-block:: console

   (.venv) $ pip3 install pysikuli

.. code-block:: console

   python3 -m pip install pysikuli

External dependencies
======================
External dependencies mostly belong to the playsound module, which is used to user-friendly capture ``Region`` and ``Location``. However, pysikuli can work normally without them.

MacOS
------
playsound dependencies:

.. code-block:: console
   
   $ brew install cairo pkg-config

Also you need to enable **Accessibility** and **Screen capture** permissions to terminal or python itself.

Linux:
-------
playsound dependencies:

- on Ubuntu/Debian: ``sudo apt install libgirepository1.0-dev libcairo2-dev``
- on Arch Linux: ``sudo pacman -S cairo pkgconf``
- on Fedora: ``sudo dnf install cairo-devel pkg-config python3-devel``
- on penSUSE: ``sudo zypper install cairo-devel pkg-config python3-devel``

evdev dependencies:

- ``sudo apt-get install python3-dev or python3.x``, where x is version of your python

VS Code add-ons
===============
I would also recommend installing these VS Code's add-ons:

.. _vs_addons:

- `Paste Image <https://marketplace.visualstudio.com/items?itemName=mushan.vscode-paste-image>`_, for pasting screenshots directly in the code from clipboard. You can also set up a specific folder to store your pics.
- `Image preview <https://marketplace.visualstudio.com/items?itemName=kisstkondoros.vscode-gutter-preview>`_, for preview captured photos
- `luna-paint <https://marketplace.visualstudio.com/items?itemName=Tyriar.luna-paint>`_, useful tool for fast cropping captured images inside VS Code
