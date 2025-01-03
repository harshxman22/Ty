require 'fileutils'

def update_system_and_install_dependencies
  puts "Updating system and installing dependencies..."
  system("sudo apt-get update")
  system("sudo apt-get install -y golang-go python3 python3-pip")
  system("python3 -m pip install --upgrade pip")
  system("pip3 install telebot flask pymongo aiohttp python-telegram-bot aiogram pyTelegramBotAPI psutil motor")
  puts "Dependencies installed successfully."
end

def build_go_binary
  puts "Verifying Go installation..."
  if system("go version")
    puts "Tidying Go modules..."
    system("go mod tidy")

    puts "Building Go binary..."
    if system("go build -ldflags='-w -s' -o raja raja.go")
      puts "Binary built successfully as 'raja'."
    else
      puts "Failed to build Go binary."
      exit(1)
    end
  else
    puts "Go is not installed or not configured correctly."
    exit(1)
  end
end

def run_python_script
  script_name = "d.py"
  puts "Giving execution permissions to Python script..."
  FileUtils.chmod("+x", script_name)

  puts "Running Python script..."
  if system("python3 #{script_name}")
    puts "Python script executed successfully."
  else
    puts "Failed to execute Python script."
    exit(1)
  end
end

# Execute steps in sequence
update_system_and_install_dependencies
build_go_binary
run_python_script
