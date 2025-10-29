package enshu;

public class Dept {
    private int deptNo;

    private String dname;

    private String loc;

    public int getDeptNo() {
        return deptNo;
    }

    public void setDeptNo(int deptNo) {
        if (deptNo > 0) {
            this.deptNo = deptNo;
        } else {
            System.out.println("無効な部署番号" + deptNo + "が入力されました。");
        }
    }

    public String dname() {
        return dname;
    }

    public static void main(String[], args) {
        return Null;
    }
}
