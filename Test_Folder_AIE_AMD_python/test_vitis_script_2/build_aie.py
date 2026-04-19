#!/usr/bin/env python3
import os
import sys
import shutil
from pathlib import Path

try:
    import vitis
except ImportError:
    print("ERROR: Could not import 'vitis'.")
    print("Make sure you sourced the Vitis environment first, for example:")
    print("  source /path/to/Vitis/settings64.sh")
    sys.exit(1)


VALID_MODES = {"ref", "llm", "broken"}


def fail(msg: str):
    print(f"ERROR: {msg}")
    sys.exit(1)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in VALID_MODES:
        print("Usage:")
        print(f"  {sys.argv[0]} <ref|llm|broken>")
        sys.exit(1)

    mode = sys.argv[1]

    root = Path(__file__).resolve().parent
    case_root = Path("Test_Cases/Debug001")
    workspace = root / "py_workspace"

    shared_dir = case_root / "shared"
    ref_dir = case_root / "ref"
    llm_dir = case_root / "llm_output"

    graph_file = shared_dir / "graph.cpp"
    host_file = shared_dir / "host.cpp"        # not used in AIE component build
    broken_file = shared_dir / "broken.cc"
    ref_file = ref_dir / "ref.cc"
    llm_file = llm_dir / "llm_out.cpp"
    cfg_file = case_root / "aiecompiler.cfg"   # optional

    platform = os.environ.get("AIE_PLATFORM")
    if not platform:
        fail(
            "AIE_PLATFORM environment variable is not set.\n"
            "Example:\n"
            "  export AIE_PLATFORM=/path/to/Xilinx_vek280_base_202410_1.xpfm"
        )

    if not case_root.exists():
        fail(f"Case folder not found: {case_root}")
    if not shared_dir.exists():
        fail(f"Shared folder not found: {shared_dir}")
    if not graph_file.exists():
        fail(f"Top-level graph file not found: {graph_file}")

    # Select candidate source for this build
    if mode == "ref":
        selected_source = ref_file
    elif mode == "llm":
        selected_source = llm_file
    else:
        selected_source = broken_file

    if not selected_source.exists():
        fail(f"Selected source file not found for mode '{mode}': {selected_source}")

    print(f"Mode        : {mode}")
    print(f"Workspace   : {workspace}")
    print(f"Case root   : {case_root}")
    print(f"Graph file  : {graph_file}")
    print(f"Source file : {selected_source}")
    print(f"Platform    : {platform}")
    print(f"CFG file    : {cfg_file if cfg_file.exists() else '(none)'}")

    workspace.mkdir(parents=True, exist_ok=True)

    client = vitis.create_client()
    client.set_workspace(path=str(workspace))

    component_name = f"aie_debug001_{mode}"

    # If component already exists in workspace, remove its folder first to avoid stale imports
    comp_path = workspace / component_name
    if comp_path.exists():
        print(f"Removing existing component folder: {comp_path}")
        shutil.rmtree(comp_path)

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

    # Import only the files/folders this AIE component actually needs.
    #
    # We import from case_root so relative paths inside the case stay stable.
    # Imported files/folders are copied into the component folder in the workspace.
    # AMD documents import_files(from_loc=..., files=[...]) for this use. :contentReference[oaicite:4]{index=4}
    files_to_import = ["shared"]

    # Add only the active source folder or file for this build
    if mode == "ref":
        files_to_import.append("ref")
    elif mode == "llm":
        files_to_import.append("llm_output")
    else:
        # broken.cc is already inside shared
        pass

    print(f"Importing source tree pieces: {files_to_import}")
    aie_comp.import_files(from_loc=str(case_root), files=files_to_import)

    # Optional config file
    if cfg_file.exists():
        try:
            aie_comp.remove_cfg_file("aiecompiler.cfg")
            print("Removed tool-generated aiecompiler.cfg")
        except Exception:
            print("No tool-generated aiecompiler.cfg removed (this is okay).")

        aie_comp.add_cfg_file(str(cfg_file))
        print(f"Added custom aiecompiler.cfg: {cfg_file}")
    else:
        print("No aiecompiler.cfg found; continuing without one.")

    # Top-level file path should be relative to the imported component contents.
    # Since we imported 'shared', graph.cpp should live at shared/graph.cpp in the component.
    top_file = "shared/graph.cpp"
    aie_comp.update_top_level_file(top_file)
    print(f"Set top-level file to: {top_file}")

    print("\nBuilding x86sim...")
    aie_comp.build(target="x86sim")
    print("x86sim build complete.")

    print("\nBuilding hw...")
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