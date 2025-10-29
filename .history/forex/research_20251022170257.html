<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FX 為替分析ツール (Alpha Vantage)</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        /* Interフォントの読み込み */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
        }
        /* スピナーのアニメーション */
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .spinner {
            border: 4px solid rgba(0, 0, 0, .1);
            border-left-color: #4f46e5; /* indigo-600 */
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
    </style>
</head>
<body class="bg-gray-100">

    <div class="container mx-auto max-w-5xl p-4 md:p-8 mt-10">
        <div class="bg-white rounded-2xl shadow-xl p-6 md:p-8">

            <!-- ヘッダー -->
            <h1 class="text-3xl font-bold text-gray-800 text-center mb-6">
                FX 為替分析ツール
            </h1>
            <p class="text-center text-gray-600 mb-8">
                Alpha Vantage APIを使用して為替レートを分析します。
            </p>

            <!-- 設定フォーム -->
            <form id="config-form" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 items-end mb-8">
                <!-- APIキー -->
                <div>
                    <label for="api-key" class="block text-sm font-medium text-gray-700 mb-2">Alpha Vantage APIキー</label>
                    <input type="password" id="api-key" name="api-key" class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="APIキーを入力">
                </div>

                <!-- 基準通貨 (From) -->
                <div>
                    <label for="from-currency" class="block text-sm font-medium text-gray-700 mb-2">基準通貨 (From)</label>
                    <select id="from-currency" name="from-currency" class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white">
                        <!-- オプションはJSで追加 -->
                    </select>
                </div>

                <!-- 比較通貨 (To) -->
                <div>
                    <label for="to-currency" class="block text-sm font-medium text-gray-700 mb-2">比較通貨 (To)</label>
                    <select id="to-currency" name="to-currency" class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white">
                        <!-- オプションはJSで追加 -->
                    </select>
                </div>

                <!-- 間隔 -->
                <div>
                    <label for="interval" class="block text-sm font-medium text-gray-700 mb-2">分析間隔</label>
                    <select id="interval" name="interval" class="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 bg-white">
                        <option value="FX_DAILY">日足 (Daily)</option>
                        <option value="FX_WEEKLY">週足 (Weekly)</option>
                        <option value="FX_MONTHLY">月足 (Monthly)</option>
                    </select>
                </div>

                <!-- 分析ボタン -->
                <div class="md:col-span-2 lg:col-span-4 mt-4">
                    <button type="submit" id="analyze-button" class="w-full bg-indigo-600 text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-200 flex items-center justify-center">
                        <span id="button-text">分析実行</span>
                        <div id="button-spinner" class="spinner w-5 h-5 border-2 border-white border-l-transparent ml-2 hidden"></div>
                    </button>
                </div>
            </form>

            <!-- メッセージエリア -->
            <div id="message-area" class="hidden p-4 rounded-lg mb-6 text-center"></div>

            <!-- チャートコンテナ -->
            <div class="bg-gray-50 p-4 rounded-lg shadow-inner" style="min-height: 400px;">
                <canvas id="fxChart"></canvas>
            </div>

            <!-- 最新情報サマリー -->
            <div id="summary-area" class="mt-6 text-center text-gray-700">
                <!-- JSで内容が挿入されます -->
            </div>

        </div>
    </div>

    <script>
        // --- DOM要素の取得 ---
        const configForm = document.getElementById('config-form');
        const apiKeyInput = document.getElementById('api-key');
        const fromCurrencySelect = document.getElementById('from-currency');
        const toCurrencySelect = document.getElementById('to-currency');
        const intervalSelect = document.getElementById('interval');
        const analyzeButton = document.getElementById('analyze-button');
        const buttonText = document.getElementById('button-text');
        const buttonSpinner = document.getElementById('button-spinner');
        const messageArea = document.getElementById('message-area');
        const summaryArea = document.getElementById('summary-area');
        const ctx = document.getElementById('fxChart').getContext('2d');
        
        let fxChartInstance = null; // チャートインスタンスを保持

        // --- 主要通貨リスト ---
        const currencies = [
            { code: "JPY", name: "日本円" },
            { code: "USD", name: "米ドル" },
            { code: "EUR", name: "ユーロ" },
            { code: "GBP", name: "英ポンド" },
            { code: "AUD", name: "豪ドル" },
            { code: "CAD", name: "カナダドル" },
            { code: "CHF", name: "スイスフラン" },
            { code: "NZD", name: "NZドル" },
            { code: "CNY", name: "中国人民元" },
        ];

        // --- 初期化処理 ---
        function initialize() {
            // 通貨選択オプションを生成
            currencies.forEach(currency => {
                const optionFrom = document.createElement('option');
                optionFrom.value = currency.code;
                optionFrom.textContent = `${currency.code} (${currency.name})`;
                
                const optionTo = optionFrom.cloneNode(true);

                fromCurrencySelect.appendChild(optionFrom);
                toCurrencySelect.appendChild(optionTo);
            });

            // デフォルト値の設定
            fromCurrencySelect.value = "USD";
            toCurrencySelect.value = "JPY";

            // フォーム送信イベントの監視
            configForm.addEventListener('submit', handleFormSubmit);
        }

        // --- フォーム送信ハンドラ ---
        async function handleFormSubmit(event) {
            event.preventDefault(); // デフォルトの送信をキャンセル
            
            const apiKey = apiKeyInput.value.trim();
            const fromSymbol = fromCurrencySelect.value;
            const toSymbol = toCurrencySelect.value;
            const interval = intervalSelect.value;

            if (!apiKey) {
                showMessage("APIキーを入力してください。", "error");
                return;
            }

            // ローディング状態に設定
            setLoading(true);
            showMessage("", "clear"); // 以前のエラーをクリア
            summaryArea.innerHTML = ""; // サマリーをクリア

            try {
                // API URLを構築
                const apiUrl = `https://www.alphavantage.co/query?function=${interval}&from_symbol=${fromSymbol}&to_symbol=${toSymbol}&apikey=${apiKey}`;

                // APIからデータを取得
                const response = await fetch(apiUrl);
                if (!response.ok) {
                    throw new Error(`HTTPエラー: ${response.status}`);
                }

                const data = await response.json();

                // Alpha Vantage APIからのエラーメッセージをチェック
                if (data["Error Message"]) {
                    throw new Error(`APIエラー: ${data["Error Message"]}`);
                }
                
                // "Note" (API制限など) をチェック
                if (data["Note"]) {
                    throw new Error(`API制限の可能性があります: ${data["Note"]}`);
                }

                // データを解析
                const parsedData = parseFxData(data, interval);
                if (!parsedData) {
                    throw new Error("受信したデータ形式が正しくありません。");
                }
                
                // チャートを描画
                renderChart(parsedData.labels, parsedData.data, `${fromSymbol} / ${toSymbol}`);
                
                // サマリーを表示
                showSummary(parsedData, fromSymbol, toSymbol);

            } catch (error) {
                console.error("データ取得エラー:", error);
                showMessage(error.message, "error");
            } finally {
                // ローディング状態を解除
                setLoading(false);
            }
        }

        // --- APIデータ解析 ---
        function parseFxData(data, interval) {
            // "Time Series FX (Daily)" のようなキー名を取得
            const timeSeriesKey = Object.keys(data).find(k => k.startsWith("Time Series FX"));
            
            if (!timeSeriesKey || !data[timeSeriesKey]) {
                return null;
            }

            const timeSeries = data[timeSeriesKey];
            const dates = Object.keys(timeSeries); // 日付キーを取得
            
            // APIは最新順で返すので、チャートのために逆順（古い順）にする
            dates.reverse(); 

            const labels = [];
            const chartData = [];

            dates.forEach(date => {
                labels.push(date);
                // 終値('4. close')を取得
                chartData.push(parseFloat(timeSeries[date]["4. close"])); 
            });

            return { labels, data: chartData };
        }

        // --- チャート描画 ---
        function renderChart(labels, data, label) {
            // 既存のチャートがあれば破棄
            if (fxChartInstance) {
                fxChartInstance.destroy();
            }

            fxChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: data,
                        borderColor: '#4f46e5', // indigo-600
                        backgroundColor: 'rgba(79, 70, 229, 0.1)',
                        borderWidth: 2,
                        pointRadius: 1, // 点を小さく
                        pointHoverRadius: 5,
                        fill: true,
                        tension: 0.1 // 少し滑らかに
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '日付'
                            },
                            ticks: {
                                // ラベルが多すぎるときの間引き
                                autoSkip: true,
                                maxTicksLimit: 15 
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '価格'
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return `${context.dataset.label}: ${context.raw.toFixed(4)}`; // 小数点以下4桁
                                }
                            }
                        },
                        legend: {
                            display: true,
                            position: 'top',
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            });
        }

        // --- サマリー表示 ---
        function showSummary(parsedData, from, to) {
            if (parsedData.data.length === 0) return;
            
            const latestPrice = parsedData.data[parsedData.data.length - 1];
            const latestDate = parsedData.labels[parsedData.labels.length - 1];
            
            summaryArea.innerHTML = `
                <p class="text-lg font-semibold text-gray-800">最新 (${latestDate})</p>
                <p class="text-2xl font-bold text-indigo-600">
                    1 ${from} = ${latestPrice.toFixed(4)} ${to}
                </p>
            `;
        }

        // --- ローディング状態管理 ---
        function setLoading(isLoading) {
            if (isLoading) {
                analyzeButton.disabled = true;
                buttonText.classList.add('hidden');
                buttonSpinner.classList.remove('hidden');
            } else {
                analyzeButton.disabled = false;
                buttonText.classList.remove('hidden');
                buttonSpinner.classList.add('hidden');
            }
        }

        // --- メッセージ表示 ---
        function showMessage(message, type = "info") {
            messageArea.classList.remove('hidden', 'bg-red-100', 'text-red-700', 'bg-blue-100', 'text-blue-700');
            
            if (type === "error") {
                messageArea.textContent = message;
                messageArea.classList.add('bg-red-100', 'text-red-700');
            } else if (type === "info") {
                messageArea.textContent = message;
                messageArea.classList.add('bg-blue-100', 'text-blue-700');
            } else if (type === "clear") {
                messageArea.textContent = "";
                messageArea.classList.add('hidden');
            }
        }

        // --- アプリケーションの実行 ---
        initialize();

    </script>
</body>
</html>
