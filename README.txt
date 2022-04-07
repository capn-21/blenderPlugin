
Kaedim Exporter Change Log

v1.1:
    Plugin now raises an exception if user tries to export while no objects are selected.

v1.2:
    Fixed naming convention error preventing import.

v1.3:
    Introduced a quick import feature for reference images. Clicking on import after selecting a folder 
    will set the viewport to front orthographic and import the most recently added image file from that 
    folder as a reference object.

v1.3.1:
    Import reference feature now looks for both .jpeg and .png files in the designated directory.

V1.3.2:
    Fixed issue that stopped import of .jpeg reference images if they were saved as .jpg

V1.4:
    Added ability to embed image texture files into the FBX binary file. 
    Now recalculates normals upon export for all selected objects}