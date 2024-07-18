#!/usr/bin/env python

import pathlib
import waves.scons_extensions

# Define abaqus_source_abspath
abaqus_source_abspath = pathlib.Path('/scratch/user/singhj/waves/BulgeModel')

# Inherit the parent construction environment
Import("env")

# Simulation variables
build_directory = pathlib.Path(Dir(".").abspath)
workflow_name = build_directory.name
model = "BM"
simulation_variables = {
    'density': [9.5E-9, 1.9E-8, 2.85E-8],
    'ym': [40000., 80000., 120000.]
}

# Collect the target nodes to build a concise alias for all targets
workflow = []

# Function to add simulations for each set of parameters
def add_simulation(env, density, ym):
    sim_name = f"{model}_density_{density}_ym_{ym}"
    target_odb = f"{sim_name}.odb"
    cae_file = f"{sim_name}.cae"

    print(f"Adding simulation for density={density}, ym={ym} -> sim_name={sim_name}")

    # Perform the AbaqusJournal build
    abaqus_journal = env.AbaqusJournal(
        target=target_odb,
        source=["submit_cae.py", cae_file],
        journal_options=f"--input-file {cae_file} --job-name {sim_name} --model-name {model}"
    )
    workflow.extend(abaqus_journal)

    # Perform the copy and substitution step
    abaqus_source_file = abaqus_source_abspath / f"{model}.inp.in"
    target_file = build_directory / f"{sim_name}.inp"

    print(f"Creating target file: {target_file}")

    copy_substitute = waves.scons_extensions.copy_substitute(
        source_list=[abaqus_source_file],
        substitution_dictionary={
            'density': density,
            'ym': ym
        },
        env=env,
        build_subdirectory=str(build_directory / sim_name)
    )
    workflow.extend(copy_substitute)

# Loop over all combinations of parameters and add simulations
for density in simulation_variables['density']:
    for ym in simulation_variables['ym']:
        add_simulation(env, density, ym)

# Collector alias based on build directory name
env.Alias(workflow_name, workflow)

# Error handling if abaqus is not found
if not env.get("abaqus", None):
    print(f"Error: 'abaqus' program not found in the construction environment.")
    Exit(1)  # Exit SCons with an error status
