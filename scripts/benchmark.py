
#!/usr/bin/env python3
"""
Performance Benchmarking Script for Splunk MCP Server
Tests various aspects of the MCP server performance
"""

import asyncio
import time
import statistics
import json
import os
from typing import Dict, List, Any
from fastmcp import Client
from src.splunk_mcp.main import mcp

class PerformanceBenchmark:
    """Performance benchmarking suite"""
    
    def __init__(self):
        self.results = {}
        self.client = None
        
    async def __aenter__(self):
        self.client = Client(mcp)
        await self.client.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def benchmark_tool_call(self, tool_name: str, args: Dict[str, Any], iterations: int = 10) -> Dict[str, Any]:
        """Benchmark a specific tool call"""
        times = []
        errors = 0
        
        for i in range(iterations):
            start_time = time.time()
            try:
                await self.client.call_tool(tool_name, args)
                end_time = time.time()
                times.append(end_time - start_time)
            except Exception as e:
                errors += 1
                print(f"Error in iteration {i+1}: {e}")
        
        if times:
            return {
                "tool": tool_name,
                "iterations": iterations,
                "errors": errors,
                "avg_time": statistics.mean(times),
                "min_time": min(times),
                "max_time": max(times),
                "median_time": statistics.median(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
        else:
            return {
                "tool": tool_name,
                "iterations": iterations,
                "errors": errors,
                "avg_time": None,
                "min_time": None,
                "max_time": None,
                "median_time": None,
                "std_dev": None
            }
    
    async def benchmark_health_check(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark health check endpoint"""
        return await self.benchmark_tool_call("mcp_health_check", {}, iterations)
    
    async def benchmark_list_indexes(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark list indexes tool"""
        return await self.benchmark_tool_call("list_indexes", {}, iterations)
    
    async def benchmark_splunk_search(self, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark splunk search tool"""
        query = "search index=_internal | head 10"
        return await self.benchmark_tool_call("splunk_search", {"query": query}, iterations)
    
    async def benchmark_itsi_services(self, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark ITSI services tool"""
        return await self.benchmark_tool_call("get_itsi_services", {}, iterations)
    
    async def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all available benchmarks"""
        print("Starting performance benchmarks...")
        
        benchmarks = [
            ("health_check", self.benchmark_health_check),
            ("list_indexes", self.benchmark_list_indexes),
            ("splunk_search", self.benchmark_splunk_search),
            ("itsi_services", self.benchmark_itsi_services),
        ]
        
        results = {}
        
        for name, benchmark_func in benchmarks:
            print(f"Running {name} benchmark...")
            try:
                result = await benchmark_func()
                results[name] = result
                print(f"✓ {name}: {result['avg_time']:.3f}s avg ({result['iterations']} iterations)")
            except Exception as e:
                print(f"✗ {name}: Failed - {e}")
                results[name] = {"error": str(e)}
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = "benchmark_results.json"):
        """Save benchmark results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")

async def main():
    """Main benchmarking function"""
    print("Splunk MCP Server Performance Benchmark")
    print("=" * 50)
    
    # Check if Splunk credentials are available
    if not os.getenv("SPLUNK_TOKEN"):
        print("⚠️  Warning: SPLUNK_TOKEN not set. Some benchmarks may fail.")
    
    async with PerformanceBenchmark() as benchmark:
        results = await benchmark.run_all_benchmarks()
        benchmark.save_results(results)
        
        # Print summary
        print("\n" + "=" * 50)
        print("Benchmark Summary")
        print("=" * 50)
        
        for name, result in results.items():
            if "error" in result:
                print(f"{name}: ERROR - {result['error']}")
            elif result.get("avg_time"):
                print(f"{name}: {result['avg_time']:.3f}s avg ({result['iterations']} iterations)")
            else:
                print(f"{name}: No successful iterations")

if __name__ == "__main__":
    asyncio.run(main())