To install the plugin for the first time start by downloading the zip of the latest release.
Open Blender navigate to Edit tab and select Preferences, choose the Add-ons tab and Click install.
Find the .zip you downloaded from github and install it (it should appear under the add-ons).
Make sure to enable it and then expand it to enable the automated check for updates as well.

Kaedim Exporter Change Log

v1.1:

- Plugin now raises an exception if user tries to export while no objects are selected.

v1.2:

- Fixed naming convention error preventing import.

v1.3:

- Introduced a quick import feature for reference images. Clicking on import after selecting a folder will set the viewport to front orthographic and import the most recently added image file from that folder as a reference object.

v1.3.1:

- Import reference feature now looks for both .jpeg and .png files in the designated directory.

v1.3.2:

- Fixed issue that stopped import of .jpeg reference images if they were saved as .jpg

v1.4.0:

- Added ability to embed image texture files into the FBX binary file.
- Now recalculates normals upon export for all selected objects

v1.4.1:

- Automatically selects and deletes loose edges upon export. This is to prevent the wireframe bug from occurring in threejs.

v1.4.2:

- Normals recalculation can now be toggled via checkbox in Extras
- FBX texture packing option moved to Extras

v1.4.3:

- Added hard constraints for model watertightness 
- Fixed FBX scaling problem
- All checked  by default

When updating version make sure to edit addon_constructor.py line 22, kaedimexpoorter.py line 4 and addon_updater.py line 25
