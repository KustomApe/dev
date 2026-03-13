//+------------------------------------------------------------------+
//|                                     Dow_Theory_Catch_Wave.mq5    |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026"
#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   1

#property indicator_type1   DRAW_ZIGZAG
#property indicator_color1  clrYellow
#property indicator_width1  2

//--- 入力パラメータ
input int    InpDepth      = 12;      // ZigZag Depth
input int    InpDeviation  = 5;       // ZigZag Deviation
input int    InpBackstep   = 3;       // ZigZag Backstep
input color  InpUpColor    = clrLime;   // 上昇トレンド（押し安値）の色
input color  InpDnColor    = clrRed;    // 下降トレンド（戻り高値）の色

//--- 変数
int      handleZZ;
double   BufferZZ[];
double   BufferTrend[]; // 1:Up, -1:Down

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
   SetIndexBuffer(0, BufferZZ, INDICATOR_DATA);
   SetIndexBuffer(1, BufferTrend, INDICATOR_CALCULATIONS);
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, 0.0);
   
   handleZZ = iCustom(_Symbol, _Period, "Examples\\ZigZag", InpDepth, InpDeviation, InpBackstep);
   return(handleZZ == INVALID_HANDLE ? INIT_FAILED : INIT_SUCCEEDED);
}

void OnDeinit(const int reason) { ObjectsDeleteAll(0, "CTW_"); }

//+------------------------------------------------------------------+
//| OnCalculate                                                      |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total, const int prev_calculated, const datetime &time[],
                const double &high[], const double &low[], const double &close[])
{
   double tempZZ[];
   ArraySetAsSeries(tempZZ, true);
   ArraySetAsSeries(time, true);
   
   if(CopyBuffer(handleZZ, 0, 0, rates_total, tempZZ) <= 0) return(0);

   ArrayInitialize(BufferZZ, 0.0);
   ObjectsDeleteAll(0, "CTW_");

   double lastH = 0, prevH = 0;
   double lastL = 0, prevL = 0;
   int trend = 0; // 1:上昇, -1:下降

   // 過去から現在へ向かってダウ理論をスキャン（簡易化のため直近10個の頂点を処理）
   int found = 0;
   for(int i = rates_total - 1; i >= 0; i--)
   {
      if(tempZZ[i] > 0)
      {
         BufferZZ[rates_total - 1 - i] = tempZZ[i];
         
         // 山と谷の判定ロジック
         bool isHigh = (i < rates_total-1 && i > 0) ? (tempZZ[i] > high[i+1] || tempZZ[i] > low[i+1]) : true;
         
         if(isHigh) {
            prevH = lastH;
            lastH = tempZZ[i];
         } else {
            prevL = lastL;
            lastL = tempZZ[i];
         }

         // --- ダウ理論の判定 ---
         // 上昇トレンド：高値更新＋安値切り上げ
         if(lastH > prevH && lastL > prevL && prevH > 0 && prevL > 0) trend = 1;
         // 下降トレンド：安値更新＋高値切り下げ
         else if(lastH < prevH && lastL < prevL && prevH > 0 && prevL > 0) trend = -1;

         // 意識される水平線の描画（直近の押し安値・戻り高値）
         string label = isHigh ? "LastHigh" : "LastLow";
         color col = (trend == 1) ? InpUpColor : (trend == -1 ? InpDnColor : clrGray);
         
         if(found < 4) { // 直近数個のみ表示
            DrawDowLine("CTW_"+(string)i, time[i], tempZZ[i], col, label);
            found++;
         }
      }
   }

   return(rates_total);
}

//+------------------------------------------------------------------+
//| ダウ理論に基づいたラインとラベルの描画                                  |
//+------------------------------------------------------------------+
void DrawDowLine(string name, datetime startTime, double price, color col, string text)
{
   datetime now = TimeCurrent();
   if(ObjectCreate(0, name, OBJ_TREND, 0, startTime, price, now, price))
   {
      ObjectSetInteger(0, name, OBJPROP_COLOR, col);
      ObjectSetInteger(0, name, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(0, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 2);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   }
   
   // 経過日数の表示を右端に
   long diffSeconds = now - startTime;
   int days = (int)(diffSeconds / 86400);
   string dayStr = (days == 0) ? "Today" : (string)days + "d ago";

   string labelName = name + "_L";
   if(ObjectCreate(0, labelName, OBJ_TEXT, 0, now, price))
   {
      ObjectSetString(0, labelName, OBJPROP_TEXT, "  " + text + " (" + dayStr + ")");
      ObjectSetInteger(0, labelName, OBJPROP_COLOR, col);
      ObjectSetInteger(0, labelName, OBJPROP_ANCHOR, ANCHOR_LEFT);
   }
}
