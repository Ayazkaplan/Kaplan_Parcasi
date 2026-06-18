# Flask Hesap Makinesi Web Uygulaması

Kullanıcının isteğine göre modern, responsive ve ihtiyaçlara cevap verebilen bir Flask hesap makinesi uygulaması geliştiriyorum. Uygulama Flask framework'ü kullanılarak oluşturulacak ve aşağıdaki özelliklere sahip olacak:

## Uygulama Özellikleri:
- Modern, responsive arayüz (Bootstrap 5 kullanılarak)
- Temel hesap makinesi işlemleri (toplama, çıkarma, çarpma, bölme)
- Üstel işlemler ve kök alma
- Geçmiş işlemleri kaydetme ve gösterme
- Kullanıcı dostu hata mesajları
- Gelişmiş hesaplama modülleri (yüzde, faktöriyel)
- Karanlık/ışık modu geçişi
- Tuş ses efektleri
- Klavye desteği

```python
"""
hesap_makinesi.py
Modern Flask tabanlı hesap makinesi uygulaması
"""

from flask import Flask, render_template_string, request, jsonify
import math
import json
from datetime import datetime

app = Flask(__name__)

# Hesaplama geçmişini saklamak için geçici bellek
calculation_history = []

# HTML ve CSS şablonu
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern Hesap Makinesi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #6c5ce7;
            --secondary-color: #a29bfe;
            --bg-color: #f8f9fa;
            --text-color: #333;
            --card-bg: #ffffff;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            --border-radius: 12px;
        }

        .dark-mode {
            --primary-color: #8b5cf6;
            --secondary-color: #a78bfa;
            --bg-color: #121212;
            --text-color: #f8f9fa;
            --card-bg: #1e1e1e;
            --shadow: 0 4px 6px rgba(0, 0, 0, 0.5);
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            transition: background-color 0.3s, color 0.3s;
        }

        .calculator-container {
            max-width: 400px;
            margin: 2rem auto;
            padding: 2rem;
            background-color: var(--card-bg);
            border-radius: var(--border-radius);
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
        }

        .display {
            background-color: var(--primary-color);
            color: white;
            padding: 1.5rem;
            border-radius: var(--border-radius);
            margin-bottom: 1.5rem;
            text-align: right;
            font-size: 2rem;
            height: 60px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }

        .history-item {
            background-color: rgba(108, 92, 231, 0.1);
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            transition: all 0.2s;
        }

        .history-item:hover {
            background-color: rgba(108, 92, 231, 0.2);
            transform: translateX(5px);
        }

        .btn {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }

        .btn-secondary {
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }

        .btn-dark {
            background-color: #343a40;
            border-color: #343a40;
        }

        .btn-outline-secondary {
            color: var(--text-color);
            border-color: var(--secondary-color);
        }

        .btn-outline-secondary:hover {
            background-color: var(--secondary-color);
            color: white;
        }

        .btn-group {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .theme-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background-color: var(--card-bg);
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: var(--shadow);
        }

        .history-panel {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 1.5rem;
        }

        .history-panel::-webkit-scrollbar {
            width: 6px;
        }

        .history-panel::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        .history-panel::-webkit-scrollbar-thumb {
            background: var(--secondary-color);
            border-radius: 10px;
        }

        @media (max-width: 576px) {
            .calculator-container {
                margin: 1rem;
                padding: 1.5rem;
            }

            .display {
                height: 50px;
                font-size: 1.5rem;
            }

            .btn {
                height: 50px;
            }
        }
    </style>
</head>
<body>
    <button class="theme-toggle" id="themeToggle">
        <i class="fas fa-moon" id="themeIcon"></i>
    </button>

    <div class="container">
        <div class="calculator-container">
            <div class="display" id="display">0</div>

            <div class="btn-group">
                <button class="btn btn-secondary" onclick="clearAll()">AC</button>
                <button class="btn btn-secondary" onclick="backspace()">⌫</button>
                <button class="btn btn-secondary" onclick="appendOperator('%')">%</button>
                <button class="btn btn-primary" onclick="appendOperator('/')">÷</button>
            </div>

            <div class="btn-group">
                <button class="btn btn-outline-secondary" onclick="appendNumber('7')">7</button>
                <button class="btn btn-outline-secondary" onclick="appendNumber('8')">8</button>
                <button class="btn btn-outline-secondary" onclick="appendNumber('9')">9</button>
                <button class="btn btn-primary" onclick="appendOperator('*')">×</button>
            </div>

            <div class="btn-group">
                <button class="btn btn-outline-secondary" onclick="appendNumber('4')">4</button>
                <button class="btn btn-outline-secondary" onclick="appendNumber('5')">5</button>
                <button class="btn btn-outline-secondary" onclick="appendNumber('6')">6</button>
                <button class="btn btn-primary" onclick="appendOperator('-')">-</button>
            </div>

            <div class="btn-group">
                <button class="btn btn-outline-secondary" onclick="appendNumber('1')">1</button>
                <button class="btn btn-outline-secondary" onclick="appendNumber('2')">2</button>
                <button class="btn btn-outline-secondary" onclick="appendNumber('3')">3</button>
                <button class="btn btn-primary" onclick="appendOperator('+')">+</button>
            </div>

            <div class="btn-group">
                <button class="btn