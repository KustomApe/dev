package com.sample;

// 公開する内容
public class Factory {
    public static Sample create() {
        // SampleImplのインスタンスを生成して、参照をSample型で返してる
        return new Sample() {
            @Override
            public static void execute() {
                System.out.println("test");
            }
        }
    }
}
    //インナークラスをやめましょう
//    private static class InnerSample implements Sample {
//        @Override
//        public void execute() {
//            System.out.println("Inner Class");
//        }
//    }
//}
