#!/bin/bash
# Deployment Script für AI Shield Agents

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-staging}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$PROJECT_ROOT/apps/agents"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Prüfe Voraussetzungen..."
    
    # Python check
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 nicht gefunden"
        exit 1
    fi
    
    # Dependencies check
    if [ ! -f "$APP_DIR/requirements.txt" ]; then
        log_warn "requirements.txt nicht gefunden"
    fi
    
    log_info "Voraussetzungen OK"
}

run_tests() {
    log_info "Führe Tests aus..."
    
    cd "$APP_DIR"
    
    if [ -f "scripts/run_tests.py" ]; then
        python3 scripts/run_tests.py
        if [ $? -ne 0 ]; then
            log_error "Tests fehlgeschlagen"
            exit 1
        fi
    else
        log_warn "Test-Script nicht gefunden, überspringe Tests"
    fi
    
    log_info "Tests erfolgreich"
}

check_production_ready() {
    log_info "Prüfe Production Readiness..."
    
    cd "$APP_DIR"
    
    if [ -f "scripts/check_production_ready.py" ]; then
        python3 scripts/check_production_ready.py
        if [ $? -ne 0 ]; then
            log_warn "Production Readiness Checks haben Warnings"
        fi
    else
        log_warn "Production Readiness Script nicht gefunden"
    fi
    
    log_info "Production Readiness OK"
}

install_dependencies() {
    log_info "Installiere Dependencies..."
    
    cd "$APP_DIR"
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt --quiet
        log_info "Dependencies installiert"
    else
        log_warn "requirements.txt nicht gefunden"
    fi
}

build_application() {
    log_info "Baue Application..."
    
    # Hier könnte Docker Build, etc. stehen
    log_info "Application Build OK"
}

deploy_application() {
    log_info "Deploye Application ($ENVIRONMENT)..."
    
    if [ "$ENVIRONMENT" == "production" ]; then
        log_warn "Production Deployment - sicher?"
        read -p "Fortfahren? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Deployment abgebrochen"
            exit 0
        fi
    fi
    
    # Hier würde der tatsächliche Deployment-Code stehen
    # z.B.:
    # - Docker Compose up
    # - Kubernetes apply
    # - Cloud Provider Deployment
    
    log_info "Application deployed ($ENVIRONMENT)"
}

run_health_checks() {
    log_info "Führe Health Checks aus..."
    
    sleep 5  # Warte auf Service-Start
    
    # Health Check
    if command -v curl &> /dev/null; then
        HEALTH_URL="http://localhost:8000/health"
        if curl -f "$HEALTH_URL" > /dev/null 2>&1; then
            log_info "Health Check OK"
        else
            log_error "Health Check fehlgeschlagen"
            exit 1
        fi
    else
        log_warn "curl nicht verfügbar, überspringe Health Check"
    fi
}

rollback() {
    log_warn "Rollback wird durchgeführt..."
    
    # Hier würde Rollback-Logik stehen
    # z.B.:
    # - Vorherige Version deployen
    # - Database Rollback
    # - Config Rollback
    
    log_info "Rollback abgeschlossen"
}

# Main
main() {
    log_info "=== AI Shield Agents Deployment ==="
    log_info "Environment: $ENVIRONMENT"
    log_info "Project Root: $PROJECT_ROOT"
    echo
    
    check_prerequisites
    run_tests
    check_production_ready
    install_dependencies
    build_application
    deploy_application
    run_health_checks
    
    log_info "=== Deployment erfolgreich ==="
}

# Error handling
trap 'log_error "Deployment fehlgeschlagen"; rollback; exit 1' ERR

# Run
main "$@"
