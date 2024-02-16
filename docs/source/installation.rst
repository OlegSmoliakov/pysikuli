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
External dependencies mostly belong to the sounddevice module, which is used to user-friendly capture ``Region`` and ``Location``. However, pysikuli can work normally without them.

Windows:
--------
.. rubric:: sounddevice dependence:

- `Microsoft C++ build tools <https://visualstudio.microsoft.com/visual-cpp-build-tools>`_ 

Linux:
-------
.. rubric:: sounddevice dependencies:

.. code-block:: console
   
   $ sudo apt install libportaudio2

Also, pysikuli will try to install this package on its own the first time you run it

MacOS
-----
You need to enable **Accessibility** and **Screen capture** permissions to terminal or python itself.


VS Code add-ons
===============
I would also recommend installing these VS Code's add-ons:

.. _vs_addons:

- `Paste Image <https://marketplace.visualstudio.com/items?itemName=mushan.vscode-paste-image>`_, for pasting screenshots directly in the code from clipboard. You can also set up a specific folder to store your pics.
- `Image preview <https://marketplace.visualstudio.com/items?itemName=kisstkondoros.vscode-gutter-preview>`_, for preview captured photos
- `luna-paint <https://marketplace.visualstudio.com/items?itemName=Tyriar.luna-paint>`_, useful tool for fast cropping captured images inside VS Code
