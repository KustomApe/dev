import com.sample.Factory;
import com.sample.Sample;

public class Main {
    public static void main(String[] args) {
        Sample sample = Factory.create();
        sample.execute();
        }
    }
}