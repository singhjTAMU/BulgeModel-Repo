import os
import shutil
import inspect
import tempfile
import argparse
import sys
import json
import abaqus
import abaqusConstants
from abaqus import *

def main(input_file, job_name, model_name="BulgeModel", cpus=None, **kwargs):
    if cpus is not None:
        kwargs.update({"numCpus": cpus})

    with tempfile.NamedTemporaryFile(suffix='.cae', dir=".") as copy_file:
        shutil.copyfile(input_file, copy_file.name)

        openMdb(pathName=copy_file.name)

        if job_name in mdb.jobs.keys():
            script_job = mdb.jobs[job_name]
            script_job.setValues(**kwargs)
        elif model_name in mdb.models.keys():
            script_job = abaqus.mdb.Job(name=job_name, model=model_name, **kwargs)
        else:
            raise RuntimeError(f"Could not find model name '{model_name}' in file '{input_file}'")

        script_job.submit()
        script_job.waitForCompletion()

def get_parser():
    filename = inspect.getfile(lambda: None)
    basename = os.path.basename(filename)
    basename_without_extension, extension = os.path.splitext(basename)

    default_model_name = "BulgeModel-1"
    default_cpus = None
    default_json_file = None

    prog = f"abaqus cae -noGui {basename}"
    cli_description = (
        "Open an Abaqus CAE model file and submit the job."
        "If the job already exists, ignore the model name and update the job options. If the job does not exist, "
        "create it using the job attributes passed in from the API/CLI, e.g. ``cpus`` and ``kwargs``. "
        "Because Abaqus modifies CAE files on open, a temporary copy of the file is created to avoid constant job "
        "rebuilds in build tools like SCons or Make."
    )
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument('-i', '--input-file', type=str, required=True,
                        help="The Abaqus CAE model file with extension, e.g. ``input_file.cae``")
    parser.add_argument('-j', '--job-name', type=str, required=True,
                        help="The name of the Abaqus job")
    parser.add_argument('-m', '--model-name', type=str, default=default_model_name,
                        help="The name of the Abaqus model (default %(default)s)")
    parser.add_argument('--cpus', type=int, default=default_cpus,
                        help="The number of cpus for the Abaqus simulation (default %(default)s)")
    parser.add_argument('--json-file', type=str, default=default_json_file,
                        help="A JSON file containing a dictionary of keyword arguments for ``abaqus.mdb.Job`` "
                             "(default %(default)s)")
    return parser

def return_json_dictionary(json_file):
    kwargs = {}
    if json_file is not None:
        with open(json_file) as json_open:
            dictionary = json.load(json_open)
            for key, value in dictionary.items():
                if isinstance(key, str):
                    key = str(key)
                if isinstance(value, str):
                    value = str(value)
                if hasattr(abaqusConstants, value):
                    value = getattr(abaqusConstants, value)
                kwargs[key] = value
    return kwargs

if __name__ == '__main__':
    parser = get_parser()
    args, unknown = parser.parse_known_args()

    kwargs = return_json_dictionary(args.json_file)

    try:
        main(
            input_file=args.input_file,
            job_name=args.job_name,
            model_name=args.model_name,
            cpus=args.cpus,
            **kwargs
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
