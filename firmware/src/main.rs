
cat > src/main.rs << 'EOF'
#![no_std]
#![no_main]

use riscv_rt::entry;

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}

#[entry]
fn main() -> ! {
    loop {}
}
EOF