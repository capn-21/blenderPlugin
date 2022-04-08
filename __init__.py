

bl_info = {
    "name": "Kaedim 3D Artist Utilities",
    "author": "Chris Kinch - Kaedim",
    "version": (1, 3),
    "blender": (2, 93, 4),
    "location": "View3D > Toolbar(N) > Kaedim Exporter",
    "description": "Tools to make.",
    "warning": "",
    "wiki_url": "",
    "category": "Export"
}

from . import KaedimUtilities

if __name__ == "__main__":
    KaedimUtilities.register()