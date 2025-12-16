use std::env;
use std::path::PathBuf;
use cc::Build;

fn main() {
    // Build Wasm3 C runtime
    let mut build = Build::new();
    
    // Add Wasm3 source files
    let wasm3_dir = PathBuf::from("../wasm3/source");
    
    build
        .include(&wasm3_dir)
        .file("../wasm3/source/wasm3.c")
        .file("../wasm3/source/m3_api_libc.c")
        .file("../wasm3/source/m3_api_uvwasi.c")
        .file("../wasm3/source/m3_api_wasi.c")
        .file("../wasm3/source/m3_bind.c")
        .file("../wasm3/source/m3_code.c")
        .file("../wasm3/source/m3_compile.c")
        .file("../wasm3/source/m3_core.c")
        .file("../wasm3/source/m3_env.c")
        .file("../wasm3/source/m3_exec.c")
        .file("../wasm3/source/m3_function.c")
        .file("../wasm3/source/m3_info.c")
        .file("../wasm3/source/m3_module.c")
        .file("../wasm3/source/m3_parse.c")
        .flag("-O3")
        .compile("wasm3");
    
    println!("cargo:rerun-if-changed=../wasm3/source");
}