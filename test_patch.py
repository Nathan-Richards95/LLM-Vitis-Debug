import constants
import helpers.general_helper as general_helper
from pathlib import Path

patch = """diff --git a/vector_add.cpp
index 9c04634..0e208af 100644
--- a/vector_add.cpp
+++ b/vector_add.cpp
@@ -5,7 +5,7 @@ void vector_add(
     input_window<int32_t>* in1,
     output_window<int32_t>* out
 ) {
-    for (int i = 0; i < VECTOR_SIZE; i++) {
+    for (int idx = 0; idx < VECTOR_SIZE; idx++) {
         int32_t a = window_readincr(in0);
         int32_t b = window_readincr(in1);
         window_writeincr(out, a + b); 
"""

if __name__ == "__main__":
    tc_path = Path("Test_Cases/Debug002")
    model_type = "test_git_patch"
    general_helper.apply_git_patch(tc_path, model_type, patch)