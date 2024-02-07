API
===
Mouse functions
-----------------
.. autofunction:: pysikuli.click
.. autofunction:: pysikuli.rightClick
.. autofunction:: pysikuli.mouseDown
.. autofunction:: pysikuli.mouseUp
.. autofunction:: pysikuli.mouseMove
.. autofunction:: pysikuli.mouseSmoothMove
.. autofunction:: pysikuli.mouseMoveRelative
.. autofunction:: pysikuli.mousePosition
.. autofunction:: pysikuli.scroll
.. autofunction:: pysikuli.hscroll
.. autofunction:: pysikuli.vscroll
.. autofunction:: pysikuli.dragDrop

Keyboard functions
------------------------
.. autofunction:: pysikuli.tap
.. autofunction:: pysikuli.keyUp
.. autofunction:: pysikuli.keyDown
.. autofunction:: pysikuli.hotkey
.. autofunction:: pysikuli.write
.. autofunction:: pysikuli.pressedKeys
.. autofunction:: pysikuli.paste
.. autofunction:: pysikuli.copyToClip
.. autofunction:: pysikuli.pasteFromClip

Pop-ups
--------
.. autofunction:: pysikuli.popupAlert
.. autofunction:: pysikuli.popupPassword
.. autofunction:: pysikuli.popupConfirm
.. autofunction:: pysikuli.popupPrompt

File management functions
--------------------------
.. autofunction:: pysikuli.saveNumpyImg
.. autofunction:: pysikuli.saveScreenshot
.. autofunction:: pysikuli.deleteFile

Utils
-------
.. autofunction:: pysikuli.getLocation
.. autofunction:: pysikuli.getRegion
.. autofunction:: pysikuli.cleanupPics

Screenshot functions
----------------------
.. autofunction:: pysikuli.exist
.. autofunction:: pysikuli.existAny
.. autofunction:: pysikuli.existCount
.. autofunction:: pysikuli.existFromFolder
.. autofunction:: pysikuli.find
.. autofunction:: pysikuli.grab
.. autofunction:: pysikuli.getPixel
.. autofunction:: pysikuli.wait
.. autofunction:: pysikuli.waitWhileExist

Window control functions
-------------------------
.. autofunction:: pysikuli.activateWindow
.. autofunction:: pysikuli.activateWindowAt
.. autofunction:: pysikuli.activateWindowUnderMouse
.. autofunction:: pysikuli.getWindowRegion
.. autofunction:: pysikuli.getWindowWithTitle
.. autofunction:: pysikuli.getWindowUnderMouse
.. autofunction:: pysikuli.getAllWindowsTitle
.. autofunction:: pysikuli.minimizeWindow
.. autofunction:: pysikuli.maximizeWindow
.. autofunction:: pysikuli.closeWindow
.. autofunction:: pysikuli.windowExist

Classes
---------
.. autoclass:: pysikuli.Region

   Uses the same functions that are declared separately, but
   sets the region and time_step parameters by default.

   .. autoattribute:: pysikuli.Region.reg
      :annotation: tuple(int, int, int, int)

   .. autoattribute:: pysikuli.Region.x1
      :annotation: (int)
      
   .. autoattribute:: pysikuli.Region.y1
      :annotation: (int)

   .. autoattribute:: pysikuli.Region.x2
      :annotation: (int)

   .. autoattribute:: pysikuli.Region.y2
      :annotation: (int)

   .. autoattribute:: pysikuli.Region.time_step
      :annotation: (float)

      Common parameter for all search function in Class ``Region``
      Sets the time between each iteration of the search. 
      Default values is ``config.TIME_STEP``
   .. automethod:: click
   .. automethod:: rightClick
   .. automethod:: has
   .. automethod:: find
   .. automethod:: existAny
   .. automethod:: wait
   .. automethod:: waitWhileExist

.. py:class:: pysikuli.Button

   - Button.left
   - Button.middle
   - Button.right


.. py:class:: pysikuli.Key

   The class **Key** attributes are platform-dependent, but they are the same in Linux and Windows.
   
   Common attributes:

   - Key.alt
   - Key.alt_r
   - Key.alt_gr
   - Key.shift
   - Key.shift_r
   - Key.ctrl, Key.ctrl_r
   - Key.caps_lock
   - Key.left
   - Key.right
   - Key.up  
   - Key.down    
   - Key.page_down
   - Key.page_up
   - Key.home
   - Key.end
   - Key.esc
   - Key.space
   - Key.tab
   - Key.f1
   - Key.f2
   - Key.f3
   - Key.f4
   - Key.f5
   - Key.f6
   - Key.f7
   - Key.f8
   - Key.f9
   - Key.f10
   - Key.f11
   - Key.f12
   - Key.f13
   - Key.f14
   - Key.f15
   - Key.f16
   - Key.f17
   - Key.f18
   - Key.f19
   - Key.f20

   - Key.media_play_pause
   - Key.media_volume_mute
   - Key.media_volume_down
   - Key.media_volume_up
   - Key.media_previous
   - Key.media_next

   Windows/Linux specific keys:

      - Key.win
      - Key.enter
      - Key.delete
      - Key.backspace
      
      - Key.insert
      - Key.menu
      - Key.num_lock
      - Key.pause
      - Key.print_screen
      - Key.scroll_lock

   MacOS specific keys:

      - Key.cmd
      - Key.cmd_r
      - Key.delete

      - Key.option
      - Key.option_r
      - Key.return_r

.. py:attribute:: pysikuli.config

   The ``config`` variable contain ``Config`` class
   with all global pysikuli settings. 
   The full setting list is provided below. 

   General parameters:

   ================================ =========================== ==================================== ===================================================================================================================================
      Parameter                        Type                       Default value                       Description
   ================================ =========================== ==================================== ===================================================================================================================================
      OSX, WIN, UNIX                 bool                        ``False``                            Sets to ``True`` value if you use this **OS**
      MIN_SLEEP_TIME                 float                       ``0.02``                             If the time is less than this value, the sleep time isn't accurate enough
      PAUSE_BETWEEN_ACTION           float                       ``0``                                The number of seconds of pause after EVERY public function call. Useful for debugging
      FAILSAFE                       bool                        ``True``                             If the mouse is within ``FAILSAFE_REGIONS`` or ``FAILSAFE_HOTKEY`` is pressed and ``FAILSAFE`` is ``True``, a ``FailSafeException`` will be raised.
      FAILSAFE_REGIONS               list                        ``[(0, 0, 0, 0)]``                   You can add another regions using the ``.append()`` method.
      FAILSAFE_HOTKEY                list                        MacOS:                               Currently, only one hotkey can be configured

                                                                 ``[Key.alt, Key.shift, "c"]``
                                                                 
                                                                 Windows/Linux:

                                                                 ``[Key.ctrl, Key.alt, "z"]``     
      WINDOW_WAITING_CONFIRMATION    bool                        ``True``                             If active, pysikuli will wait for the window management functions to complete their execution
      REFRESH_RATE                   int                         set automatically                    Left in case of incorrect detection. Uses in ``scroll`` functions and ``DEBUG SETTINGS``
      MONITOR_REGION                 tuple                       the screen region of                 Left in case of incorrect detection. Uses as default ``Region`` in search functions and for validating user ``Region`` s
                                    
                                     (int, int, int, int)   
                                                                 
                                                                 your main monitor            
      MONITOR_RESOLUTION             tuple(int, int)             the resolution of                    Uses in ``popup`` functions
                                                                 
                                                                 your main monitor            
      DEBUG                          bool                        ``False``                            If ``True``, ``DEBUG_SETTINGS``  will be applied
   ================================ =========================== ==================================== ===================================================================================================================================

   ``DEBUG_SETTINGS`` list:

   =========================  ===============
   Parameter                  Default value
   =========================  ===============
   PAUSE_BETWEEN_ACTION       ``0.5``
   TIME_STEP                  ≈ time per frame
   MOUSE_SPEED                ``1``
   =========================  ===============

   Search functions parameters:

   =========================  ==========  ==============  ==============================================================================
   Parameter                  Type        Default value    Description
   =========================  ==========  ==============  ==============================================================================
   TIME_STEP                  float       ``0``            TIME_STEP is the time in seconds between each step in function loop, such as ``find``, ``wait``, ``tap``, ``write``, ``click`` and etc.
   MAX_SEARCH_TIME            float       ``2.0``          The time limit for search functions. If it is exceeded, ``None`` is returned
   GRAYSCALE                  bool        ``True``         This parameter increases speed by about 30%, but degrades unambiguous image recognition
   COMPRESSION_RATIO          float       ``2``            This option almost doubles the speed by using compressed images in image recognition, but degrades unambiguous image recognition
   MIN_PRECISION              float       ``0.8``          The value after which all search functions return positive
   =========================  ==========  ==============  ==============================================================================

   Mouse functions parameters:

   =========================  ===============  ================  =============
   Parameter                  Type             Default value     Description
   =========================  ===============  ================  =============
   MOUSE_PRIMARY_BUTTON       ``Button``       ``Button.left``    The primary button used for mouse actions by default
   MOUSE_SECONDARY_BUTTON     ``Button``       ``Button.right``   The secondary button used for mouse actions by default
   MOUSE_SPEED                float            ``2``              The speed of the mouse movement. This is abstract value and if equal to 1 it ≈ 1000px per second
   =========================  ===============  ================  =============

   Utils functions parameters:

   =======================  =====  =========================================  ==========================
   Parameter                Type   Default value                              Description
   =======================  =====  =========================================  ==========================
   SOUND_ON                 bool   ``True``                                   Determines if sound is enabled
   SOUND_CAPTURE_PATH       str    ``"tools_data/_capture.mp3"``              Path to the capture sound file
   SOUND_FINISH_PATH        str    ``"tools_data/_finish.mp3"``               Path to the finish sound file
   =======================  =====  =========================================  ==========================

   Popup functions parameters: 

   ===========================  ===================  =======================  ======================================
   Parameter                    Type                 Default value             Description
   ===========================  ===================  =======================  ======================================
   OK_TEXT                      str                  ``"OK"``                  Text for the "OK" button
   CANCEL_TEXT                  str                  ``"Cancel"``              Text for the "Cancel" button
   ROOT_WINDOW_POSITION         tuple(int, int)      ≈ center of the screen    Position of the root window (the top left corner of the window)
   PROPORTIONAL_FONT_SIZE       int                  ``10``                    Font size for proportional text
   MONOSPACE_FONT_SIZE          int                  ``9``                     Font size for monospace text
   TEXT_ENTRY_FONT_SIZE         int                  ``12``                    Font size for text entry fields
   ===========================  ===================  =======================  ======================================
