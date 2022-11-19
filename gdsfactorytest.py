#%%
import gdsfactory as gf
from gdsfactory.tech import LayerStack, LayerLevel, LAYER
# WG=220nm Si core
# SLAB150 = 150nm Si slab, 70nm shallow etch for grating couplers
# SLAB90 = 90n Si slab, for modulators
# DEEPTRENCH
# MH heater
# M1 metal 1

c = gf.layers.LAYER_COLORS.preview()
#print(c)

layer_wg = gf.LAYER.WG
#print(layer_wg)

extract = c.extract(layers=(gf.LAYER.M1, gf.LAYER.VIAC))
#print(extract)

removed = extract.remove_layers(layers=(gf.LAYER.VIAC))
#print(removed)

c = gf.components.straight(layer=(2,0))
#print(c)

remap = c.remap_layers(layermap={(2,0): gf.LAYER.WGN})
#print(remap)

#%%
# Create a generic LayerStack.
# Could also put it in a function that returns a LayerStack

def get_layer_stack_generic(thickness_silicon_core: float = 220e-3, thickness_cladding: float = 3.0
) -> LayerStack:
    LayerStack(layers=dict(core= LayerLevel(
                                layer=LAYER.WG,
                                thickness=thickness_silicon_core,
                                zmin=0.0,
                                material="si"),
                        clad=LayerLevel(
                            layer=LAYER.WGCLAD,
                            thickenss=thickness_cladding,
                            zmin=0.0,
                            material="sio2"),
                        slab150=LayerLevel(
                            layer=LAYER.SLAB150,
                            thickness=150e-3,
                            zmin=0,
                            material="si",
                        ),
                        slab90=LayerLevel(
                            layer=LAYER.SLAB90,
                            thickness=90e-3,
                            zmin=0.0,
                            material="si",
                        ),
                        nitride=LayerLevel(
                            layer=LAYER.WGN,
                            thickness=350e-3,
                            zmin=220e-3 + 100e-3,
                            material="sin",
                        ),
                        ge=LayerLevel(
                            layer=LAYER.GE,
                            thickness=500e-3,
                            zmin=thickness_silicon_core,
                            material="ge",
                        ),
                        via_contact=LayerLevel(
                            layer=LAYER.VIAC,
                            thickness=1100e-3,
                            zmin=90e-3,
                            material="Aluminum",
                        ),
                        metal1=LayerLevel(
                            layer=LAYER.M1,
                            thickness=750e-3,
                            zmin=thickness_silicon_core + 1100e-3,
                            material="Aluminum",
                        ),
                        heater=LayerLevel(
                            layer=LAYER.HEATER,
                            thickness=750e-3,
                            zmin=thickness_silicon_core + 1100e-3,
                            material="TiN",
                        ),
                        viac=LayerLevel(
                            layer=LAYER.VIA1,
                            thickness=1500e-3,
                            zmin=thickness_silicon_core + 1100e-3 + 750e-3,
                            material="Aluminum",
                        ),
                        metal2=LayerLevel(
                            layer=LAYER.M2,
                            thickness=2000e-3,
                            zmin=thickness_silicon_core + 1100e-3 + 750e-3 + 1.5,
                            material="Aluminum",
                        ),
                    )
                )
    
#%%
import gdsfactory as gf
import gdsfactory.simulation.gmeep as gm
import gdsfactory.simulation as sim
from gdsfactory.tech import LayerStack, LayerLevel, LAYER
import numpy as np

c = gf.components.straight(length=2)
df = gm.write_sparameters_meep(c, run=True, ymargin_top=3, ymargin_bot=3)
#%%
# V useful help function for gm methods
help(gm.write_sparameters_grating)

#%%
import gdsfactory as gf
from gdsfactory.types import Layer, LayerColors, LayerColor, LayerStack, LayerLevel
from pydantic import BaseModel

nm = 1e-3

# Define layer stack
class LayerMap(BaseModel):
    WG: Layer = (34, 0)
    SLAB150: Layer = (2, 0)
    DEVREC: Layer = (68, 0)
    PORT: Layer = (1, 10)
    PORTE: Layer = (1, 11)
    TE: Layer = (203, 0)
    TM: Layer = (204, 0)
    TEXT: Layer = (66, 0)


LAYER = LayerMap()

# Give the layers colors so diagrams are clear
layer_colors = dict(
    WG=LayerColor(gds_layer=34, gds_datatype=0, color="gold"),
    SLAB150=LayerColor(gds_layer=2, gds_datatype=0, color="red"),
    TE=LayerColor(gds_layer=203, gds_datatype=0, color="green"),
)
LAYER_COLORS = LayerColors(layers=layer_colors)

def get_layer_stack_faba(
    thickness_wg: float = 500 * nm, thickness_slab: float = 150 * nm
) -> LayerStack:
    """Returns fabA LayerStack"""
    # Layerstack for simulation and 3D rendering
    return LayerStack(
        layers=dict(
            strip=LayerLevel(
                layer=LAYER.WG,
                thickness=thickness_wg,
                zmin=0.0,
                material="si"
            ),
            strip2=LayerLevel(
                layer=LAYER.SLAB150,
                thickness=thickness_slab,
                zmin=0.0,
                material="si"
            )
        )
    )
    
LAYER_STACK = get_layer_stack_faba()

WIDTH = 2

# Specify a cross_section to use
# Define path with list of points, to create component, extrude path with a cross section
strip = gf.partial(gf.cross_section.cross_section, width=WIDTH, layer=LAYER.WG)

mmi1x2 = gf.partial(
    gf.components.mmi1x2,
    width=WIDTH,
    width_taper=WIDTH,
    width_mmi=3 * WIDTH,
    cross_section=strip,
)

generic_pdk = gf.pdk.GENERIC

fab_a = gf.Pdk(
    name="Fab_A",
    cells=dict(mmi1x2=mmi1x2),
    cross_sections=dict(strip=strip),
    layers=LAYER.dict(),
    base_pdk=generic_pdk,
    sparameters_path=gf.config.sparameters_path,
    layer_colors=LAYER_COLORS,
    layer_stack=LAYER_STACK,
)
fab_a.activate()

gc = gf.partial(
    gf.components.grating_coupler_elliptical_te, layer=LAYER.WG, cross_section=strip
)

c = gf.components.mzi()
c_gc = gf.routing.add_fiber_array(component=c, grating_coupler=gc, with_loopback=False)
c_gc

#%%
import gdsfactory as gf
from gdsfactory.types import LayerSpec

@gf.cell
def straight_wide(
    length: float=5, width: float=1, layer: LayerSpec =(2,0)
) -> gf.Component:
    wg = gf.Component("straight sample")
    wg.add_polygon([(0,0), (length,0), (length, width), (0,width)], layer=layer)
    wg.add_port(
        name="o1", center=(0,width/2), width=width, orientation=180,layer=layer
    )
    wg.add_port(
        name="o2", center=(length, width/2), width=width, orientation=0, layer=layer
    )
    return wg

def test_straight_wide(data_regression):
    component= straight_wide()
    data_regression.check(component.to_dict())

c = gf.Component("MultiWaveguide")
WG1= straight_wide(length=10,width=1)
WG2= straight_wide(length=12,width=2)
wg1 = c.add_ref(WG1)
wg2 = c << WG2
wg3 = c.add_ref(straight_wide(length=14, width=3))
c.show(show_ports=True)
c