//+------------------------------------------------------------------+
//|                ZigZag_Triad_MTF_History_Days_Length.mq5          |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024"
#property indicator_chart_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_type1   DRAW_ZIGZAG
#property indicator_color1  clrYellow
#property indicator_width1  2

//--- 入力パラメータ
input ENUM_TIMEFRAMES InpTimeframe = PERIOD_CURRENT; 
input int    InpDepth      = 12;
input int    InpDeviation  = 5;
input int    InpBackstep   = 3;
input int    InpHistory    = 3;           // 保持するラインの数（各）
input color  InpResColor   = clrTomato;
input color  InpSupColor   = clrDeepSkyBlue;
input int    InpLineStyle  = STYLE_SOLID;
input int    InpFontSize   = 8;

//--- グローバル変数
int      handleZZ;
double   BufferZZ[];

//+------------------------------------------------------------------+
//| 初期化                                                            |
//+------------------------------------------------------------------+
int OnInit()
{
   SetIndexBuffer(0, BufferZZ, INDICATOR_DATA);
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, 0.0);
   
   handleZZ = iCustom(_Symbol, InpTimeframe, "Examples\\ZigZag", InpDepth, InpDeviation, InpBackstep);
   return(handleZZ == INVALID_HANDLE ? INIT_FAILED : INIT_SUCCEEDED);
}

void OnDeinit(const int reason) { ObjectsDeleteAll(0, "ZZH_"); }

//+------------------------------------------------------------------+
//| メイン計算                                                        |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
   double tempZZ[];
   datetime tempTime[];
   ArraySetAsSeries(tempZZ, true);
   ArraySetAsSeries(tempTime, true);
   
   int copyCount = 500; // 日数を遡るため少し多めに取得
   if(CopyBuffer(handleZZ, 0, 0, copyCount, tempZZ) <= 0) return(0);
   if(CopyTime(_Symbol, InpTimeframe, 0, copyCount, tempTime) <= 0) return(0);

   ArrayInitialize(BufferZZ, 0.0);
   ObjectsDeleteAll(0, "ZZH_"); // 描画をフレッシュに保つ

   int resFound = 0;
   int supFound = 0;

   for(int i = 1; i < copyCount - 1; i++)
   {
      if(tempZZ[i] > 0)
      {
         bool isHigh = false;
         for(int j=i+1; j<copyCount; j++) {
            if(tempZZ[j] > 0) {
               if(tempZZ[i] > tempZZ[j]) isHigh = true;
               break;
            }
         }

         string type = isHigh ? "Res" : "Sup";
         int currentIdx = isHigh ? resFound : supFound;
         color lineCol = isHigh ? InpResColor : InpSupColor;

         if(currentIdx < InpHistory)
         {
            DrawHistoryTrendLine("ZZH_"+type+"_"+(string)currentIdx, tempTime[i], tempZZ[i], lineCol);
            if(isHigh) resFound++; else supFound++;
         }
      }
      if(resFound >= InpHistory && supFound >= InpHistory) break;
   }

   // ZigZag描画用
   for(int i = 0; i < 100 && i < rates_total; i++) {
      if(tempZZ[i] > 0) BufferZZ[rates_total - 1 - i] = tempZZ[i];
   }

   return(rates_total);
}

//+------------------------------------------------------------------+
//| トレンドラインと経過日数ラベルを描画する関数                                |
//+------------------------------------------------------------------+
void DrawHistoryTrendLine(string name, datetime startTime, double price, color col)
{
   datetime now = TimeCurrent();
   
   // 1. トレンドラインの描画（発生時間から現在まで）
   if(ObjectCreate(0, name, OBJ_TREND, 0, startTime, price, now, price))
   {
      ObjectSetInteger(0, name, OBJPROP_COLOR, col);
      ObjectSetInteger(0, name, OBJPROP_STYLE, InpLineStyle);
      ObjectSetInteger(0, name, OBJPROP_RAY_RIGHT, false); // 突き抜けないように設定
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   }

   // 2. 経過日数の計算
   long diffSeconds = now - startTime;
   int days = (int)(diffSeconds / 86400); // 1日は86400秒
   
   string dayText = (days == 0) ? "Today" : (string)days + " days ago";
   
   // 3. ラベルの描画
   string labelName = name + "_Label";
   if(ObjectCreate(0, labelName, OBJ_TEXT, 0, now, price))
   {
      ObjectSetString(0, labelName, OBJPROP_TEXT, "  " + dayText);
      ObjectSetInteger(0, labelName, OBJPROP_COLOR, col);
      ObjectSetInteger(0, labelName, OBJPROP_FONTSIZE, InpFontSize);
      ObjectSetInteger(0, labelName, OBJPROP_ANCHOR, ANCHOR_LEFT);
      ObjectSetInteger(0, labelName, OBJPROP_SELECTABLE, false);
   }
}
