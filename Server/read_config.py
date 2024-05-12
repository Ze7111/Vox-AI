import toml

# Load the configuration from the TOML file
config_path = 'config.toml'
config = toml.load(config_path)

# Extract the server configuration
server_config = config.get('server', {})
ip = server_config.get('ip', '127.0.0.1')
port = server_config.get('port', 6379)
password = server_config.get('password', '')

# Display the loaded configuration
print(f"IP Address: {ip}")
print(f"Port: {port}")
print(f"Password: {password}")
