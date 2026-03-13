//+------------------------------------------------------------------+
//|                                  Dow_Triad_Ultra_MTF_Full.mq5    |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026"
#property indicator_chart_window
#property indicator_buffers 1
#property indicator_plots   1
#property indicator_type1   DRAW_ZIGZAG
#property indicator_color1  clrGold
#property indicator_width1  2

//--- 入力パラメータ
input ENUM_TIMEFRAMES InpTimeframe = PERIOD_H4;      // 分析する上位足（MTF）
input int    InpDepth      = 12;
input int    InpDeviation  = 5;
input int    InpBackstep   = 3;
input bool   InpShowFibo   = true;                   // フィボナッチを表示
input bool   InpAlertBreak = true;                   // ブレイクアウトアラート
input color  InpFiboColor  = clrLightSteelBlue;

//--- グローバル変数
int      handleZZ;
double   BufferZZ[];
datetime lastAlertTime = 0;
double   lastKnownHigh = 0;
double   lastKnownLow  = 0;

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
   SetIndexBuffer(0, BufferZZ, INDICATOR_DATA);
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, 0.0);
   
   // 指定した上位足のZigZagハンドルを取得
   handleZZ = iCustom(_Symbol, InpTimeframe, "Examples\\ZigZag", InpDepth, InpDeviation, InpBackstep);
   return(handleZZ == INVALID_HANDLE ? INIT_FAILED : INIT_SUCCEEDED);
}

void OnDeinit(const int reason) { ObjectsDeleteAll(0, "DTU_"); }

//+------------------------------------------------------------------+
//| OnCalculate                                                      |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total, const int prev_calculated, const datetime &time[],
                const double &high[], const double &low[], const double &close[])
{
   // 上位足データのコピー
   double tempZZ[];
   datetime tempTime[];
   ArraySetAsSeries(tempZZ, true);
   ArraySetAsSeries(tempTime, true);
   ArraySetAsSeries(close, true);
   
   int copyCount = 500;
   if(CopyBuffer(handleZZ, 0, 0, copyCount, tempZZ) <= 0) return(0);
   if(CopyTime(_Symbol, InpTimeframe, 0, copyCount, tempTime) <= 0) return(0);

   ArrayInitialize(BufferZZ, 0.0);
   ObjectsDeleteAll(0, "DTU_Fibo"); // Fiboは毎秒更新

   int foundCount = 0;
   double p1=0, p2=0;
   datetime t1=0, t2=0;

   // 1. MTF描画 & 頂点特定
   for(int i = 0; i < copyCount && foundCount < 2; i++)
   {
      if(tempZZ[i] > 0)
      {
         // 現在のチャート（下位足）の該当する時間にプロット
         int localIdx = iBarShift(_Symbol, _Period, tempTime[i]);
         if(localIdx >= 0 && localIdx < rates_total)
            BufferZZ[rates_total - 1 - localIdx] = tempZZ[i];

         // フィボナッチ用の頂点確保
         if(foundCount == 0) { p1 = tempZZ[i]; t1 = tempTime[i]; }
         if(foundCount == 1) { p2 = tempZZ[i]; t2 = tempTime[i]; }
         foundCount++;
      }
   }

   // 2. 自動フィボナッチ
   if(InpShowFibo && foundCount >= 2)
   {
      DrawAutoFibo("DTU_Fibo", t2, p2, t1, p1);
   }

   // 3. ブレイクアウトアラート (現在足の終値が直近頂点を抜けたか)
   if(InpAlertBreak && foundCount >= 2 && time[0] != lastAlertTime)
   {
      double currentPrice = close[0];
      // p1が最新の頂点
      if(lastKnownHigh > 0 && currentPrice > lastKnownHigh) {
         Alert(StringFormat("MTF Breakout UP! %s Price: %f", EnumToString(InpTimeframe), currentPrice));
         lastAlertTime = time[0];
      }
      if(lastKnownLow > 0 && currentPrice < lastKnownLow) {
         Alert(StringFormat("MTF Breakout DOWN! %s Price: %f", EnumToString(InpTimeframe), currentPrice));
         lastAlertTime = time[0];
      }
      // 次回判定用に更新
      lastKnownHigh = (p1 > p2) ? p1 : p2;
      lastKnownLow  = (p1 < p2) ? p1 : p2;
   }

   return(rates_total);
}

//+------------------------------------------------------------------+
//| フィボナッチ描画関数                                               |
//+------------------------------------------------------------------+
void DrawAutoFibo(string name, datetime t1, double v1, datetime t2, double v2)
{
   if(ObjectCreate(0, name, OBJ_FIBO, 0, t1, v1, t2, v2))
   {
      ObjectSetInteger(0, name, OBJPROP_COLOR, InpFiboColor);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, name, OBJPROP_RAY_RIGHT, true);
      ObjectSetInteger(0, name, OBJPROP_BACK, true);
   }
   else {
      ObjectMove(0, name, 0, t1, v1);
      ObjectMove(0, name, 1, t2, v2);
   }
}
