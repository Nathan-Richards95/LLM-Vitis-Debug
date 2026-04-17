
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

try:
    import vitis
except ImportError:
    print("ERROR: Could not import 'vitis'.")
    print("Make sure you sourced the Vitis environment first, for example:")
    print("  source /data/courses/class_cse494598cen571spring2026_aaror112/Vitis_2024_1/Vitis/2024.1/settings64.sh")
    sys.exit(1)


def main():
    root = Path(__file__).resolve().parent
    workspace = root / "py_workspace"
    source_root = root / "lab4" / "src"
    cfg_file = root / "aiecompiler.cfg"
    top_file = "lab4/src/aie_top_all.cpp"

    # Change this if your platform lives somewhere else.
    # Replace with the exact .xpfm path on your machine.
    platform = os.environ.get("AIE_PLATFORM")
    if not platform:
        print("ERROR: AIE_PLATFORM environment variable is not set.")
        print("Example:")
        print("  export AIE_PLATFORM=/path/to/Xilinx_vek280_base_202410_1.xpfm")
        sys.exit(1)

    if not source_root.exists():
        print(f"ERROR: Source folder not found: {source_root}")
        sys.exit(1)

    if not cfg_file.exists():
        print(f"ERROR: Config file not found: {cfg_file}")
        sys.exit(1)

    print(f"Workspace   : {workspace}")
    print(f"Source root : {source_root}")
    print(f"Config file : {cfg_file}")
    print(f"Platform    : {platform}")

    workspace.mkdir(parents=True, exist_ok=True)

    client = vitis.create_client()
    client.set_workspace(path=str(workspace))

    component_name = "aie_exp3_py"

    # AMD docs show create_aie_component + build(target="x86sim"/"hw").
    # Template names can vary by Vitis release, so try the common ones.
    aie_comp = None
    template_errors = []

    for template_name in ["empty", "empty_aie_component"]:
        try:
            print(f"Trying template: {template_name}")
            aie_comp = client.create_aie_component(
                name=component_name,
                platform=platform,
                template=template_name
            )
            break
        except Exception as e:
            template_errors.append((template_name, str(e)))

    if aie_comp is None:
        print("ERROR: Failed to create AI Engine component.")
        for tpl, err in template_errors:
            print(f"  template={tpl}: {err}")
        sys.exit(1)

    print("Created AI Engine component.")

    # Import the entire lab4 folder so relative paths like lab4/src/... remain valid.
    print("Importing source tree...")
    aie_comp.import_files(from_loc=str(root), files=["lab4"])

    # If the tool generated a default cfg, remove it and use your custom cfg instead.
    # AMD documents remove_cfg_file(...) followed by add_cfg_file(...) for custom cfg usage.
    try:
        aie_comp.remove_cfg_file("aiecompiler.cfg")
        print("Removed tool-generated aiecompiler.cfg")
    except Exception:
        print("No tool-generated aiecompiler.cfg removed (this is usually okay).")

    aie_comp.add_cfg_file(str(cfg_file))
    print("Added custom aiecompiler.cfg")

    aie_comp.update_top_level_file(top_file)
    print(f"Set top-level file to: {top_file}")

    print("\nBuilding x86sim...")
    aie_comp.build(target="x86sim")
    print("x86sim build complete.")

    print("\nBuilding hw (used for aiesim/hardware-target build artifacts)...")
    aie_comp.build(target="hw")
    print("hw build complete.")

    print("\nComponent report:")
    try:
        print(aie_comp.report())
    except Exception:
        print("Report call did not return printable output, but builds may still have succeeded.")

    print("\nDone.")
    print(f"Check outputs under: {workspace / component_name}")


if __name__ == "__main__":
    main()
