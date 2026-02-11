#!/usr/bin/env python3
import sys
import argparse
from aws_setup import AWSEnvironment
from agent import initialize_chatbot, run_agent_interactive

def main():
    parser = argparse.ArgumentParser(description="AWS Chatbot")
    parser.add_argument('--mock', action='store_true', help='Use mock AWS environment')
    args = parser.parse_args()

    # Determine whether to use mock AWS environment
    use_mock_aws = args.mock
    environment_name = "Mock AWS (Moto)" if use_mock_aws else "AWS"

    print(f"Starting chatbot with {environment_name} environment...\n")

    # Initialize AWS environment
    with AWSEnvironment(use_moto=use_mock_aws):
        chatbot = initialize_chatbot(use_mock=use_mock_aws)
        if chatbot is None:
            print("Failed to initialize chatbot. Exiting.")
            sys.exit(1)
        
        try:
            run_agent_interactive(chatbot, environment_name)
        except KeyboardInterrupt:
            print("\nChatbot session ended by user.")
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()