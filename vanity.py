import argparse
import json
from solders.keypair import Keypair  # type: ignore
import re
import sys
import base58
import signal
import multiprocessing
from multiprocessing import Process, Queue, cpu_count
import time
import os

def generate_vanity_address(pattern_compiled, queue, progress_queue, batch_size=10000):
    """
    Generates Solana keypairs and checks if the public key matches the desired pattern.
    If a match is found, it sends the result to the main process via the queue.
    """
    while True:
        attempts = 0
        for _ in range(batch_size):
            keypair = Keypair()
            pubkey = str(keypair.pubkey())
            attempts += 1

            if pattern_compiled.search(pubkey):
                vanity_address = {
                    "public_key": pubkey,
                    "secret_key": base58.b58encode(bytes(keypair)).decode("utf-8"),
                }
                queue.put(vanity_address)
                return  # Exit after finding a match

        progress_queue.put(attempts)  # Report progress for the batch


def progress_monitor(progress_queue, total_attempts):
    """
    Monitors and displays the progress of the vanity address generation process.
    """
    start_time = time.time()
    while True:
        attempts = progress_queue.get()
        if attempts == "DONE":
            break
        total_attempts.value += attempts
        elapsed_time = time.time() - start_time
        attempts_per_second = total_attempts.value / elapsed_time
        print(
            f"\rGenerated & Searched wallets: {total_attempts.value} | Speed: {attempts_per_second:.2f}/s",
            end="",
        )


def main(vanity_text, max_matches, ignore_case, match_end):
    """
    Main function to generate Solana vanity addresses based on the specified criteria.
    """
    pluralized = "es" if max_matches > 1 else ""
    filename = f"{vanity_text}-vanity-address{pluralized}.json"

    # Handle interrupt signals gracefully
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Prepend '^' if matching at the start, append '$' if matching at the end
    if match_end:
        pattern = f"{vanity_text}$"
    else:
        pattern = f"^{vanity_text}"

    # Compile the regex pattern
    pattern_compiled = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
    print(
        f"Searching for vanity: {vanity_text}, ignoring case: {'yes' if ignore_case else 'no'}, match end: {'yes' if match_end else 'no'}"
    )

    # Use multiprocessing to parallelize the search
    queue = Queue()  # For results
    progress_queue = Queue()  # For progress updates
    total_attempts = multiprocessing.Value("i", 0)  # Shared counter for total attempts

    # Start progress monitor
    progress_process = Process(target=progress_monitor, args=(progress_queue, total_attempts))
    progress_process.start()

    # Start worker processes
    num_cores = cpu_count()  # Use ALL CPU cores
    processes = []
    for _ in range(num_cores):
        p = Process(
            target=generate_vanity_address,
            args=(pattern_compiled, queue, progress_queue),
        )
        p.start()
        processes.append(p)

    found = 0
    results = []
    while found < max_matches:
        result = queue.get()
        results.append(result)
        found += 1
        print(f"\nMatch found: {result['public_key']}")

        if found >= max_matches:
            print("Found enough matches, exiting.")
            break

    # Clean up
    for p in processes:
        p.terminate()
    progress_queue.put("DONE")
    progress_process.join()

    # Save results to file (append if file exists)
    try:
        if os.path.exists(filename):
            with open(filename, "r") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Append new results to existing data
        existing_data.extend(results)

        # Save the updated data back to the file
        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)
    except Exception as e:
        print(f"Error saving results to file: {e}")
        sys.exit(1)

    print(f"Total Wallets Searched: {total_attempts.value}")


def signal_handler(sig, frame):
    """
    Handles interrupt signals (e.g., Ctrl+C) to exit the script gracefully.
    """
    print("\nExiting gracefully")
    sys.exit(0)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Vanity.py - Generate Vanity Solana Wallet addresses."
    )
    parser.add_argument(
        "--vanity-text",
        "--vanity",
        "-v",
        type=str,
        required=True,
        help="The text to search for in the wallet address.",
    )
    parser.add_argument(
        "--max-matches",
        "--max",
        "-m",
        type=int,
        default=1,
        help="The number of matches to find before exiting",
    )
    parser.add_argument(
        "--match-end",
        "--end",
        "-e",
        action="store_true",
        help="Match the vanity text at the end of the address instead of the beginning",
    )
    parser.add_argument(
        "--ignore-case",
        "--ignore",
        "-i",
        action="store_true",
        help="Ignore case in text matching",
    )
    args = parser.parse_args()

    # Start the main function
    main(args.vanity_text, args.max_matches, args.ignore_case, args.match_end)