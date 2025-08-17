package com.sample;

//パッケージにいれることで外部からアクセスできなくなる=非公開のクラス(隠蔽する実装情報)
class SampleImpl implements Sample {
    @Override
    public void execute() {
        System.out.println("Hello");
    }
}
