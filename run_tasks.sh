#!/bin/bash

# Function to install dependencies
install_dependencies() {
  echo "Installing dependencies..."
  sudo apt-get update
  sudo apt-get install -y python3 python3-pip golang-go
  pip3 install --upgrade pip
  pip3 install telebot flask pymongo aiohttp python-telegram-bot aiogram pyTelegramBotAPI psutil motor
}

# Function to verify Go installation
verify_go() {
  echo "Verifying Go installation..."
  go version
}

# Function to tidy Go modules
go_mod_tidy() {
  echo "Running 'go mod tidy'..."
  go mod tidy
}

# Function to build Go binary
build_go_binary() {
  echo "Building Go binary..."
  go build -ldflags="-w -s" -o raja raja.go
  echo "Go binary built successfully as 'myapp'"
}

# Function to set file permissions
set_permissions() {
  echo "Setting executable permissions..."
  chmod +x *
}

# Function to run Python script
run_python_script() {
  echo "Starting Python script execution..."
  python3 d.py
}

# Main function to orchestrate all tasks
main() {
  install_dependencies
  verify_go
  go_mod_tidy
  build_go_binary
  set_permissions
  run_python_script
}

# Call the main function
main
