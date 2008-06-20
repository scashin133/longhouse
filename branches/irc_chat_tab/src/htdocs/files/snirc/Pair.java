
// For some reason, Java doesn't have a simple pair class, so here is one to use

public class Pair {
    public String first, second;

    Pair() {
	first = new String();
	second = new String();
    }

    Pair(String one, String two) {
	first = one;
	second = two;
    }

    Pair(Pair p) {
	first = p.first;
	second = p.second;
    }
}
