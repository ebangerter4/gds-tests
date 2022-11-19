#%%
from types import LambdaType
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import nlopt
import numpy as np
from meep import Block, EigenModeSource, MaterialGrid, Simulation, Vector3, Volume
from meep.adjoint import DesignRegion, EigenmodeCoefficient, OptimizationProblem
from meep.visualization import get_2D_dimensions
from numpy import ndarray

import gdsfactory as gf
from gdsfactory import Component
from gdsfactory.simulation.gmeep import get_simulation
from gdsfactory.tech import LayerStack
from gdsfactory.types import Layer
from gdsfactory.simulation.gmeep import get_meep_adjoint_optimizer

#%%
def J(source, top, bottom):
    # Want both the ports to have 50% of the power
    product = (100*top*bottom) # Greatest value will be when they're both 0.5
    return product
opt = get_meep_adjoint_optimizer(component=Component("mmi1x2"))