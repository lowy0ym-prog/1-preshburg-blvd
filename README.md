# 1 Preshburg Blvd — Blender reconstruction

This repository builds an editable Blender model and PNG/GLB previews of the building at 1 Preshburg Blvd, Monroe, NY 10950.

## Geometry priorities
- Forest Rd is the front road across the south/front of the site.
- Strelisk Ct is on the west/left side.
- Preshburg Blvd is on the east/right side.
- The building is modeled as a tall white-sided multi-level residential building.
- The Strelisk side includes stacked porches/balconies.
- The Forest Rd side includes the repeated projecting bay/window rhythm, raised retaining wall and evergreen landscaping.
- The rear includes additional porch/balcony geometry.

The model is an approximation based on the supplied Street View/map screenshots and publicly available property/location information; it is not a survey or architectural drawing.

## Build
GitHub Actions downloads Blender, runs build_preshburg.py headlessly, renders five views, saves the native .blend, and exports a .glb. The files are uploaded as one Actions artifact.
