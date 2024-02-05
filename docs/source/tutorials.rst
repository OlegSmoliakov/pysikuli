==========
Tutorials
==========

Calculator
==========
The completed project is available here: :download:`Download <tutorials/calculator/calculator_source.zip>`.

This is a short script that will allow you to familiarize yourself with the basic pysikuli's features. 

.. rubric::  Firstly, import ``pysikuli`` and ``Key`` class:

.. code-block:: python

   import pysikuli as sik

   from pysikuli import Key

.. rubric:: Now, lets take 3 screenshot of calculator's ``2``, ``+`` and ``=`` buttons and save them in ``/pics`` folder in project root directory.

At this step, it is more convenient and faster to use :ref:`Paste Image <vs_addons>` for this purpose. 
However the tutorial can be repeated without it

Captured pics:

.. list-table:: 

   * - .. figure:: tutorials/calculator/calculator_source/pics/pic_2.png
           :height: 90px 
           :align: center

           pic_2.png

     - .. figure:: tutorials/calculator/calculator_source/pics/pic_plus.png
           :height: 90px 
           :align: center

           pic_plus.png
   
     - .. figure:: tutorials/calculator/calculator_source/pics/pic_equal.png
           :height: 90px 
           :align: center

           pic_equal.png

Then add them to the script:

.. code-block:: python

   if __name__ == "__main__":
      pic_2 = "pics/pic_2.png"
      pic_plus = "pics/pic_plus.png"
      pic_equal = "pics/pic_equal.png"


.. rubric:: To run calculator let's use the most common way:

Press the ``Win`` key, write a ``calculator`` and press ``Enter`` to apply.

In code:

.. code-block:: python

   sik.tap(Key.win), sik.sleep(0.02)
   sik.paste("calculator"), sik.sleep(0.3)
   sik.tap(Key.enter)


.. note:: 

   The ``sik.sleep(...)`` value can be various and depend on your PC reaction.
   You can test several values and choose your favorites

.. rubric:: Now, we can start clicking on calculator's button

.. code-block:: python

   sik.click(pic_2, precision=0.9)
   sik.click(pic_plus)
   sik.click(pic_2, precision=0.9)
   sik.click(pic_equal)

.. note:: 

   if the ``click()`` function couldn't find the buttons or missed,
   you can increase the precision or take another screenshot 
   with more details


Completed code below:

.. code-block:: python

   import pysikuli as sik

   from pysikuli import Key

   if __name__ == "__main__":
      pic_2 = "pics/pic_2.png"
      pic_plus = "pics/pic_plus.png"
      pic_equal = "pics/pic_equal.png"

      sik.tap(Key.win), sik.sleep(0.02)
      sik.paste("calculator"), sik.sleep(0.3)
      sik.tap(Key.enter)

      sik.click(pic_2, precision=0.9)
      sik.click(pic_plus)
      sik.click(pic_2, precision=0.9)
      sik.click(pic_equal)

.. rubric:: Result:

.. figure:: tutorials/calculator/calculator_result.gif
   :alt: Logo
   :align: center

