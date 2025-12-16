#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

// Wasm3 headers
#include "wasm3.h"
#include "m3_env.h"

typedef struct {
    IM3Environment env;
    IM3Runtime runtime;
    IM3Module module;
    IM3Function heartbeat_func;
    uint8_t wasm_heap[8192];
} WasmContext;

// UART write function (emulated)
void uart_write(const char* data, size_t len) {
    // This will be intercepted by Renode or hardware UART
    for(size_t i = 0; i < len; i++) {
        *(volatile uint32_t*)0x10013000 = (uint8_t)data[i];
    }
}

// Initialize Wasm context, parse and load the module, and locate "heartbeat" function.
WasmContext* wasm_init(const uint8_t* wasm_binary, size_t wasm_size) {
    if (!wasm_binary || wasm_size == 0) return NULL;

    WasmContext* ctx = (WasmContext*)calloc(1, sizeof(WasmContext));
    if (!ctx) return NULL;

    ctx->env = m3_NewEnvironment();
    if (!ctx->env) {
        free(ctx);
        return NULL;
    }

    // Create runtime with a stack and the provided wasm heap
    M3Result result = m3_NewRuntime(&ctx->runtime, ctx->env, sizeof(ctx->wasm_heap));
    if (result != m3Err_none) {
        m3_FreeEnvironment(ctx->env);
        free(ctx);
        return NULL;
    }

    // Parse and load module
    result = m3_ParseModule(ctx->env, &ctx->module, wasm_binary, (uint32_t)wasm_size);
    if (result != m3Err_none) {
        m3_FreeRuntime(ctx->runtime);
        m3_FreeEnvironment(ctx->env);
        free(ctx);
        return NULL;
    }

    result = m3_LoadModule(ctx->runtime, ctx->module);
    if (result != m3Err_none) {
        m3_FreeModule(ctx->module);
        m3_FreeRuntime(ctx->runtime);
        m3_FreeEnvironment(ctx->env);
        free(ctx);
        return NULL;
    }

    // Find the exported function "heartbeat" (module name NULL to search default)
    result = m3_FindFunction(&ctx->heartbeat_func, ctx->runtime, "heartbeat");
    if (result != m3Err_none) {
        // If function not found, still keep module loaded but mark func as NULL
        ctx->heartbeat_func = NULL;
    }

    return ctx;
}

// Execute the heartbeat function with device_id and uptime arguments, and write the returned JSON to UART.
void wasm_execute_heartbeat(WasmContext* ctx, uint32_t device_id, uint64_t uptime) {
    if (!ctx || !ctx->heartbeat_func) return;

    char device_id_str[12];
    char uptime_str[22];
    const char* args[2];

    snprintf(device_id_str, sizeof(device_id_str), "%u", device_id);
    snprintf(uptime_str, sizeof(uptime_str), "%llu", (unsigned long long)uptime);

    args[0] = device_id_str;
    args[1] = uptime_str;

    M3Result result = m3_Call(ctx->heartbeat_func, 2, args);
    if (result != m3Err_none) {
        // call failed; nothing to do
        return;
    }

    const char* json_result = NULL;
    m3_GetResults(ctx->heartbeat_func, &json_result, 1);
    if (json_result) {
        uart_write(json_result, strlen(json_result));
    }
}

// Cleanup wasm context and free all resources.
void wasm_cleanup(WasmContext* ctx) {
    if (!ctx) return;
    if (ctx->module) m3_FreeModule(ctx->module);
    if (ctx->runtime) m3_FreeRuntime(ctx->runtime);
    if (ctx->env) m3_FreeEnvironment(ctx->env);
    free(ctx);
}