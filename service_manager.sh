#!/bin/bash
# Evil Assistant - Service Manager
# Convenient commands for managing the Evil Assistant service

SERVICE_NAME="evil-assistant"

show_help() {
    echo "🍓 Evil Assistant Service Manager"
    echo "================================"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the Evil Assistant service"
    echo "  stop      - Stop the Evil Assistant service"
    echo "  restart   - Restart the Evil Assistant service"
    echo "  status    - Show service status"
    echo "  logs      - Show real-time logs (Ctrl+C to exit)"
    echo "  enable    - Enable auto-start on boot"
    echo "  disable   - Disable auto-start on boot"
    echo "  install   - Install the systemd service"
    echo "  uninstall - Remove the systemd service"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start the service"
    echo "  $0 logs      # Watch logs in real-time"
    echo "  $0 status    # Check if it's running"
}

check_service_exists() {
    if ! systemctl list-unit-files | grep -q "^${SERVICE_NAME}.service"; then
        echo "❌ Service not installed. Run: $0 install"
        exit 1
    fi
}

case "$1" in
    start)
        check_service_exists
        echo "🚀 Starting Evil Assistant..."
        sudo systemctl start $SERVICE_NAME
        echo "✅ Service started"
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    stop)
        check_service_exists
        echo "🛑 Stopping Evil Assistant..."
        sudo systemctl stop $SERVICE_NAME
        echo "✅ Service stopped"
        ;;
    restart)
        check_service_exists
        echo "🔄 Restarting Evil Assistant..."
        sudo systemctl restart $SERVICE_NAME
        echo "✅ Service restarted"
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    status)
        check_service_exists
        echo "📊 Evil Assistant Status:"
        sudo systemctl status $SERVICE_NAME --no-pager
        ;;
    logs)
        check_service_exists
        echo "📋 Evil Assistant Logs (Ctrl+C to exit):"
        echo "========================================"
        sudo journalctl -u $SERVICE_NAME -f
        ;;
    enable)
        check_service_exists
        echo "⚡ Enabling auto-start on boot..."
        sudo systemctl enable $SERVICE_NAME
        echo "✅ Auto-start enabled"
        ;;
    disable)
        check_service_exists
        echo "⏸️  Disabling auto-start on boot..."
        sudo systemctl disable $SERVICE_NAME
        echo "✅ Auto-start disabled"
        ;;
    install)
        echo "📦 Installing Evil Assistant service..."
        ./install_service.sh
        ;;
    uninstall)
        echo "🗑️  Uninstalling Evil Assistant service..."
        sudo systemctl stop $SERVICE_NAME 2>/dev/null || true
        sudo systemctl disable $SERVICE_NAME 2>/dev/null || true
        sudo rm -f /etc/systemd/system/${SERVICE_NAME}.service
        sudo systemctl daemon-reload
        echo "✅ Service uninstalled"
        ;;
    "")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
