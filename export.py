import argparse
import json
import pathlib
import subprocess
import yaml

parser = argparse.ArgumentParser(
    prog="export", description="Conan recipe export helper"
)
parser.add_argument("package", nargs="*")
args = parser.parse_args()

with open("mercs_deps.json", "r", encoding="utf-8") as f:
    for dep in json.load(f):
        name = dep["name"]
        if args.package and name not in args.package:
            continue
        version = dep["version"]
        recipe_config_dir = pathlib.Path("recipes") / name
        recipe_config = recipe_config_dir / "config.yml"
        with recipe_config.open() as config_file:
            config = yaml.safe_load(config_file)
            version_data = config["versions"].get(version)
            if version_data is None:
                raise Exception(f"Could not find version {version} for package {name}")
            recipe = recipe_config_dir / version_data["folder"]
            subprocess.run(["conan", "export", str(recipe), f"{name}/{version}@"])
