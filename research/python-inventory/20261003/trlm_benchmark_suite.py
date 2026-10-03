import ctypes
import numpy as np
import time
import os
import sys

class TRLM_AutomatedBenchmarkMatrix:
    def __init__(self, iterations=5000, seq_len=128, dim=64):
        self.iterations = iterations
        self.seq_len = seq_len
        self.dim = dim
        self.lib_path = "./libggml_trlm.so"
        self.lib = None
        np.random.seed(42)
        self.mock_k_stream = [np.random.normal(0, 0.1, self.dim).astype(np.float32) for _ in range(self.iterations)]
        self.mock_v_stream = [np.random.normal(0, 0.1, self.dim).astype(np.float32) for _ in range(self.iterations)]

    def _setup_ffi_bindings(self):
        """Compiles and links the un-mangled native C API gateway."""
        if not os.path.exists(self.lib_path):
            print(f"[BENCHMARK-ERROR] Shared object binary '{self.lib_path}' not discovered.")
            sys.exit(1)
        self.lib = ctypes.CDLL(self.lib_path)
        self.lib.trlm_create_edge_context.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.trlm_create_edge_context.restype = ctypes.c_void_p
        self.lib.trlm_destroy_edge_context.argtypes = [ctypes.c_void_p]
        self.lib.trlm_destroy_edge_context.restype = None
        self.lib.trlm_prepend_token_data.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
        self.lib.trlm_prepend_token_data.restype = ctypes.c_int

    def run_raw_python_benchmark(self) -> float:
        """Simulates an explicit right-to-left attention cache using native Python arrays."""
        python_k_cache = []
        python_v_cache = []
        start_clock = time.perf_counter()
        for idx in range(self.iterations):
            k_token = self.mock_k_stream[idx]
            v_token = self.mock_v_stream[idx]
            python_k_cache.insert(0, k_token)
            python_v_cache.insert(0, v_token)
            if len(python_k_cache) > self.seq_len:
                cutoff = int(self.seq_len * 0.376)
                python_k_cache = python_k_cache[:cutoff]
                python_v_cache = python_v_cache[:cutoff]
        stop_clock = time.perf_counter()
        return stop_clock - start_clock

    def run_native_ffi_benchmark(self) -> float:
        """Streams arrays directly into the pre-allocated C++ static memory arena."""
        self._setup_ffi_bindings()
        ctx_handle = self.lib.trlm_create_edge_context(self.seq_len, 47)
        start_clock = time.perf_counter()
        for idx in range(self.iterations):
            k_token = self.mock_k_stream[idx]
            v_token = self.mock_v_stream[idx]
            k_ptr = k_token.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            v_ptr = v_token.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            self.lib.trlm_prepend_token_data(ctx_handle, k_ptr, v_ptr)
        stop_clock = time.perf_counter()
        self.lib.trlm_destroy_edge_context(ctx_handle)
        return stop_clock - start_clock
