#!/usr/bin/env python3
"""
Test the AI inference node

Quick test to verify everything is working
"""

import asyncio
from client import InferenceClient


async def main():
    print("🧪 Testing AI Inference Node")
    print("=" * 50)
    print()

    async with InferenceClient(requester_id="test-client") as client:
        # Test 1: Discover nodes
        print("1. Discovering inference nodes...")
        nodes = await client.discover_nodes()
        print(f"   Found {len(nodes)} node(s): {nodes}")
        print()

        if not nodes:
            print("❌ No nodes found! Start one with: ./start_inference_node.sh")
            return

        # Test 2: Check node status
        print("2. Checking node status...")
        for node in nodes:
            status = await client.get_node_status(node)
            if status:
                print(f"   ✓ {node}")
                print(f"     Backend: {status['backend']}")
                print(f"     Models: {', '.join(status['available_models'][:3])}")
                print(f"     Load: {status['current_load']}/{status['max_concurrent']}")
        print()

        # Test 3: Simple inference
        print("3. Testing simple inference...")
        prompt = "What is mutual aid? Answer in one sentence."
        print(f"   Prompt: {prompt}")

        response = await client.infer(prompt, temperature=0.7)
        print(f"   Response: {response}")
        print()

        # Test 4: System prompt
        print("4. Testing with system prompt...")
        response = await client.infer(
            prompt="Analyze this offer: 'I have 10kg of fresh tomatoes to share'",
            system_prompt="You are a helpful assistant for a gift economy platform. Be concise.",
            temperature=0.5,
        )
        print(f"   Response: {response}")
        print()

        print("✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
