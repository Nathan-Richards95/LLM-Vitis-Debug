import vitis
import constants
from pathlib import Path
import os
import sys
import shutil
import subprocess

class Vitis_Helper:
    def __init__(self, tc_name: str, mode: str, verbose: bool = True):
        # Necessary paths for x86 and hw build
        self.tc_dir = Path("Test_Cases") / tc_name                  #Path to the test case folder
        self.workspace_dir = self.tc_dir / "workspace"              #Path to the workspace where the build will happen
        self.mode_dir = self.tc_dir / mode                          #Path to the mode-specific directory (e.g. "llama" or "ref")
        self.broken_dir = self.tc_dir / "broken"                    #Path to the broken implementation (used for copying files and build setup)
        self.comp_dir = self.workspace_dir / f"aie_{mode}"          #Path to the component directory that will be created during setup and build

        # Settings
        self.verbose = verbose                                      #Whether to print verbose output during the build process     
        self.mode = mode                                            #Mode can be either "ref" for building the reference implementation, or the model name (e.g. "llama") for building the LLM-generated implementation

        # Relevant files (will be set during setup)
        self.host_file = None                                       #Path to the host file (copied from broken/shared)
        self.input_file = None                                      #Path to the input file (copied from broken/shared)
        self.kernel_file = None                                     #Path to the kernel file (copied from broken/shared)
        self.graph_file = None                                      #Path to the graph file (copied from ref or llm dir depending on mode)
        self.output_file = None                                     #Path to the output file (will be generated after build and simulation)

        # AIE Sim stuff
        self.client = None                                          #Vitis client object
        self.component_name = None                                  #Vitis AI Engine component object name
        self.aie_comp = None                                        #Vitis AI Engine component object (created during setup)

        # Call the setup function
        setup_success = self.setup()
        if not setup_success:
            print("Vitis_Helper setup failed. Please check the error messages above.")
            sys.exit(1)

    def validate_mode(self):
        # check that the mode is valid
        if self.mode not in constants.VALID_VITIS_MODES:
            print(f"Invalid mode: {self.mode}. Valid modes are: {constants.VALID_VITIS_MODES}")
            return False
        return True

    def create_directories(self):
        # Create workspace and create a new folder if the model name does not
        # exist in the test case. Copy from the broken folder
        print(f"Creating model directory: {self.mode_dir} and copying from broken directory: {self.broken_dir}")
        if not self.mode_dir.exists():
            shutil.copytree(self.broken_dir, self.mode_dir)

        if not self.workspace_dir.exists():
            self.workspace_dir.mkdir(parents=True, exist_ok=True)

    def create_component(self):
        # Set up component name and paths
        self.component_name = f"aie_{self.mode}"
        self.comp_dir = self.workspace_dir / self.component_name
        if self.comp_dir.exists():
            print(f"Component path {self.comp_dir} already exists. Removing it for a clean build.")
            shutil.rmtree(self.comp_dir)
        platform = os.environ.get("AIE_PLATFORM")
        if not platform:
            print(
                "AIE_PLATFORM environment variable is not set.\n"
                "Example:\n"
                "  export AIE_PLATFORM=/path/to/Xilinx_vek280_base_202410_1.xpfm"
            )
            return False
        template_errors = []
        templates = ["empty", "empty_aie_component"] #empty template is literally nothing, empty_aie_component has a bit for component setup
        for template_name in templates:
            try:
                self.aie_comp = self.client.create_aie_component(
                    name=self.component_name,
                    platform=platform,
                    template=template_name
                )
                break
            except Exception as e:
                template_errors.append((template_name, str(e)))
        if self.aie_comp is None:
            print("ERROR: Failed to create AI Engine component. Template errors:")
            for template_name, error in template_errors:
                print(f"Template '{template_name}': {error}")
            return False
        print(f'Created AI Engine component') if self.verbose else None
        return True

    def initialize_client(self):
        # Create the vitis client
        self.client = vitis.create_client()
        self.client.set_workspace(path=str(self.workspace_dir))

    def set_file_paths(self):
        # Set the relavent files paths
        self.host_file = self.mode_dir / "host.cpp"
        self.input_file = self.mode_dir / "input.txt"
        self.kernel_file = self.mode_dir / "kernel.cpp"
        self.graph_file = self.mode_dir / "graph.cpp"
        self.output_file = self.mode_dir / "output.txt"

    def import_files(self):
         # Import the source files into the component
        from_loc = str(self.tc_dir)
        files_to_import = [self.mode]
        self.aie_comp.import_files(from_loc=from_loc, files=files_to_import)
        print(f"Imported source tree pieces: {files_to_import}") if self.verbose else None

    def configure_component(self):
        # Set the config file if it exists in the test case
        cfg_file = self.tc_dir / "shared" / "aiecompiler.cfg"
        if cfg_file.exists():
            try:
                self.aie_comp.remove_cfg_file("aiecompiler.cfg")
                print("Removed tool-generated aiecompiler.cfg") if self.verbose else None
            except Exception:
                print("No tool-generated aiecompiler.cfg removed (this is okay).") if self.verbose else None

            self.aie_comp.add_cfg_file(str(cfg_file))
            print(f"Added custom aiecompiler.cfg: {cfg_file}") if self.verbose else None
        else:
            print("No aiecompiler.cfg found; continuing without one.") if self.verbose else None
        # Set the top file as the graph
        top_file = f'{self.mode}/graph.cpp'
        self.aie_comp.update_top_level_file(top_file)
        print(f"Set top-level file to: {top_file}") if self.verbose else None

    def setup(self):
        if not self.validate_mode(): return False
        self.create_directories()
        self.initialize_client()
        if not self.create_component(): return False
        self.set_file_paths()
        self.import_files()
        self.configure_component()
        return True

    def build_component_x86(self):
        # Build the x86 component using Vitis       
        print("\n Building x86sim...") if self.verbose else None
        try:
            x86_build_success = False
            print("Building x86sim...")
            self.aie_comp.build(target="x86sim")
        except Exception as e:
            print(f"x86sim build failed: {e}")
            try:
                print(self.aie_comp.get_report())
            except Exception:
                pass
            return x86_build_success
        build_success = True
        print("x86sim build complete.\n") if self.verbose else None
        return build_success

    def run_x86_sim(self):
        x86_sim_success = False
        try:
            x86_sim_dir = self.workspace_dir / self.component_name / "build" / "x86sim"
            data_dir = x86_sim_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            src_file = self.input_file
            dst_file_x86 = data_dir / "PhaseIn_0.txt"
            if not src_file.exists():
                print(f"Error: Expected source file {src_file} not found after x86sim build.")
                return False
            shutil.copy(src_file, dst_file_x86)
            print(f"Copied x86sim input to: {dst_file_x86}") if self.verbose else None
            print("Running x86sim executable...") if self.verbose else None
            subprocess.run(
                ["x86simulator"],
                cwd = x86_sim_dir,
                check = True
            )
            output_target = self.tc_dir / self.mode / "output.txt"   
            x86_sim_output = x86_sim_dir / "x86simulator_output" / "data" / "Output_0.txt"
            if not x86_sim_output.exists():
                print(f"Error: Expected x86sim output file {x86_sim_output} not found after simulation.")
                return False
            shutil.copy(x86_sim_output, output_target)
            print(f"Copied x86sim output to: {output_target}") if self.verbose else None    
            print("x86sim execution complete.") if self.verbose else None
        except Exception as e:
            print(f"x86sim execution failed: {e}")
            return x86_sim_success
        x86_sim_success = True
        return x86_sim_success

    def build_component_hw(self):
        print("Building hardware...") if self.verbose else None
        hw_build_success = False
        try:
            self.aie_comp.build(target="hw")
        except Exception as e:
            print(f"Hardware build failed: {e}")
            return hw_build_success
        print("Hardware build complete.") if self.verbose else None
        return hw_build_success

    def run_hw_sim(self):
        hw_sim_success = False
        try:
            src_file = self.input_file
            hw_build_dir = self.workspace_dir / self.component_name / "build" / "hw"
            data_dir = hw_build_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            dst_file_hw = data_dir / "PhaseIn_0.txt"
            shutil.copy(src_file, dst_file_hw)
            print(f"Copied hardware build input to: {dst_file_hw}") if self.verbose else None
            subprocess.run(
                ["aiesimulator", "--profile"],
                cwd = hw_build_dir,
                check = True
            )
            print("\nComponent Report:")
            try:
                print(self.aie_comp.get_report())
            except Exception:
                print("Report call did not return printable output, but builds may still have succeeded.")
            print("\nDone.")
            print(f"Check outputs under: {self.workspace_dir / self.component_name}")
        except Exception as e:
            print(f"Hardware simulation failed: {e}")
            return hw_sim_success
        hw_sim_success = True
        return hw_sim_success

    def run_full_pipeline(self):
        x86_build_success = self.build_component_x86()
        x86_sim_success = self.run_x86_sim()
        hw_build_success = self.build_component_hw()
        hw_sim_success = self.run_hw_sim()
        return {
            "x86_build_success": x86_build_success,
            "x86_sim_success": x86_sim_success,
            "hw_build_success": hw_build_success,
            "hw_sim_success": hw_sim_success
        }
