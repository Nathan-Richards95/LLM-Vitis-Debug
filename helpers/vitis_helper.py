import vitis
import constants

class Vitis_Helper:
    def __init__(self, tc_name: str, model_name: str, verbose: bool = True):
        self.tc_path = Path("Test_cases") / tc_name
        self.workspace = self.tc_path / "workspace"
        self.shared_dir = self.tc_path / "shared"
        self.ref_dir = self.tc_path / "ref"
        self.llm_dir = self.tc_path / f'{model_name}'
        self.verbose = verbose

        self.host_file = self.shared_dir / "host.cpp"
        self.input_file = self.shared_dir / "input.txt"

    #mode can be either "ref", or "<model_name>" (e.g. "llama")
    def build_project(self, mode: str):
        # Build the project using Vitis
        if mode not in constants.VALID_VITIS_MODES:
            print(f"Invalid mode: {mode}. Valid modes are: {constants.VALID_VITIS_MODES}")
            return False
        kernel_file = self.tc_path / mode / "ref.cpp"
        graph_file = self.tc_path / mode / "graph.cpp"

        self.workspace.mkdir(parents=True, exist_ok=True)

        client = vitis.create_client()
        client.set_workspace(path=str(self.workspace))

        component_name = f"aie_{mode}"

        comp_path = self.workspace / component_name
        if comp_path.exists():
            print(f"Component path {comp_path} already exists. Removing it for a clean build.")
            shutil.rmtree(comp_path)

        aie_comp = None
        template_errors = []

        for template_name in ["empty", "empty_aie_component"]:
            try:
                aie_comp = client.create_aie_component(
                    name=component_name,
                    platform=constants.FPGA_PART,
                    template=template_name
                )
                break
            except Exception as e:
                template_errors.append((template_name, str(e)))
        
        if aie_comp is None:
            print("ERROR: Failed to create AI Engine component. Template errors:")
            for template_name, error in template_errors:
                print(f"Template '{template_name}': {error}")
            return False

        print(f'Created AI Engine component') if self.verbose else None
        files_to_import = ["shared", kernel_file, graph_file]

        print(f"Importing source tree pieces: {files_to_import}") if self.verbose else None
        aie_comp.import_files(from_loc=str(case_root), files=files_to_import)

        # optional config file
        cfg_file = self.tc_path / "aiecompiler.cfg"
        if cfg_file.exists():
            try:
                aie_comp.remove_cfg_file("aiecompiler.cfg")
                print("Removed tool-generated aiecompiler.cfg") if self.verbose else None
            except Exception:
                print("No tool-generated aiecompiler.cfg removed (this is okay).") if self.verbose else None

            aie_comp.add_cfg_file(str(cfg_file))
            print(f"Added custom aiecompiler.cfg: {cfg_file}") if self.verbose else None
        else:
            print("No aiecompiler.cfg found; continuing without one.") if self.verbose else None

        top_file = f'{mode}/graph.cpp'
        aie_comp.update_top_level_file(top_file)
        print(f"Set top-level file to: {top_file}") if self.verbose else None

        print("\n Building x86sim...") if self.verbose else None
        aie_comp.build(target="x86sim", clean=True)
        print("x86sim build complete.\n") if self.verbose else None

        x86_sim_dir = self.workspace / component_name / "build" / "x86sim"
        data_dir = x86_sim_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        src_file = self.input_file
        dst_file = datra_dir / "PhaseIn_0.txt"
        if not src_file.exists():
            print(f"Error: Expected source file {src_file} not found after x86sim build.")
            return False

        shutil.copy(src_file, dst_file)
        print(f"Copied x86sim input to: {dst_file}") if self.verbose else None

        print("Running x86sim executable...") if self.verbose else None
        subprocess.run(
            ["x86simulator"],
            cwd = x86_sim_dir,
            check = True
        )
        ouput_target = self.tc_path / mode / "output.txt"   
        x86_sim_output = x86_sim_dir / "x86simulator_output" / "data" / "Output_0.txt"
        if not x86_sim_output.exists():
            print(f"Error: Expected x86sim output file {x86_sim_output} not found after simulation.")
            return False
        shutil.copy(x86_sim_output, output_target)
        print(f"Copied x86sim output to: {output_target}") if self.verbose else None    
        print("x86sim execution complete.") if self.verbose else None

        print("Building hardware...") if self.verbose else None
        aie_comp.build(target="hw")
        print("Hardware build complete.") if self.verbose else None

        print("\nComponent Report:")
        try:
            print(aie_comp.get_report())
        except Exception:
            print("Report call did not return printable output, but builds may still have succeeded.")

        print("\nDone.")
        print(f"Check outputs under: {workspace / component_name}")
