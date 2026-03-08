#!/usr/bin/env bash
# Script para chequear linter, formatter y type checker
set -e

echo "🔍 Ejecutando ruff check (linter)..."
uv run ruff check .

echo ""
echo "✨ Ejecutando ruff format --check (formatter)..."
uv run ruff format --check .

echo ""
echo "🔎 Ejecutando mypy (type checker)..."
uv run mypy .

echo ""
echo "✅ Linter, formatter y type checker OK"
