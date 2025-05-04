# System Login Application

A secure, full-screen login application that blocks system access until successful authentication. Built with Python and Tkinter, this application provides a modern, user-friendly interface with robust security features.

## Features

- 🔒 Full-screen login interface
- 🛡️ System access blocking until authentication
- ⌨️ Keyboard and mouse input restriction
- 🔑 Secure password field with masking
- 🎨 Modern UI with dark theme
- ⚡ Optimized performance
- 🔄 Automatic startup capability

## Security Features

- Blocks Alt, Windows, and Tab keys
- Prevents Alt+Tab and Win+Tab window switching
- Disables Alt+F4 window closing
- Maintains window focus
- Keeps window always on top
- Restricts input to login form only

## Requirements

- Python 3.7 or higher
- Windows 10/11
- Administrator privileges

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Manual Start
1. Run the application with administrator privileges:
   ```bash
   python login_app.py
   ```
   Or use the provided batch file:
   ```bash
   run_app.bat
   ```

## Configuration

The application can be configured by modifying the following:

- UI colors in the `colors` dictionary
- Font settings and styling

## Troubleshooting

### Common Issues

1. **Application not starting**
   - Ensure Python is installed and in PATH
   - Run as administrator
   - Check for missing dependencies

2. **Input blocking issues**
   - Verify administrator privileges
   - Check if any security software is interfering
   - Ensure all dependencies are installed

3. **API connection errors**
   - Verify the API endpoint is correct
   - Check network connectivity
   - Ensure the API server is running

### Error Messages

- "Connection error": API server is unreachable
- "Invalid credentials": Username/password mismatch
- "Please enter both username and password": Missing credentials

## Security Notes

- The application requires administrator privileges to block system input
- Always use strong passwords
- Keep the application and dependencies updated
- Monitor for any security vulnerabilities

## Development

To modify or extend the application:

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make changes to `login_app.py`
3. Test thoroughly before deployment
4. Update version numbers and documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the development team.