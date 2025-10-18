import os
import shutil
import sys
import glob
import subprocess
import inspect
import importlib


def find_protoc():
    protoc = None
    if "PROTOC" in os.environ and os.path.exists(os.environ["PROTOC"]):
        protoc = os.environ["PROTOC"]
    else:
        protoc = shutil.which("protoc")

    if protoc is None:
        sys.stderr.write(
            "protobuf-compiler cannot be found. Please make sure that it is installed. \
                    Or set the PROTOC environment variable to the path of the protoc binary.\n"
        )
        sys.exit(1)
    return protoc


def compile_protos(output_dir: str):
    protoc = find_protoc()

    # Get a list of all .proto files in the directory
    proto_files = glob.glob(f"{output_dir}/mlens_proto/*.proto")

    print(f"Found {len(proto_files)} proto files to compile.")

    protoc_cmd_npm = [
        protoc,
        "--proto_path=.",
        f"--js_out=import_style=commonjs,binary:{output_dir}",
    ]

    # Compile the protos
    print("Compiling protos for python:")
    for proto_file in proto_files:
        protoc_cmd_npm.append(proto_file)
        try:
            subprocess.run(
                [
                    protoc,
                    f"--proto_path={output_dir}",
                    f"--mypy_out={output_dir}",
                    f"--python_out={output_dir}",
                    proto_file,
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error compiling proto file {proto_file}: {e}")
            sys.exit(1)

    print("Compiling protos for js:")
    try:
        subprocess.run(
            protoc_cmd_npm,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error compiling proto file for js: {e}")
        sys.exit(1)


def generate_init(output_dir: str):
    print("Generating __init__.py:")
    mlens_proto_dir = os.path.join(output_dir, "mlens_proto")
    sys.path.insert(0, output_dir)
    try:
        with open(os.path.join(mlens_proto_dir, "__init__.py"), "w") as f:
            for filename in os.listdir(mlens_proto_dir):
                if filename.endswith("_pb2.py"):
                    module_name = filename[:-3]  # Remove .py extension
                    module = importlib.import_module(f"mlens_proto.{module_name}")
                    classes = [
                        m[0]
                        for m in inspect.getmembers(module, inspect.isclass)
                        if m[1].__module__ == module.__name__
                    ]
                    for cls in classes:
                        f.write(f"from .{module_name} import {cls}\n")
    except Exception as e:
        print(f"Error generating __init__.py: {e}")
        sys.exit(1)
    finally:
        sys.path.pop(0)


def generate_index_js(output_dir: str):
    print("Generating index.js:")
    try:
        # Extract class names from js files
        proto_classes = []
        proto_files = glob.glob(f"{output_dir}/mlens_proto/*_pb.js")

        for proto_file in proto_files:
            filename = os.path.basename(proto_file)
            module_name = filename[:-3]  # Remove .js extension
            base_name = module_name.replace("_pb", "")

            with open(proto_file, "r") as f:
                content = f.read()
                for line in content.split("\n"):
                    # Match export lines for our package, e.g., proto.mlens.v1.ClassName
                    if line.startswith("goog.exportSymbol('proto.mlens.v1."):
                        class_name = line.split("'")[1].split(".")[-1]
                        proto_classes.append((class_name, module_name))

        # Group classes by their module to create concise requires
        modules = {}
        for cls, mod in proto_classes:
            modules.setdefault(mod, []).append(cls)

        # Generate the index.js file with CommonJS requires and exports
        with open(f"{output_dir}/mlens_proto/index.js", "w") as f:
            # Requires grouped per module
            for module_name, classes in modules.items():
                class_list = ", ".join(sorted(set(classes)))
                f.write(f"const {{ {class_list} }} = require('./{module_name}');\n")

            f.write("\n")

            # Aggregate exports
            all_class_names = [cls for cls, _ in proto_classes]
            # Preserve order but remove duplicates
            seen = set()
            unique_classes = []
            for c in all_class_names:
                if c not in seen:
                    seen.add(c)
                    unique_classes.append(c)

            f.write("module.exports = {\n")
            f.write("  " + ", ".join(unique_classes) + "\n")
            f.write("};\n")

        print("Generated index.js successfully with ES module format.")
    except Exception as e:
        print(f"Error generating index.js: {e}")
        sys.exit(1)


def generate_stubs(output_dir: str):
    print("Generating stubs:")
    stubgen = shutil.which("stubgen")
    if stubgen is None:
        print("Error: stubgen not found.")
        sys.exit(1)
    cwd = os.getcwd()
    os.chdir(output_dir)
    try:
        subprocess.run(
            [
                stubgen,
                "-o",
                ".",
                "--no-import",
                "-m",
                "mlens_proto",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error generating stubs: {e}")
        sys.exit(1)
    os.chdir(cwd)


def main():
    output_dir = "."
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    compile_protos(output_dir)
    generate_init(output_dir)
    generate_stubs(output_dir)
    generate_index_js(output_dir)


if __name__ == "__main__":
    main()
