Kaedim Exporter Change Log

v1.1:
- Plugin now raises an exception if user tries to export while no objects are selected.

v1.2:
- Fixed naming convention error preventing import.

v1.3:
- Introduced a quick import feature for reference images. Clicking on import after selecting a folder will set the viewport to front orthographic and import the most recently added image file from that folder as a reference object. 

v1.3.1:
- Import reference feature now looks for both .jpeg and .png files in the designated directory.


When updating version make sure to edit addon_constructor.py line 22, kaedimexpoorter.py line 4 and addon_updater.py line 25