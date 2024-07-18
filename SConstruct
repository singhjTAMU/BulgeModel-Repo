#!/usr/bin/env python

import os
import pathlib
import inspect
import waves
import SCons
from SCons.Script import *


# Accept command line options with fall back default values
AddOption(
    "--build-dir",
    dest = "variant_dir_base",
    default = "build",
    nargs = 1,
    type = "string",
    action = "store",
    metavar = "DIR",
    help = "SCons build (variant) root directory. Relative or absolute path. (default: '%default')"
)

# Inherit user's full environment and set project options
env = Environment(
    ENV = os.environ.copy(),
    variant_dir_base = GetOption("variant_dir_base")
)

# Empty defaults list to avoid building all simulation targets default
env.Default()

# Find programs for target ignoring/absolute path for target actions
env["sphinx_build"] = waves.scons_extensions.add_program(["sphinx-build"], env)
env["abaqus"] = waves.scons_extensions.add_program(["/sw/hprc/sw/ABAQUS/2021/Commands/abaqus", "abaqus"], env)  

# Set project internal variables and variable substitution dictionaries
project_name = "BulgeModel-CAE"
version = "0.1.0"
latex_project_name = project_name.replace("_", "-")
author_list = ["Jasdeep Singh"]
author_latex = r" \and ".join(author_list)
documentation_source_dir = pathlib.Path("docs")

project_variables = {
    "BulgeModel": project_name,
    "project_dir": Dir(".").abspath,
    "version": version,
    "documentation_pdf": f"{latex_project_name}-{version}.pdf",
}

# Build path object for extension and re-use
variant_dir_base = pathlib.Path(env["variant_dir_base"])

# Add WAVES builders
env.Append(BUILDERS={
    "AbaqusJournal": waves.scons_extensions.abaqus_journal(program=env["abaqus"]),
    "AbaqusSolver": waves.scons_extensions.abaqus_solver(program=env["abaqus"]),
    "SphinxBuild": waves.scons_extensions.sphinx_build(program=env["sphinx_build"], options="-W"),
    "SphinxPDF": waves.scons_extensions.sphinx_latexpdf(program=env["sphinx_build"], options="-W")
})
env.Append(SCANNERS=waves.scons_extensions.sphinx_scanner())                       

# Add simulation targets
workflow_configurations = [
    "Bulge_SConscript.py"                                                                       
]

for workflow in workflow_configurations:
    build_dir = variant_dir_base / workflow
    SConscript(workflow, variant_dir = build_dir,
    exports = "env", duplicate = True)

# Add default target list to help message
waves.scons_extensions.project_help_message()
